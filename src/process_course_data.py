#!/usr/bin/env python3
"""
Course Data Processing Script

Processes raw course catalog data from Banner API into cleaned, subject-organized files
for the UCR Course Scheduling Chatbot.

Input: data/raw/course_catalog.json (raw Banner API data)
Output: data/processed/subjects/[SUBJECT].json (cleaned, organized by subject)
"""

import json
from collections import defaultdict
from pathlib import Path


def clean_course_data(course):
    """
    Extract and clean essential course information from raw Banner data.
    
    Args:
        course (dict): Raw course data from Banner API
        
    Returns:
        dict: Cleaned course data with essential fields only
    """
    # Extract basic course info
    course_id = course.get('subjectCourse', '')
    title = course.get('courseTitle', '')
    
    # Handle credit hours (can be fixed value or range)
    credit_hours = course.get('creditHours')
    if credit_hours is None or credit_hours == 0:
        # Handle credit range (e.g., 1-6 credits) or when creditHours is 0
        low = course.get('creditHourLow', 0)
        high = course.get('creditHourHigh', 0)
        if low and high and low != high:
            credits = f"{low}-{high}"
        elif high and high > 0:
            credits = str(high)
        elif low and low > 0:
            credits = str(low)
        else:
            credits = "TBD"
    else:
        credits = str(credit_hours)
    
    # Extract prerequisites
    prerequisites = course.get('prerequisites', '').strip()
    
    # Build section info
    section_info = {
        'section': course.get('sequenceNumber', ''),
        'crn': course.get('courseReferenceNumber', ''),
        'instructor': None,
        'schedule': {
            'days': [],
            'startTime': None,
            'endTime': None,
            'building': None,
            'room': None
        },
        'type': course.get('scheduleTypeDescription', ''),
        'method': course.get('instructionalMethodDescription', ''),
        'availability': {
            'enrolled': course.get('enrollment', 0),
            'capacity': course.get('maximumEnrollment', 0),
            'available': course.get('seatsAvailable', 0)
        }
    }
    
    # Extract instructor info
    faculty = course.get('faculty', [])
    if faculty and len(faculty) > 0:
        primary_instructor = next((f for f in faculty if f.get('primaryIndicator')), faculty[0])
        section_info['instructor'] = primary_instructor.get('displayName', 'TBD')
    else:
        section_info['instructor'] = 'TBD'
    
    # Extract meeting time info
    meetings = course.get('meetingsFaculty', [])
    if meetings and len(meetings) > 0:
        meeting_time = meetings[0].get('meetingTime', {})
        if meeting_time:
            # Extract day information
            days = []
            day_fields = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            day_abbrev = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
            
            for day_field, abbrev in zip(day_fields, day_abbrev):
                if meeting_time.get(day_field, False):
                    days.append(abbrev)
            
            section_info['schedule'] = {
                'days': days,
                'startTime': meeting_time.get('beginTime'),
                'endTime': meeting_time.get('endTime'),
                'building': meeting_time.get('building'),
                'room': meeting_time.get('room')
            }
    
    return {
        'course_id': course_id,
        'title': title,
        'credits': credits,
        'prerequisites': prerequisites,
        'section': section_info
    }


def group_courses_by_subject(raw_data):
    """
    Group courses by subject and combine sections for the same course.
    
    Args:
        raw_data (list): List of raw course data
        
    Returns:
        dict: Dictionary of subjects with organized course data
    """
    subjects = defaultdict(lambda: defaultdict(lambda: {
        'title': '',
        'credits': '',
        'prerequisites': '',
        'sections': []
    }))
    
    for course in raw_data:
        subject = course.get('subject', '')
        if not subject:
            continue
            
        cleaned = clean_course_data(course)
        course_id = cleaned['course_id']
        
        if not course_id:
            continue
        
        # Update course info (title, credits, prerequisites should be same across sections)
        course_entry = subjects[subject][course_id]
        course_entry['title'] = cleaned['title']
        course_entry['credits'] = cleaned['credits']
        course_entry['prerequisites'] = cleaned['prerequisites']
        
        # Add section info
        course_entry['sections'].append(cleaned['section'])
    
    return subjects


def create_subjects_index(subjects):
    """
    Create an index of all subjects with metadata.
    
    Args:
        subjects (dict): Dictionary of subjects with course data
        
    Returns:
        dict: Index with subject metadata
    """
    index = {}
    
    for subject, courses in subjects.items():
        total_courses = len(courses)
        total_sections = sum(len(course['sections']) for course in courses.values())
        
        index[subject] = {
            'total_courses': total_courses,
            'total_sections': total_sections,
            'filename': f"{subject}.json"
        }
    
    return index


def main():
    """Main processing function."""
    # Setup paths
    base_dir = Path(__file__).parent.parent
    raw_file = base_dir / 'data' / 'raw' / 'course_catalog.json'
    output_dir = base_dir / 'data' / 'processed' / 'subjects'
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading raw course catalog...")
    try:
        with open(raw_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {raw_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {raw_file}")
        return
    
    print(f"Processing {len(raw_data)} courses...")
    
    # Group courses by subject
    subjects = group_courses_by_subject(raw_data)
    
    print(f"Found {len(subjects)} subjects")
    
    # Write subject files
    for subject, courses in subjects.items():
        subject_file = output_dir / f"{subject}.json"
        
        with open(subject_file, 'w', encoding='utf-8') as f:
            json.dump(dict(courses), f, indent=2, ensure_ascii=False)
        
        print(f"  {subject}: {len(courses)} courses -> {subject_file.name}")
    
    # Create subjects index
    print("Creating subjects index...")
    index = create_subjects_index(subjects)
    index_file = output_dir.parent / 'subjects_index.json'
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"Subjects index saved to {index_file}")
    print("Processing complete!")
    
    # Print summary
    total_courses = sum(len(courses) for courses in subjects.values())
    total_sections = sum(
        sum(len(course['sections']) for course in courses.values())
        for courses in subjects.values()
    )
    
    print(f"\nSummary:")
    print(f"  Total subjects: {len(subjects)}")
    print(f"  Total courses: {total_courses}")
    print(f"  Total sections: {total_sections}")


if __name__ == "__main__":
    main()