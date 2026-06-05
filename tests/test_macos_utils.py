import sys
from app.native import macos_utils


def test_platform_constants():
    # Ensure the module exposes IS_DARWIN and HAS_PYOBJC
    assert hasattr(macos_utils, 'IS_DARWIN')
    assert hasattr(macos_utils, 'HAS_PYOBJC')


def test_get_macos_version_fallback():
    # On non-darwin the function should return None
    if not macos_utils.IS_DARWIN:
        assert macos_utils.get_macos_version() is None
    else:
        v = macos_utils.get_macos_version()
        assert isinstance(v, str) or v is None
