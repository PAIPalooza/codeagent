import os
import pytest
import tempfile
import shutil
import stat
from pathlib import Path

# This allows the tests to find the app module
from app.utils.file_writer import make_dirs, write_file, read_file


class TestFileWriter:
    """Test suite for file_writer utility functions."""
    
    def setup_method(self):
        """Set up a temporary directory for file operations."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up the temporary directory after tests."""
        shutil.rmtree(self.temp_dir)
    
    def test_make_dirs(self):
        """Test that make_dirs creates directories correctly."""
        test_path = os.path.join(self.temp_dir, "nested/dirs/structure")
        
        # Test directory creation
        make_dirs(test_path)
        assert os.path.isdir(test_path), "Directory was not created"
        
        # Test idempotence (calling again should not raise error)
        make_dirs(test_path)
        assert os.path.isdir(test_path), "Directory should still exist after second call"
    
    def test_write_file(self):
        """Test that write_file writes content to a file correctly."""
        # Test writing to a file in an existing directory
        file_path = os.path.join(self.temp_dir, "test_file.txt")
        content = "Hello, world!"
        
        write_file(file_path, content)
        
        assert os.path.isfile(file_path), "File was not created"
        with open(file_path, "r", encoding="utf-8") as f:
            assert f.read() == content, "File content does not match expected content"
        
        # Test writing to a file in a non-existing nested directory
        nested_file_path = os.path.join(self.temp_dir, "nested/path/test_file.txt")
        nested_dir = os.path.dirname(nested_file_path)
        make_dirs(nested_dir)
        
        write_file(nested_file_path, content)
        
        assert os.path.isfile(nested_file_path), "Nested file was not created"
        with open(nested_file_path, "r", encoding="utf-8") as f:
            assert f.read() == content, "Nested file content does not match expected content"
    
    def test_write_file_overwrites_existing_file(self):
        """Test that write_file overwrites existing files."""
        file_path = os.path.join(self.temp_dir, "overwrite_test.txt")
        
        # Write initial content
        initial_content = "Initial content"
        write_file(file_path, initial_content)
        
        # Overwrite with new content
        new_content = "New content"
        write_file(file_path, new_content)
        
        # Verify content was overwritten
        with open(file_path, "r", encoding="utf-8") as f:
            assert f.read() == new_content, "File content was not overwritten"
    
    def test_read_file(self):
        """Test that read_file correctly reads file content."""
        file_path = os.path.join(self.temp_dir, "read_test.txt")
        content = "Content to be read"
        
        # Create test file
        write_file(file_path, content)
        
        # Test reading content
        read_content = read_file(file_path)
        assert read_content == content, "Read content does not match written content"
    
    def test_read_file_nonexistent(self):
        """Test that read_file raises FileNotFoundError for non-existent files."""
        non_existent_path = os.path.join(self.temp_dir, "non_existent.txt")
        
        with pytest.raises(FileNotFoundError):
            read_file(non_existent_path)
    
    def test_error_handling(self):
        """Test error handling for permission issues."""
        # Skip this test on Windows as permission handling differs
        if os.name == 'nt':
            pytest.skip("Skipping permission test on Windows")
        
        # Create a read-only directory
        readonly_dir = os.path.join(self.temp_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, stat.S_IRUSR | stat.S_IXUSR)  # Read and execute only
        
        try:
            # Attempt to write to a file in the read-only directory
            file_path = os.path.join(readonly_dir, "test.txt")
            
            with pytest.raises(PermissionError):
                write_file(file_path, "test content")
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, stat.S_IRWXU)
