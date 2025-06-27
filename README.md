# 🧠 UCR Course Planner Chatbot

An AI-powered course scheduling assistant that helps UCR students build optimal class schedules. Students can share their degree progress and preferences, and the chatbot generates valid course schedules for the quarter.

**⚡ 1-Week MVP Timeline**: Command-line chatbot with core scheduling logic and OpenAI integration.

---

## 📌 Project Goals

- ✅ **Data Collection**: Scrape and process UCR course catalog data from Banner API
- 🚧 **Smart Filtering**: Match courses against student prerequisites and preferences  
- 🚧 **Schedule Generation**: Create conflict-free course combinations  
- 🚧 **Chatbot Interface**: Natural language interaction for gathering student needs

---

## 🔧 Current Stack

**Language**: Python  
**Data Storage**: JSON files (97 subject-specific files)  
**Data Collection**: `requests` + UCR Banner API scraping  
**AI / Chatbot**: Groq API (free tier - 30 requests/minute)  
**Interface**: Command-line (1-week MVP)

**Current Data**: ~11K courses for Fall 2024 (term 202440) split by subject

---

## 🚀 1-Week Development Plan

### **Days 1-2: Core Data Processing**
- [x] Course data scraping and processing (COMPLETE)
- [ ] Prerequisites parser - extract course codes from prerequisite text
- [ ] Mock student profiles - create sample students with different majors/progress
- [ ] Basic eligibility filter - match completed courses against prerequisites

### **Days 3-4: Schedule Logic**
- [ ] Time conflict detection - parse meeting times, detect overlaps
- [ ] Simple recommendation engine - score courses by eligibility → major requirements → availability
- [ ] Hard-coded major requirements - CS/Engineering degree plans (skip web scraping)

### **Days 5-6: Chatbot Interface**
- [ ] Command-line chatbot - Q&A flow to gather student information
- [ ] Groq API integration - extract preferences from natural language
- [ ] Schedule output - present recommendations in readable format

### **Day 7: Polish & Demo**
- [ ] Testing with sample students
- [ ] Demo preparation and documentation

---

## 📁 Project Structure

```
ucr-course-planner/
├── data/
│   ├── raw/course_data.json           # ~35MB raw course data
│   └── processed/                     # 97 subject-specific JSON files
│       ├── cs_courses.json
│       ├── math_courses.json
│       └── ...
├── src/
│   ├── scraper.py                     # UCR Banner API scraper
│   ├── clean.py                       # Data processing pipeline
│   ├── write_local_data.py            # Data persistence
│   └── analyze_json_entries.py        # Data structure analysis
└── requirements.txt
```

---

## 🏃 Quick Start

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Verify data (should show 97 subject files)
ls data/processed/
```

### Data Pipeline
```bash
# Fetch fresh course data (optional - data already exists)
python src/scraper.py

# Process and split by subject
python src/clean.py

# Analyze data structure
python src/analyze_json_entries.py
```

---

## 💡 MVP Shortcuts for 1-Week Timeline

- **No web interface** - Command-line only
- **Hard-coded major requirements** - Skip web scraping, manually define CS/Engineering plans
- **Simple prerequisite parsing** - Basic regex pattern matching
- **Single term focus** - Fall 2024 data only
- **Manual testing** - No automated test suite

---

## 🎯 Success Criteria

A working command-line chatbot where students can:
1. Describe their major and completed courses in natural language
2. State their preferences (units, time constraints, etc.)
3. Receive a list of recommended courses for Fall 2024
4. See course details including times, availability, and prerequisites

---

## 📄 License

MIT License