"""Placeholder test to verify pytest infrastructure works."""

import pytest


class TestPlaceholder:
    """Placeholder test class to verify setup."""

    @pytest.mark.unit
    def test_import_archguard(self):
        """Test that archguard can be imported."""
        try:
            import archguard  # noqa: F401
            assert True
        except ImportError:
            pytest.skip("Cannot import archguard yet (placeholder test)")

    @pytest.mark.unit
    def test_placeholder(self):
        """Placeholder test that always passes."""
        assert True
