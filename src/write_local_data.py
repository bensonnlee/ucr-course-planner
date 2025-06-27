"""
This module contains the code to write course
data to the local data/raw/course_data.json file.
"""

import json
import sys

from scraper import fetch_course_data
from scraper_parallel import fetch_course_data as fetch_course_data_parallel


def write_course_data(term: str = "202440", use_parallel: bool = False):
    """
    Write course data to the local course_data.json file.
    
    Args:
        term: Term code (e.g., "202440" for Fall 2024)
        use_parallel: Whether to use the parallel scraper version
    """
    if use_parallel:
        print("Using parallel scraper...")
        courses = fetch_course_data_parallel(term)
    else:
        print("Using standard scraper...")
        courses = fetch_course_data(term)
    
    with open("data/raw/course_data.json", "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    use_parallel = len(sys.argv) > 1 and sys.argv[1] == "parallel"
    write_course_data(use_parallel=use_parallel)
