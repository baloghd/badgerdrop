"""Unit tests for constants module."""

from pathlib import Path

import pytest

import badgerdrop.config.constants as constants


class TestWindowConstants:
    """Tests for window-related constants."""

    def test_default_width(self):
        """Test WINDOW_DEFAULT_WIDTH constant."""
        assert constants.WINDOW_DEFAULT_WIDTH == 800
        assert isinstance(constants.WINDOW_DEFAULT_WIDTH, int)

    def test_default_height(self):
        """Test WINDOW_DEFAULT_HEIGHT constant."""
        assert constants.WINDOW_DEFAULT_HEIGHT == 500
        assert isinstance(constants.WINDOW_DEFAULT_HEIGHT, int)


class TestBorderRadiusConstants:
    """Tests for border radius constants."""

    def test_border_radius_values(self):
        """Test BORDER_RADIUS constants."""
        assert constants.BORDER_RADIUS_LARGE == 24
        assert constants.BORDER_RADIUS_MEDIUM == 20
        assert constants.BORDER_RADIUS_SMALL == 16
        assert constants.BORDER_RADIUS_XSMALL == 12


class TestPaddingConstants:
    """Tests for padding constants."""

    def test_padding_values(self):
        """Test PADDING constants."""
        assert constants.PADDING_XLARGE == 48
        assert constants.PADDING_LARGE == 32
        assert constants.PADDING_MEDIUM == 24
        assert constants.PADDING_SMALL == 16


class TestFontConstants:
    """Tests for font-related constants."""

    def test_font_sizes(self):
        """Test font size constants."""
        assert constants.FONT_SIZE_TITLE == 24
        assert constants.FONT_SIZE_SUBTITLE == 14
        assert constants.FONT_SIZE_ARROW == 48
        assert constants.FONT_SIZE_TOAST == 16


class TestTransitionConstants:
    """Tests for transition/animation constants."""

    def test_transition_durations(self):
        """Test TRANSITION constants."""
        assert constants.TRANSITION_SLOW == 400
        assert constants.TRANSITION_MEDIUM == 350
        assert constants.TRANSITION_FAST == 300
        assert isinstance(constants.TRANSITION_SLOW, int)


class TestFileConstants:
    """Tests for file-related constants."""

    def test_permissions(self):
        """Test file permission constants."""
        assert constants.PERMISSION_EXECUTABLE == 0o755
        assert constants.PERMISSION_FILE == 0o644

    def test_copy_chunk_size(self):
        """Test COPY_CHUNK_SIZE constant."""
        assert constants.COPY_CHUNK_SIZE == 8192
        assert isinstance(constants.COPY_CHUNK_SIZE, int)

    def test_icon_size(self):
        """Test ICON_SIZE constants."""
        assert constants.ICON_SIZE_DEFAULT == 128
        assert isinstance(constants.ICON_SIZE_DEFAULT, int)

    def test_unsafe_filename_chars(self):
        """Test UNSAFE_FILENAME_CHARS constant."""
        assert isinstance(constants.UNSAFE_FILENAME_CHARS, str)
        assert '<' in constants.UNSAFE_FILENAME_CHARS


class TestPathConstants:
    """Tests for path-related constants."""

    def test_default_install_dir(self):
        """Test DEFAULT_INSTALL_DIR constant."""
        assert constants.DEFAULT_INSTALL_DIR == "~/Applications"

    def test_default_config_dir(self):
        """Test DEFAULT_CONFIG_DIR constant."""
        assert constants.DEFAULT_CONFIG_DIR == ".config/badgerdrop"


class TestTimeoutConstants:
    """Tests for timeout-related constants."""

    def test_process_terminate_timeout(self):
        """Test PROCESS_TERMINATE_TIMEOUT constant."""
        assert constants.PROCESS_TERMINATE_TIMEOUT == 5
        assert isinstance(constants.PROCESS_TERMINATE_TIMEOUT, int)


class TestDefaultSettings:
    """Tests for default settings constants."""

    def test_defaults(self):
        """Test default setting constants."""
        assert constants.DEFAULT_PLAY_SOUND is True
        assert constants.DEFAULT_SOUND_THEME == "default"
        assert constants.DEFAULT_AUTO_MAKE_EXECUTABLE is True
        assert constants.DEFAULT_SHOW_NOTIFICATIONS is True
