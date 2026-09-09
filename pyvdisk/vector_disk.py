"""向量数据盘：在 PyVDisk 文件系统中持久化多个 HNSW 向量集合。"""
from __future__ import annotations
import hashlib, json, math, os, tempfile, threading
from typing import Any, Dict, Iterable, List, Optional
from .disk import VirtualDisk
from .identity import probe_disk, write_identity_to_block0
from .vfs import VFS

VECTOR_ROOT = "/.vectors"
VECTOR_MANIFEST = "/.vector_disk.json"
SUPPORTED_METRICS = ("cosine", "l2", "ip")

class VectorDiskError(Exception):
    """向量数据盘操作失败。"""

def _hnswlib():
    try:
        import hnswlib
    except ImportError as exc:
        raise ImportError("向量数据盘需要上游依赖 hnswlib；请运行 pip install hnswlib") from exc
    return hnswlib

def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

def _match_filter(metadata: Dict[str, Any], where: Optional[Dict[str, Any]]) -> bool:
    """支持等值、$eq/$ne/$gt/$gte/$lt/$lte/$in 以及顶层 $and/$or。"""
    if not where:
        return True
    for key, condition in where.items():
        if key == "$and":
            if not all(_match_filter(metadata, part) for part in condition): return False
            continue
        if key == "$or":
            if not any(_match_filter(metadata, part) for part in condition): return False
            continue
        actual = metadata.get(key)
        if not isinstance(condition, dict):
            if actual != condition: return False
            continue
        for op, expected in condition.items():
            try:
                if op == "$eq": ok = actual == expected
                elif op == "$ne": ok = actual != expected
                elif op == "$gt": ok = actual > expected
                elif op == "$gte": ok = actual >= expected
                elif op == "$lt": ok = actual < expected
                elif op == "$lte": ok = actual <= expected
                elif op == "$in": ok = actual in expected
                else: raise VectorDiskError(f"不支持的过滤操作符: {op}")
            except TypeError:
                ok = False
            if not ok: return False
    return True

