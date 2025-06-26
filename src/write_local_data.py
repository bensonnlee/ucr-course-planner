"""
This module contains the code to write course
data to the local data/raw/course_data.json file.
"""

import json

from scraper import fetch_course_data


def write_course_data(term: str = "202440"):
    """
    Write course data to the local course_data.json file.
    """
    courses = fetch_course_data(term)
    with open("data/raw/course_data.json", "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    write_course_data()
