"""
File and directory manipulation utilities.

This module provides utilities for working with files and directories,
including creating directories, reading/writing file content, and creating ZIP archives.
"""

import os
import errno
import zipfile
from typing import Union, AnyStr, Optional, List
from pathlib import Path


def make_dirs(path: Union[str, Path]) -> None:
    """
    Create directories recursively, similar to `mkdir -p`.
    
    Args:
        path: Directory path to create.
        
    Raises:
        PermissionError: If the user doesn't have permission to create the directory.
        OSError: For other OS-related errors during directory creation.
    """
    os.makedirs(path, exist_ok=True)


def write_file(path: Union[str, Path], content: str) -> None:
    """
    Write content to a file, creating parent directories if they don't exist.
    
    Args:
        path: File path to write to.
        content: Content to write to the file.
        
    Raises:
        PermissionError: If the user doesn't have permission to write to the file.
        OSError: For other OS-related errors during file writing.
    """
    # Create parent directories if they don't exist
    directory = os.path.dirname(path)
    if directory:
        make_dirs(directory)
        
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def read_file(path: Union[str, Path]) -> str:
    """
    Read content from a file.
    
    Args:
        path: File path to read from.
        
    Returns:
        The content of the file as a string.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        PermissionError: If the user doesn't have permission to read the file.
        OSError: For other OS-related errors during file reading.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def create_zip_archive(
    source_dir: Union[str, Path],
    zip_path: Union[str, Path],
    project_name: str,
    compression: int = zipfile.ZIP_DEFLATED
) -> str:
    """
    Create a ZIP archive from a directory.
    
    This function creates a ZIP archive from all files in the source directory,
    preserving the relative directory structure inside the archive. Files are 
    stored inside a top-level directory named after the project.
    
    Args:
        source_dir: Source directory to zip.
        zip_path: Target path for the ZIP file.
        project_name: Name of the project to use as the top-level directory in the archive.
        compression: ZIP compression method (default: zipfile.ZIP_DEFLATED).
        
    Returns:
        Path to the created ZIP file.
        
    Raises:
        FileNotFoundError: If the source directory doesn't exist.
        PermissionError: If the user doesn't have permission to read or write files.
        OSError: For other OS-related errors during ZIP creation.
    """
    # Ensure source directory exists
    source_dir = Path(source_dir)
    if not source_dir.exists() or not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory '{source_dir}' not found or is not a directory")
    
    # Ensure parent directory for zip_path exists
    zip_path = Path(zip_path)
    make_dirs(zip_path.parent)
    
    # Create the ZIP file
    with zipfile.ZipFile(zip_path, "w", compression) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                # Get path relative to source_dir
                rel_path = os.path.relpath(abs_path, source_dir)
                # Add file to ZIP with project_name as the top directory
                zipf.write(abs_path, arcname=os.path.join(project_name, rel_path))
    
    return str(zip_path)
