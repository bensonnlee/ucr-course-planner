from google import genai
from google.genai import types
from PIL import Image
import json

client = genai.Client(api_key="AIzaSyBr6ygL75JGfowAsVrT5QaCBlwBkQ_tjhg")

# reference data
student_major_plan = client.files.upload(file="../ucr-course-planner/data/student_ce_plan.png")
with open("../ucr-course-planner/data/processed/subjects/CS.json") as f:
  CS_course_catalog = f.read()
with open("../ucr-course-planner/data/processed/subjects/EE.json") as f:
  EE_course_catalog = f.read()
with open("../ucr-course-planner/data/processed/subjects/MATH.json") as f:
  MATH_course_catalog = f.read()
with open("../ucr-course-planner/data/processed/subjects/PHYS.json") as f:
  PHYS_course_catalog = f.read()

"""
CS_course_catalog = client.files.upload(file="../ucr-course-planner/data/processed/subjects/CS.json")
EE_course_catalog = client.files.upload(file="../ucr-course-planner/data/processed/subjects/EE.json")
MATH_course_catalog = client.files.upload(file="../ucr-course-planner/data/processed/subjects/MATH.json")
PHYS_course_catalog = client.files.upload(file="../ucr-course-planner/data/processed/subjects/PHYS.json")
"""

#print(course_catalog)

user_question = "What should my schedule for the next quarter be?"
classes_taken = ["CS10A", "ENGL001A", "ENGR001G", "MATH009A", "CS10B", "ENGL001B", "MATH009B", "PHYS040A", "CS10C", "MATH009C", "MATH011", "MATH045", "PHYS040B", "EE020B"]
response = client.models.generate_content(
  model="gemini-2.5-flash", 
  config=types.GenerateContentConfig(
    system_instruction="""Your goal is to help students create a course schedule for the current quarter. 
                        Give a short answer, giving only the list of specific classes suggesed based on the course catalog that should be taken and relevant information regarding times, sections, CRNs, and instructors.
                        The classes you choose needs to be based on the classes the student has already taken and can only include classes in the suggested course plan picture. 
                        No substitutes of other classes that technically meet prerequisite requirements but are not on the suggested course plan can be given.
                        Additionally, students can only take classes once they have the prerequisites for it.
                        You may give a very brief explanation as well."""
  ),
  contents=[
    user_question,
    classes_taken,
    CS_course_catalog,
    EE_course_catalog,
    MATH_course_catalog,
    PHYS_course_catalog,
    student_major_plan
  ]
)
print("Question:", user_question, "\n")
print("Classes taken:", classes_taken, "\n")
print("Response:", response.text)