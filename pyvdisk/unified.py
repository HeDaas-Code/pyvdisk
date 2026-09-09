"""Backward-compatible aliases for the canonical DataDisk API."""
from .infrastructure.disk import DataDisk, DataDiskError, MetadataTransaction
DataInfrastructure = Unified = Container = DataDisk
UnifiedError = DataDiskError
__all__ = ["DataDisk", "DataInfrastructure", "Unified", "Container", "DataDiskError", "UnifiedError", "MetadataTransaction"]
