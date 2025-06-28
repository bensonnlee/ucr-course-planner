import os
import json

# get student profile
def load_student_profile(path="../profiles/student.json"):
    with open(path, "r") as profile:
        return json.load(profile)

# --- Load all courses from course directory ---
def load_all_courses(directory="../data/processed"):
    all_courses = []
    for fname in os.listdir(directory):
        if fname.startswith("cs"):
            with open(os.path.join(directory, fname), "r") as f:
                all_courses.extend(json.load(f))
    return all_courses

# remove courses that don't match student constraints
def course_matches(course, student):
    taken = student["taken_courses"]
    prefs = student["preferences"]

    if course["subjectCourse"] in taken:
        return False

    if prefs.get("no_friday") and "false" in course.get("Monday", ""):
        return False

    if prefs.get("no_mornings"):
        start = course.get("beginTime", "")
        if start and start[:2].isdigit() and int(start[:2]) < 10:
            return False

    # if prefs.get("max_units") and course.get("units", 0) > prefs["max_units"]:
    #     return False

    return True

# rank the course by interest keywords
def rank_by_interests(courses, interests):
    ranked = []
    for course in courses:
        desc = course.get("courseTitle", "").lower()
        score = sum(1 for word in interests if word.lower() in desc)
        ranked.append((score, course))
    return [c for score, c in sorted(ranked, key=lambda x: -x[0]) if score > 0]

# main
def main():
    student = load_student_profile()
    
    all_courses = load_all_courses()
    print(json.dumps(all_courses, indent=2))

    filtered = [c for c in all_courses if course_matches(c, student)]
    ranked = rank_by_interests(filtered, student["preferences"]["interests"])

    print("\n🎓 Recommended Courses:\n")
    for course in ranked[:5]:
        print(f"{course['subjectCourse']}: {course['courseTitle']} — {course['creditHourHigh']} units")
        print(course.get("description", "No description available."))
        print("-" * 60)

if __name__ == "__main__":
    main()
