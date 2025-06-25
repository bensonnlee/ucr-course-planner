# 🧠 AI Course Planner

This project is a smart course recommendation system for university students. It pulls real-time course registration data, analyzes it with logic and AI, and generates optimized course schedules based on each student’s history and preferences.

The goal is to reduce the stress and guesswork of class planning, helping students build effective schedules, whether they’re trying to graduate early, avoid 8AMs, or fulfill GE and major requirements efficiently.

---

## 📌 Project Goals

- ✅ Automatically ingest and store course catalog and enrollment data  
- ✅ Filter courses based on prerequisites and student preferences  
- ✅ Recommend valid and optimal class schedules  
- ✅ Allow students to describe preferences in plain language via a chatbot  
- 🚧 Eventually display and edit schedules through a web interface  

---

## 🔧 Stack Overview

**Language**: Python  
**Data Collection**: `requests`, `json`  
**Database**: MongoDB with `pymongo`  
**Data Handling**: `pandas`, `jupyter` (optional)  
**AI / Chatbot**: OpenAI API (`openai` Python SDK)  
**Backend API**: FastAPI (starting Phase 4)  
**Frontend**: Simple HTML or React (starting Phase 4)

---

## ✅ Phase 1: Data Pipeline & Exploration

**Goal**: Collect, clean, and explore course data from the registration system.

### Milestones

1. **Scraper**  
   - Use `requests` to download course data.  
   - Store raw JSON files locally under `/data/raw/`.

2. **MongoDB Integration**  
   - Store course documents using `pymongo`.  
   - Flexible schema supports variations in class formats.

3. **Data Cleaning**  
   - Normalize fields (e.g., course codes, names, times).  
   - Deduplicate courses and handle cross-listed sections.

4. **Exploration**  
   - Use `pandas` or Jupyter notebooks to explore:  
     - Common prerequisites  
     - Time conflicts  
     - Waitlist trends (if available)

**Success criteria**: A clean, queryable MongoDB collection of classes.

---

## ⚙️ Phase 2: Basic Course Planning Backend

**Goal**: Recommend courses that a student is eligible for and interested in.

### Milestones

1. **Define Student Profile Format**  
Example:
```
{
  "taken_courses": ["CS 10", "MATH 2"],
  "preferences": {
    "preferred_subjects": ["CS", "STAT"],
    "ge_requirements": ["Area C"],
    "max_units": 16,
    "no_early_classes": true
  }
}
```

2. **Eligibility Filtering**  
   - Check prerequisites based on taken courses.  
   - Discard ineligible options.

3. **Time and Preference Filtering**  
   - Remove classes that violate preferences (e.g., early classes, wrong subject).

4. **Ranking System**  
   - Prioritize major requirements, then GE, then electives.  
   - Basic scoring algorithm for initial MVP.

**Success criteria**: A function that takes a profile and returns ranked course suggestions.

---

## 🧠 Phase 3: Local AI Chatbot Interface

**Goal**: Interact with users through natural language and generate structured preferences.

### Milestones

1. **Simple Chat Interface**  
   - Example prompt:  
     _“I need 4 classes, no 8AMs, and one Area D course.”_

2. **Preference Extraction**  
   - Use OpenAI API (with function calling or prompt parsing) to convert natural language → student profile JSON.

3. **Recommendation Call**  
   - Pass structured profile to planner logic.  
   - Return recommended courses to user via terminal or local script.

**Success criteria**: Users describe goals in natural language and receive a list of recommended classes.

---

## 🌐 Phase 4: Web API and UI (MVP)

**Goal**: Make the planner accessible through a simple web interface.

### Milestones

1. **Backend API (FastAPI)**  
   - `POST /recommend`: Accepts student profile, returns course list.  
   - `GET /courses`: Optional, lists or searches all classes.

2. **Minimal Frontend (Optional)**  
   - Input form or chatbot-style UI (HTML or React).  
   - Display ranked course results with course name, time, units, and availability.

3. **Deploy the MVP**  
   - Backend: Render, Railway, or Fly.io  
   - Frontend: Vercel or Netlify  
   - MongoDB: MongoDB Atlas (cloud)

**Success criteria**: A user can go to a webpage, input their course preferences, and get an intelligently suggested list of classes.

---

## 📄 License

MIT License
