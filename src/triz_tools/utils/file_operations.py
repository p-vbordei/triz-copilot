#!/usr/bin/env python3
"""
File Operations Utilities

Common file and directory operations with error handling.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Union, Callable
from contextlib import contextmanager
import fcntl
import logging

logger = logging.getLogger(__name__)


def ensure_directory(path: Union[str, Path], mode: int = 0o755) -> Path:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        mode: Directory permissions
        
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True, mode=mode)
    return path


def safe_file_operation(
    operation: Callable,
    file_path: Union[str, Path],
    default_return: Any = None,
    create_backup: bool = False,
    backup_suffix: str = '.backup'
) -> Any:
    """
    Safely perform file operation with backup and error handling.
    
    Args:
        operation: Function to perform on file
        file_path: Path to file
        default_return: Default return value on error
        create_backup: Whether to create backup before operation
        backup_suffix: Suffix for backup file
        
    Returns:
        Result of operation or default_return
    """
    file_path = Path(file_path)
    backup_path = None
    
    try:
        # Create backup if requested and file exists
        if create_backup and file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Created backup: {backup_path}")
        
        # Perform operation
        result = operation(file_path)
        
        # Remove backup on success
        if backup_path and backup_path.exists():
            backup_path.unlink()
            logger.debug(f"Removed backup: {backup_path}")
        
        return result
        
    except Exception as e:
        logger.error(f"File operation failed for {file_path}: {str(e)}")
        
        # Restore from backup if available
        if backup_path and backup_path.exists():
            try:
                shutil.copy2(backup_path, file_path)
                logger.info(f"Restored from backup: {backup_path}")
            except Exception as restore_error:
                logger.error(f"Failed to restore backup: {str(restore_error)}")
        
        return default_return


@contextmanager
def atomic_write(
    file_path: Union[str, Path],
    mode: str = 'w',
    encoding: str = 'utf-8',
    **kwargs
):
    """
    Context manager for atomic file writing.
    
    Writes to temporary file first, then renames to target path.
    This ensures file is never in partially written state.
    
    Args:
        file_path: Target file path
        mode: File open mode
        encoding: Text encoding
        **kwargs: Additional arguments for open()
        
    Yields:
        File handle for writing
    """
    file_path = Path(file_path)
    ensure_directory(file_path.parent)
    
    # Create temporary file in same directory
    temp_fd, temp_path = tempfile.mkstemp(
        suffix='.tmp',
        prefix=f'.{file_path.name}.',
        dir=file_path.parent
    )
    
    temp_path = Path(temp_path)
    
    try:
        with open(temp_fd, mode, encoding=encoding, **kwargs) as f:
            yield f
        
        # Atomic rename
        temp_path.replace(file_path)
        logger.debug(f"Atomically wrote file: {file_path}")
        
    except Exception:
        # Clean up temporary file
        if temp_path.exists():
            temp_path.unlink()
        raise


def read_json_file(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Safely read JSON file with error handling.
    
    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or is invalid
        
    Returns:
        Parsed JSON data or default value
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.debug(f"JSON file does not exist: {file_path}")
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {str(e)}")
        return default
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {str(e)}")
        return default


def write_json_file(
    file_path: Union[str, Path],
    data: Any,
    indent: int = 2,
    atomic: bool = True,
    create_backup: bool = False
) -> bool:
    """
    Safely write JSON file.
    
    Args:
        file_path: Path to JSON file
        data: Data to write
        indent: JSON indentation
        atomic: Use atomic write
        create_backup: Create backup before writing
        
    Returns:
        True if successful, False otherwise
    """
    file_path = Path(file_path)
    ensure_directory(file_path.parent)
    
    try:
        if atomic:
            with atomic_write(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
        else:
            def write_operation(path):
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=indent, ensure_ascii=False)
                return True
            
            return safe_file_operation(
                write_operation,
                file_path,
                default_return=False,
                create_backup=create_backup
            )
        
        logger.debug(f"Successfully wrote JSON file: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error writing JSON file {file_path}: {str(e)}")
        return False


@contextmanager
def file_lock(file_path: Union[str, Path], timeout: float = 10.0):
    """
    Context manager for file locking.
    
    Args:
        file_path: Path to file to lock
        timeout: Lock timeout in seconds
        
    Yields:
        File handle with acquired lock
    """
    file_path = Path(file_path)
    lock_file = file_path.with_suffix(file_path.suffix + '.lock')
    
    try:
        # Create lock file
        with open(lock_file, 'w') as lock_f:
            # Try to acquire exclusive lock
            try:
                fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, OSError):
                # Lock not available immediately
                import time
                start_time = time.time()
                while time.time() - start_time < timeout:
                    try:
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except (IOError, OSError):
                        time.sleep(0.1)
                else:
                    raise TimeoutError(f"Could not acquire lock for {file_path} within {timeout} seconds")
            
            logger.debug(f"Acquired lock for: {file_path}")
            yield lock_f
            
    finally:
        # Clean up lock file
        if lock_file.exists():
            try:
                lock_file.unlink()
                logger.debug(f"Released lock for: {file_path}")
            except Exception as e:
                logger.warning(f"Could not remove lock file {lock_file}: {str(e)}")


def copy_file_with_metadata(
    src: Union[str, Path],
    dst: Union[str, Path],
    preserve_permissions: bool = True
) -> bool:
    """
    Copy file with metadata preservation.
    
    Args:
        src: Source file path
        dst: Destination file path
        preserve_permissions: Whether to preserve file permissions
        
    Returns:
        True if successful, False otherwise
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        ensure_directory(dst_path.parent)
        
        if preserve_permissions:
            shutil.copy2(src_path, dst_path)
        else:
            shutil.copy(src_path, dst_path)
        
        logger.debug(f"Copied file: {src_path} -> {dst_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error copying file {src} to {dst}: {str(e)}")
        return False