class VectorDisk:
    """包含多个命名向量集合的特殊 .vdisk 磁盘。"""
    def __init__(self, path: str):
        self.path = path
        self.vfs = VFS(path)
        self._mounted = False
        self._lock = threading.RLock()

    @staticmethod
    def create(path: str, size_bytes: int, label: str = "") -> None:
        VFS.create(path, size_bytes, label=label)
        with VFS(path) as vfs:
            vfs.makedirs(VECTOR_ROOT)
            vfs.write_file(VECTOR_MANIFEST, _json_bytes({"type": "vector", "version": 1}))
        ident = probe_disk(path)
        disk = VirtualDisk(path); disk.open()
        try:
            write_identity_to_block0(disk, ident.disk_uuid, "", label,
                                     is_member=False, is_vector=True)
        finally:
            disk.close()

    def mount(self) -> "VectorDisk":
        if self._mounted: return self
        if probe_disk(self.path).kind != "vector":
            raise VectorDiskError(f"不是向量数据盘: {self.path}")
        self.vfs.mount()
        try:
            if not self.vfs.exists(VECTOR_MANIFEST): raise VectorDiskError("向量数据盘清单不存在")
            for dirname in self.vfs.listdir(VECTOR_ROOT):
                base = f"{VECTOR_ROOT}/{dirname}"
                if not self.vfs.exists(base + "/config.json"): continue
                cfg = self._read_json(base + "/config.json"); records = self._read_json(base + "/records.json")
                digest = hashlib.sha256(_json_bytes(records)).hexdigest()
                if cfg.get("records_checksum") and cfg["records_checksum"] != digest: raise VectorDiskError(f"向量记录校验失败: {cfg.get('name', dirname)}")
                changed = not cfg.get("records_checksum"); cfg["records_checksum"] = digest
                ok = self.vfs.exists(base + "/index.hnsw")
                if ok and cfg.get("index_checksum"): ok = hashlib.sha256(self.vfs.read_file(base + "/index.hnsw")).hexdigest() == cfg["index_checksum"]
                if not ok or cfg.get("index_generation", 0) != cfg.get("generation", 0):
                    self._rebuild_index(cfg["name"], cfg, records); cfg["index_generation"] = cfg.get("generation", 0); cfg["index_checksum"] = hashlib.sha256(self.vfs.read_file(base + "/index.hnsw")).hexdigest(); changed = True
                if changed: self._write_json(base + "/config.json", cfg)
        except Exception:
            self.vfs.close(); raise
        self._mounted = True
        return self

    def close(self) -> None:
        if self._mounted:
            self.vfs.close(); self._mounted = False
    def __enter__(self): return self.mount()
    def __exit__(self, *exc): self.close()
    def _require_mounted(self):
        if not self._mounted: raise VectorDiskError("向量数据盘未挂载")

    @staticmethod
    def _key(name: str) -> str:
        if not name or "/" in name or "\\" in name:
            raise VectorDiskError("集合名不能为空或包含路径分隔符")
        return hashlib.sha256(name.encode("utf-8")).hexdigest()[:24]
    def _dir(self, name: str) -> str: return f"{VECTOR_ROOT}/{self._key(name)}"
    def _read_json(self, path: str): return json.loads(self.vfs.read_file(path).decode("utf-8"))
    def _write_json(self, path: str, value: Dict[str, Any]): self.vfs.write_file(path, _json_bytes(value))

    def _config(self, name: str):
        self._require_mounted(); path = self._dir(name) + "/config.json"
        if not self.vfs.exists(path): raise VectorDiskError(f"集合不存在: {name}")
        config = self._read_json(path)
        if config.get("name") != name: raise VectorDiskError(f"集合配置损坏: {name}")
        config.setdefault("generation", 0)
        config.setdefault("index_generation", config["generation"])
        return config
    def _records(self, name: str): return self._read_json(self._dir(name) + "/records.json")

    def create_collection(self, name: str, dimension: int, metric: str = "cosine",
                          max_elements: int = 10000, m: int = 16,
                          ef_construction: int = 200, ef_search: int = 50) -> None:
        with self._lock:
            self._require_mounted()
            if dimension <= 0: raise VectorDiskError("向量维度必须为正数")
            if metric not in SUPPORTED_METRICS: raise VectorDiskError(f"距离度量必须是 {SUPPORTED_METRICS}")
            if max_elements <= 0: raise VectorDiskError("max_elements 必须为正数")
            base = self._dir(name)
            if self.vfs.exists(base): raise VectorDiskError(f"集合已存在: {name}")
            self.vfs.mkdir(base)
            config = {"name": name, "dimension": dimension, "metric": metric,
                      "max_elements": max_elements, "m": m,
                      "ef_construction": ef_construction, "ef_search": ef_search,
                      "generation": 0, "index_generation": 0}
            records = {"next_label": 0, "items": {}}
            self._write_json(base + "/records.json", records)
            self._rebuild_index(name, config, records)
            config["records_checksum"] = hashlib.sha256(_json_bytes(records)).hexdigest()
            config["index_checksum"] = hashlib.sha256(self.vfs.read_file(base + "/index.hnsw")).hexdigest()
            self._write_json(base + "/config.json", config)

    def list_collections(self) -> List[Dict[str, Any]]:
        with self._lock:
            self._require_mounted(); result = []
            for dirname in self.vfs.listdir(VECTOR_ROOT):
                path = f"{VECTOR_ROOT}/{dirname}/config.json"
                if self.vfs.exists(path):
                    cfg = self._read_json(path); cfg["count"] = len(self._records(cfg["name"])["items"]); result.append(cfg)
            return sorted(result, key=lambda item: item["name"])

    def drop_collection(self, name: str) -> None:
        with self._lock:
            self._config(name); self.vfs.rmtree(self._dir(name))

    @staticmethod
    def _validate_vector(vector: Iterable[float], dimension: int) -> List[float]:
        try:
            values = [float(x) for x in vector]
        except (TypeError, ValueError) as exc:
            raise VectorDiskError("向量必须只包含数字") from exc
        if len(values) != dimension: raise VectorDiskError(f"向量维度不匹配: 期望 {dimension}，实际 {len(values)}")
        if not all(math.isfinite(value) for value in values):
            raise VectorDiskError("向量必须只包含有限数值")
        return values

    def upsert(self, collection: str, item_id: str, vector: Iterable[float], metadata: Optional[Dict[str, Any]] = None) -> None:
        self.upsert_many(collection, [{"id": item_id, "vector": vector, "metadata": metadata or {}}])

    def upsert_many(self, collection: str, items: Iterable[Dict[str, Any]]) -> None:
        with self._lock:
            config = self._config(collection); records = self._records(collection)
            staged = {"next_label": records["next_label"], "items": dict(records["items"])}
            for item in items:
                item_id = str(item["id"])
                if not item_id: raise VectorDiskError("向量 ID 不能为空")
                old = staged["items"].get(item_id); label = old["label"] if old else staged["next_label"]
                if old is None: staged["next_label"] += 1
                staged["items"][item_id] = {"label": label,
                    "vector": self._validate_vector(item["vector"], config["dimension"]),
                    "metadata": item.get("metadata") or {}}
            if len(staged["items"]) > config["max_elements"]: raise VectorDiskError("集合已超过 max_elements 容量")
            config = dict(config); config["generation"] += 1
            base = self._dir(collection)
            self._write_json(base + "/records.json.tmp", staged); self.vfs.rename(base + "/records.json.tmp", base + "/records.json")
            self._rebuild_index(collection, config, staged)
            config["index_generation"] = config["generation"]
            config["records_checksum"] = hashlib.sha256(_json_bytes(staged)).hexdigest()
            config["index_checksum"] = hashlib.sha256(self.vfs.read_file(base + "/index.hnsw")).hexdigest()
            self._write_json(base + "/config.json.tmp", config); self.vfs.rename(base + "/config.json.tmp", base + "/config.json")

    def get(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            self._config(collection); record = self._records(collection)["items"].get(str(item_id))
            if record is None: return None
            return {"id": str(item_id), "vector": record["vector"], "metadata": record["metadata"]}

    def delete(self, collection: str, item_id: str) -> bool:
        with self._lock:
            config = self._config(collection); records = self._records(collection)
            if records["items"].pop(str(item_id), None) is None: return False
            config = dict(config); config["generation"] += 1
            base = self._dir(collection)
            self._write_json(base + "/records.json.tmp", records); self.vfs.rename(base + "/records.json.tmp", base + "/records.json")
            self._rebuild_index(collection, config, records)
            config["index_generation"] = config["generation"]
            config["records_checksum"] = hashlib.sha256(_json_bytes(records)).hexdigest()
            config["index_checksum"] = hashlib.sha256(self.vfs.read_file(base + "/index.hnsw")).hexdigest()
            self._write_json(base + "/config.json.tmp", config); self.vfs.rename(base + "/config.json.tmp", base + "/config.json"); return True

    def count(self, collection: str) -> int:
        with self._lock:
            self._config(collection); return len(self._records(collection)["items"])

    def _rebuild_index(self, name: str, config: Dict[str, Any], records: Dict[str, Any]) -> None:
        hnswlib = _hnswlib(); index = hnswlib.Index(space=config["metric"], dim=config["dimension"])
        index.init_index(max_elements=max(config["max_elements"], 1), ef_construction=config["ef_construction"], M=config["m"])
        index.set_ef(config["ef_search"]); values = list(records["items"].values())
        if values: index.add_items([v["vector"] for v in values], [v["label"] for v in values])
        fd, host_path = tempfile.mkstemp(suffix=".hnsw"); os.close(fd)
        try:
            index.save_index(host_path)
            with open(host_path, "rb") as stream:
                # Publish the rebuilt index as one VFS rename.
                target = self._dir(name) + "/index.hnsw"
                temporary = target + ".tmp"
                self.vfs.write_file(temporary, stream.read())
                self.vfs.rename(temporary, target)
        finally:
            try: os.unlink(host_path)
            except OSError: pass

    def _load_index(self, name: str, config: Dict[str, Any]):
        hnswlib = _hnswlib(); data = self.vfs.read_file(self._dir(name) + "/index.hnsw")
        fd, host_path = tempfile.mkstemp(suffix=".hnsw")
        try:
            with os.fdopen(fd, "wb") as stream: stream.write(data)
            index = hnswlib.Index(space=config["metric"], dim=config["dimension"])
            index.load_index(host_path, max_elements=max(config["max_elements"], 1)); index.set_ef(config["ef_search"]); return index
        finally:
            try: os.unlink(host_path)
            except OSError: pass

    def search(self, collection: str, vector: Iterable[float], k: int = 10,
               where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        with self._lock:
            config = self._config(collection); records = self._records(collection)
            if k <= 0 or not records["items"]: return []
            query = self._validate_vector(vector, config["dimension"])
            by_label = {v["label"]: (item_id, v) for item_id, v in records["items"].items()}
            allowed = {label for label, (_id, rec) in by_label.items() if _match_filter(rec["metadata"], where)}
            if not allowed: return []
            index = self._load_index(collection, config); wanted = min(k, len(allowed))
            labels, distances = index.knn_query([query], k=wanted, filter=lambda label: int(label) in allowed)
            result = []
            for label, distance in zip(labels[0], distances[0]):
                item_id, record = by_label[int(label)]
                result.append({"id": item_id, "distance": float(distance), "metadata": record["metadata"], "vector": record["vector"]})
            return result
