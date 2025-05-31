"""
File and directory manipulation utilities.

This module provides utilities for working with files and directories,
including creating directories and reading/writing file content.
"""

import os
import errno
from typing import Optional, Union, AnyStr
from pathlib import Path


def make_dirs(path: Union[str, Path], mode: int = 0o777) -> None:
    """
    Create directories recursively, similar to `mkdir -p`.
    
    Args:
        path: Directory path to create.
        mode: Directory permissions (defaults to 0o777).
        
    Raises:
        PermissionError: If the user doesn't have permission to create the directory.
        OSError: For other OS-related errors during directory creation.
    """
    try:
        os.makedirs(path, mode=mode, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(f"Permission denied when creating directory: {path}") from e
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise OSError(f"Failed to create directory: {path}. Error: {str(e)}") from e


def write_file(path: Union[str, Path], content: AnyStr, encoding: str = "utf-8") -> None:
    """
    Write content to a file, creating parent directories if they don't exist.
    
    Args:
        path: File path to write to.
        content: Content to write to the file.
        encoding: Character encoding to use (defaults to UTF-8).
        
    Raises:
        PermissionError: If the user doesn't have permission to write to the file.
        OSError: For other OS-related errors during file writing.
    """
    # Convert Path objects to strings
    path_str = str(path)
    
    # Create parent directories if they don't exist
    directory = os.path.dirname(path_str)
    if directory and not os.path.exists(directory):
        make_dirs(directory)
    
    try:
        # Handle both string and bytes content
        mode = "w" if isinstance(content, str) else "wb"
        encoding_arg = {"encoding": encoding} if mode == "w" else {}
        
        with open(path_str, mode, **encoding_arg) as f:
            f.write(content)
    except PermissionError as e:
        raise PermissionError(f"Permission denied when writing to file: {path_str}") from e
    except OSError as e:
        raise OSError(f"Failed to write to file: {path_str}. Error: {str(e)}") from e


def read_file(path: Union[str, Path], encoding: str = "utf-8") -> AnyStr:
    """
    Read content from a file.
    
    Args:
        path: File path to read from.
        encoding: Character encoding to use (defaults to UTF-8).
        
    Returns:
        The content of the file as a string.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        PermissionError: If the user doesn't have permission to read the file.
        OSError: For other OS-related errors during file reading.
    """
    # Convert Path objects to strings
    path_str = str(path)
    
    try:
        with open(path_str, "r", encoding=encoding) as f:
            return f.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {path_str}") from e
    except PermissionError as e:
        raise PermissionError(f"Permission denied when reading file: {path_str}") from e
    except OSError as e:
        raise OSError(f"Failed to read file: {path_str}. Error: {str(e)}") from e
