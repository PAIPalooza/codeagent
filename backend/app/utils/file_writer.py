"""
File and directory manipulation utilities.

This module provides utilities for working with files and directories,
including creating directories and reading/writing file content.
"""

import os
import errno
from typing import Union, AnyStr, Optional
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
