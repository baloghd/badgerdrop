"""Unit tests for validators module."""

from pathlib import Path

import pytest

from badgerdrop.utils.validators import DirectoryValidationError, validate_directory


class TestValidateDirectory:
    """Tests for validate_directory function."""

    def test_valid_directory(self, tmp_path: Path):
        """Test validation of a valid writable directory."""
        test_dir = tmp_path / "valid_dir"
        test_dir.mkdir()
        
        result = validate_directory(test_dir)
        
        assert result == test_dir
        assert isinstance(result, Path)

    def test_directory_does_not_exist_but_parent_writable(self, tmp_path: Path):
        """Test validation when directory doesn't exist but parent is writable (should succeed)."""
        nonexistent_dir = tmp_path / "nonexistent"
        
        # Should succeed because parent (tmp_path) is writable
        result = validate_directory(nonexistent_dir)
        
        assert result == nonexistent_dir
        assert isinstance(result, Path)

    def test_directory_does_not_exist_parent_not_writable(self, tmp_path: Path):
        """Test validation when directory doesn't exist and parent is not writable."""
        # Create a non-writable parent directory
        readonly_parent = tmp_path / "readonly_parent"
        readonly_parent.mkdir()
        readonly_parent.chmod(0o555)  # Remove write permissions
        
        try:
            nonexistent_dir = readonly_parent / "nonexistent"
            
            with pytest.raises(DirectoryValidationError) as exc_info:
                validate_directory(nonexistent_dir)
            
            assert "not writable" in str(exc_info.value)
        finally:
            # Restore permissions for cleanup
            readonly_parent.chmod(0o755)

    def test_path_is_file(self, tmp_path: Path):
        """Test validation when path is a file, not directory."""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("content")
        
        with pytest.raises(DirectoryValidationError) as exc_info:
            validate_directory(test_file)
        
        assert "not a directory" in str(exc_info.value)

    def test_directory_not_writable(self, tmp_path: Path):
        """Test validation when directory is not writable."""
        test_dir = tmp_path / "readonly_dir"
        test_dir.mkdir()
        test_dir.chmod(0o555)  # Remove write permissions
        
        try:
            with pytest.raises(DirectoryValidationError) as exc_info:
                validate_directory(test_dir)
            
            assert "not writable" in str(exc_info.value)
        finally:
            # Restore permissions for cleanup
            test_dir.chmod(0o755)

    def test_nested_directory(self, tmp_path: Path):
        """Test validation of nested directory."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"
        nested_dir.mkdir(parents=True)
        
        result = validate_directory(nested_dir)
        
        assert result == nested_dir

    def test_expands_tilde_to_home(self, tmp_path: Path, monkeypatch):
        """Test that tilde is expanded to home directory by resolve()."""
        # The validator uses resolve() which expands tildes
        tilde_path = "~/test_dir"
        
        # Should succeed because ~ expands to home directory, and home is writable
        result = validate_directory(tilde_path)
        
        assert isinstance(result, Path)
        # Result should be expanded to home directory
        assert str(result).startswith(str(Path.home()))

    def test_empty_directory_path(self):
        """Test validation with empty path."""
        # Empty path is not absolute
        with pytest.raises(DirectoryValidationError) as exc_info:
            validate_directory("")
        
        assert "absolute path" in str(exc_info.value)

    def test_relative_directory_path(self, tmp_path: Path):
        """Test validation with relative path."""
        # Create a directory with relative path
        rel_dir = tmp_path / "rel_test"
        rel_dir.mkdir()
        
        # Change to parent directory and use relative path
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(DirectoryValidationError) as exc_info:
                validate_directory("rel_test")
            
            assert "absolute path" in str(exc_info.value)
        finally:
            os.chdir(original_cwd)