def get_file_info(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Get file information.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information or None if file doesn't exist
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return None
    
    try:
        stat = file_path.stat()
        return {
            "path": str(file_path),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "is_file": file_path.is_file(),
            "is_directory": file_path.is_dir(),
            "permissions": oct(stat.st_mode)[-3:]
        }
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {str(e)}")
        return None


def cleanup_temp_files(directory: Union[str, Path], pattern: str = "*.tmp", max_age_hours: int = 24) -> int:
    """
    Clean up temporary files older than specified age.
    
    Args:
        directory: Directory to clean
        pattern: File pattern to match
        max_age_hours: Maximum file age in hours
        
    Returns:
        Number of files cleaned up
    """
    import time
    from glob import glob
    
    directory = Path(directory)
    if not directory.exists():
        return 0
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    cleaned_count = 0
    
    try:
        for file_path in directory.glob(pattern):
            try:
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    cleaned_count += 1
                    logger.debug(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not clean up {file_path}: {str(e)}")
        
        logger.info(f"Cleaned up {cleaned_count} temporary files in {directory}")
        return cleaned_count
        
    except Exception as e:
        logger.error(f"Error during temp file cleanup in {directory}: {str(e)}")
        return 0


def archive_old_files(
    source_dir: Union[str, Path],
    archive_dir: Union[str, Path],
    max_age_days: int = 30,
    pattern: str = "*",
    compress: bool = True
) -> int:
    """
    Archive old files to separate directory.
    
    Args:
        source_dir: Source directory
        archive_dir: Archive directory
        max_age_days: Maximum file age in days
        pattern: File pattern to match
        compress: Whether to compress archived files
        
    Returns:
        Number of files archived
    """
    import time
    import gzip
    
    source_dir = Path(source_dir)
    archive_dir = Path(archive_dir)
    ensure_directory(archive_dir)
    
    if not source_dir.exists():
        return 0
    
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 3600
    archived_count = 0
    
    try:
        for file_path in source_dir.glob(pattern):
            if not file_path.is_file():
                continue
                
            try:
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    # Create archive path
                    archive_path = archive_dir / file_path.name
                    
                    if compress and not file_path.name.endswith('.gz'):
                        archive_path = archive_path.with_suffix(archive_path.suffix + '.gz')
                        
                        # Compress and move
                        with open(file_path, 'rb') as f_in:
                            with gzip.open(archive_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                    else:
                        # Just move
                        shutil.move(str(file_path), str(archive_path))
                    
                    # Remove original
                    if file_path.exists():
                        file_path.unlink()
                    
                    archived_count += 1
                    logger.debug(f"Archived file: {file_path} -> {archive_path}")
                    
            except Exception as e:
                logger.warning(f"Could not archive {file_path}: {str(e)}")
        
        logger.info(f"Archived {archived_count} files from {source_dir}")
        return archived_count
        
    except Exception as e:
        logger.error(f"Error during file archival: {str(e)}")
        return 0