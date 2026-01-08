"""Tests for platform detector."""

from pathlib import Path

import pytest

from py_mcp_installer.exceptions import PlatformDetectionError
from py_mcp_installer.platform_detector import PlatformDetector, PlatformInfo
from py_mcp_installer.types import Platform


def test_detect_returns_platform_info_or_raises():
    """Test that detect returns PlatformInfo or raises PlatformDetectionError."""
    detector = PlatformDetector()
    try:
        result = detector.detect()
        assert isinstance(result, PlatformInfo)
        assert isinstance(result.platform, Platform)
    except PlatformDetectionError:
        # Expected in CI where no platforms are installed
        pass


def test_detect_has_confidence_when_platform_found():
    """Test that detection includes confidence score when platform is found."""
    detector = PlatformDetector()
    try:
        info = detector.detect()
        assert hasattr(info, "confidence")
        assert 0.0 <= info.confidence <= 1.0
    except PlatformDetectionError:
        # Expected in CI where no platforms are installed
        pass


def test_detect_for_specific_platform_when_not_available():
    """Test detection raises error when specific platform is not available."""
    detector = PlatformDetector()
    # In CI, CLAUDE_CODE likely isn't installed
    with pytest.raises(PlatformDetectionError):
        detector.detect_for_platform(Platform.CLAUDE_CODE)


def test_platform_info_structure():
    """Test PlatformInfo has expected attributes."""
    # Create a mock PlatformInfo to test structure
    info = PlatformInfo(
        platform=Platform.CLAUDE_CODE,
        confidence=0.9,
        config_path=Path("/test/path")
    )
    assert info.platform == Platform.CLAUDE_CODE
    assert info.confidence == 0.9
    assert info.config_path == Path("/test/path")


def test_detect_claude_code_method_exists():
    """Test that Claude Code detection method exists."""
    detector = PlatformDetector()
    assert hasattr(detector, "detect_claude_code")
    assert callable(detector.detect_claude_code)


def test_detect_cursor_method_exists():
    """Test that Cursor detection method exists."""
    detector = PlatformDetector()
    assert hasattr(detector, "detect_cursor")
    assert callable(detector.detect_cursor)


def test_individual_detection_returns_tuple():
    """Test that individual detection methods return (confidence, path) tuple."""
    detector = PlatformDetector()
    result = detector.detect_claude_code()
    assert isinstance(result, tuple)
    assert len(result) == 2
    confidence, path = result
    assert isinstance(confidence, float)
    assert path is None or isinstance(path, Path)
