"""Tests for platform detector."""

from py_mcp_installer.platform_detector import PlatformDetector, PlatformInfo
from py_mcp_installer.types import Platform


def test_detect_returns_platform_info():
    """Test that detect returns a valid PlatformInfo."""
    detector = PlatformDetector()
    result = detector.detect()
    assert isinstance(result, PlatformInfo)
    assert isinstance(result.platform, Platform)


def test_detect_has_confidence():
    """Test that detection includes confidence score."""
    detector = PlatformDetector()
    info = detector.detect()
    assert hasattr(info, "confidence")
    assert 0.0 <= info.confidence <= 1.0


def test_detect_for_specific_platform():
    """Test detection for a specific platform."""
    detector = PlatformDetector()
    info = detector.detect_for_platform(Platform.CLAUDE_CODE)
    assert isinstance(info, PlatformInfo)
    assert info.platform == Platform.CLAUDE_CODE
