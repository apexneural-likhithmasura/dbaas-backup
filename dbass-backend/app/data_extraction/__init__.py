"""
Data Extraction Module

This module handles extraction of data from various sources,
particularly JSON files from Reddit and other platforms.
"""

from .json_extraction import (
    extract_post_and_comments,
    process_multiple_json_files,
    run_complete_pipeline,
    convert_to_text_format,
    find_json_files
)

__all__ = [
    "extract_post_and_comments",
    "process_multiple_json_files",
    "run_complete_pipeline",
    "convert_to_text_format",
    "find_json_files"
]

