import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

print("AI Dog initialized!")

def get_subject_path(course_name: str) -> str:
    subject = ""
    for i in range(len(course_name)):
        if not course_name[i].isalpha():
            subject = course_name[:i]
            break
    path_name = "../data/processed/subjects/" + subject + ".json"
    return path_name

def answer_question(completed_courses, formatted_courses, question: str) -> str:
    try: 
        completed_courses_string = ", ".join(completed_courses)
        formatted_courses_string = str(formatted_courses)
        context = "A student in computer science at UCR is wanting to create a schedule for next quarter. Here is a list of courses they have already completed: " + completed_courses_string
        context = context + "\n and here is a json file list of the possible courses they can take with different information about the sections such as scheduled days, times, rooms, and more: " + formatted_courses_string
        context = context + "\nThe schedule should be reasonable such as no times overlapping, and should make good progress to their degree according to the degree catalog. \
REALLY REALLY pay attention to prerequisites for each course. If all the prerequisites for that course are not clearly in the completed courses, do not recommend it. \
Each course needs a section of a lecture and its corresponding discussion or lab which are linked together. One can not be scheduled without the other. \
Finally accomodate as much as possible to the student\'s wishes in what they want for their schedule, and you can also give suggestions if needed. \
List out their course schedule with the classes and corresponding times of the courses during the week. \
In your response, do not type out any part of the text mentioning this context, only context from the student prompt \
\nHere is the student\'s prompt: "
        context = context + question
        response = model.generate_content(context)
        return response.text
    except Exception as err:
        print(f"An error has occured: {err}")
        return "ERROR"
    
if __name__ == "__main__":
    # question = "What is the best dog?"
    # print(f"Asking: {question}")
    # answer = answer_question(question)
    # print(f"Answer: {answer}")

    with open("../data/students/mock_student.json", 'r', encoding='utf-8') as f:
        student = json.load(f)

    #print(student.get("name", "None"))

    completed_courses = student.get("completed_courses", "")
    completed_names = []
    for course in completed_courses:
        completed_names.append(course.get("course_code", "NONE"))
    print(completed_names)

    possible_courses = student.get("courses_to_complete", "")
    #print(possible_courses)

    possible_course_data = []
    choose_one_list = []
    for possible_course in possible_courses:
        course_name = possible_course.get("course_code","")

        if(course_name == ""):
            list_of_one_breadth_courses = possible_course.get("choose_one")
            for choose_one in list_of_one_breadth_courses:
                one_name = choose_one.get("course_code", "")
                choose_one_list.append(one_name)
                with open(get_subject_path(one_name), 'r', encoding='utf-8') as f:
                    all_courses_one_subject = json.load(f)

                current_course = all_courses_one_subject.get(one_name, "ERR")
                possible_course_data.append(current_course)
        else:
            with open(get_subject_path(course_name), 'r', encoding='utf-8') as f:
                all_courses_one_subject = json.load(f)

            current_course = all_courses_one_subject.get(course_name, "ERR")
            possible_course_data.append(current_course)
    
    formatted_courses = json.dumps(possible_course_data, indent=4)
    #print(formatted_courses)----------------------------------------------------

    prompt = input("What schedule are you looking for?: ")
    answer = answer_question(completed_names, formatted_courses, prompt)
    print("Answer: " + answer)
