import json
import os
from collections import defaultdict

def split_courses_by_subject():
    input_file = 'data/raw/course_data.json'
    output_dir = 'data/processed'
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        courses = json.load(f)
    
    courses_by_subject = defaultdict(list)
    
    for course in courses:
        subject = course.get('subject', 'UNKNOWN')
        courses_by_subject[subject].append(course)
    
    for subject, subject_courses in courses_by_subject.items():
        output_file = os.path.join(output_dir, f'{subject.lower()}_courses.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(subject_courses, f, indent=2, ensure_ascii=False)
        print(f"Created {output_file} with {len(subject_courses)} courses")
    
    print(f"Split {len(courses)} total courses into {len(courses_by_subject)} subject files")

if __name__ == '__main__':
    split_courses_by_subject()