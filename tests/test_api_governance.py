import warnings

from pyvdisk import DataDisk, FS, Unified, VirtualDisk, Volume


def test_default_public_imports_are_silent():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert Unified is DataDisk
        VirtualDisk("unused.vdisk")
        FS.__name__
        Volume()
    assert not [w for w in caught if issubclass(w.category, DeprecationWarning)]


def test_explicit_legacy_calls_warn_once():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        VirtualDisk("unused.vdisk", legacy=True)
        FS(object(), legacy=True)
        Volume(legacy=True)
        DataDisk("unused.vdisk", legacy=True)
    messages = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert len(messages) == 4
    assert all(w.filename.endswith("test_api_governance.py") for w in messages)
