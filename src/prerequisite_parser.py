"""
This module contains functions to parse prerequisite information from UCR course data.
"""
import re
from typing import Dict, List, Any


def parse_prerequisites(prerequisite_text: str) -> Dict[str, Any]:
    """
    Parse prerequisite text into structured data.
    
    Args:
        prerequisite_text: Raw prerequisite text from UCR system
    
    Returns:
        Dict containing parsed prerequisite information:
        - raw_text: Original prerequisite text
        - courses: List of required courses with details
        - has_prerequisites: Boolean indicating if prerequisites exist
        - logic: Description of prerequisite logic (AND/OR relationships)
    """
    if not prerequisite_text or prerequisite_text.strip() == "":
        return {
            "raw_text": "",
            "courses": [],
            "has_prerequisites": False,
            "logic": None
        }
    
    # Extract course requirements
    courses = extract_course_requirements(prerequisite_text)
    
    # Determine logic relationships
    logic = determine_prerequisite_logic(prerequisite_text)
    
    return {
        "raw_text": prerequisite_text,
        "courses": courses,
        "has_prerequisites": len(courses) > 0,
        "logic": logic
    }


def extract_course_requirements(text: str) -> List[Dict[str, Any]]:
    """
    Extract individual course requirements from prerequisite text.
    
    Args:
        text: Prerequisite text
    
    Returns:
        List of course requirement dictionaries
    """
    courses = []
    
    # Pattern to match course requirements like "Computer Science 010C"
    # or "Mathematics 009C" with minimum grade
    course_pattern = r'Course or Test:\s*([A-Za-z ]+)\s*([0-9A-Z]+)\s*\n\s*Minimum Grade of ([A-Z][+-]?)'
    
    matches = re.findall(course_pattern, text)
    
    for match in matches:
        subject_name, course_number, min_grade = match
        
        # Clean up subject name and try to extract subject code
        subject_name = subject_name.strip()
        subject_code = extract_subject_code(subject_name)
        
        course_info = {
            "subject_name": subject_name,
            "subject_code": subject_code,
            "course_number": course_number.strip(),
            "minimum_grade": min_grade.strip(),
            "concurrent_allowed": "May not be taken concurrently" not in text
        }
        
        courses.append(course_info)
    
    return courses


def extract_subject_code(subject_name: str) -> str:
    """
    Extract subject code from full subject name.
    
    Args:
        subject_name: Full subject name (e.g., "Computer Science")
    
    Returns:
        Subject code (e.g., "CS")
    """
    # Common subject mappings
    subject_mappings = {
        "Computer Science": "CS",
        "Mathematics": "MATH",
        "Physics": "PHYS",
        "Chemistry": "CHEM",
        "Biology": "BIOL",
        "Statistics": "STAT",
        "English": "ENGL",
        "Engineering": "ENGR",
        "Business": "BUS",
        "Economics": "ECON"
    }
    
    return subject_mappings.get(subject_name, subject_name.upper().replace(" ", ""))


def determine_prerequisite_logic(text: str) -> str:
    """
    Determine the logical relationships in prerequisite requirements.
    
    Args:
        text: Prerequisite text
    
    Returns:
        String describing the logic (e.g., "AND", "OR", "COMPLEX")
    """
    text_lower = text.lower()
    
    has_and = " and " in text_lower or "\nand\n" in text_lower
    has_or = " or " in text_lower or "\nor\n" in text_lower
    
    if has_and and has_or:
        return "COMPLEX"
    elif has_and:
        return "AND"
    elif has_or:
        return "OR"
    else:
        return "SINGLE"


def get_prerequisite_summary(parsed_prerequisites: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of prerequisites.
    
    Args:
        parsed_prerequisites: Output from parse_prerequisites()
    
    Returns:
        Human-readable prerequisite summary
    """
    if not parsed_prerequisites["has_prerequisites"]:
        return "No prerequisites"
    
    courses = parsed_prerequisites["courses"]
    logic = parsed_prerequisites["logic"]
    
    if len(courses) == 1:
        course = courses[0]
        return f"{course['subject_code']} {course['course_number']} (min grade: {course['minimum_grade']})"
    
    course_summaries = []
    for course in courses:
        course_summaries.append(f"{course['subject_code']} {course['course_number']} (min grade: {course['minimum_grade']})")
    
    if logic == "AND":
        return " AND ".join(course_summaries)
    elif logic == "OR":
        return " OR ".join(course_summaries)
    else:
        return f"Complex requirements: {', '.join(course_summaries)}"


if __name__ == "__main__":
    # Test with sample prerequisite text
    sample_text = """Prerequisites:CS150
(
 Course or Test: Computer Science 010C 
 Minimum Grade of C-
 May not be taken concurrently. )
and
(
 Course or Test: Computer Science 111 
 Minimum Grade of D-
 May not be taken concurrently. )
and
(
 Course or Test: Mathematics 009C 
 Minimum Grade of D-
 May not be taken concurrently. )
or
(
 Course or Test: Mathematics 09HC 
 Minimum Grade of D-
 May not be taken concurrently. )"""
    
    parsed = parse_prerequisites(sample_text)
    print("Parsed prerequisites:")
    print(f"Has prerequisites: {parsed['has_prerequisites']}")
    print(f"Logic: {parsed['logic']}")
    print(f"Courses: {len(parsed['courses'])}")
    for course in parsed['courses']:
        print(f"  - {course}")
    print(f"Summary: {get_prerequisite_summary(parsed)}")