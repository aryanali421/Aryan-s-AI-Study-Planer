# 📚 Last Stretch – AI-Powered Study Planner

Last Stretch is an AI-powered study planning application designed to help students organize their preparation, manage study sessions, and stay on track before exams.

Instead of manually building a study timetable, students can use AI to generate personalized study plans based on their subjects, exam dates, priorities, and available study time.

## ✨ Features

- **AI Study Plan Generator:** Automatically creates personalized study schedules using AI.
- **Exam Countdown:** Keep track of upcoming examinations and important deadlines.
- **Subject Prioritization:** Give additional attention to difficult subjects and weaker topics.
- **Daily Study Board:** View and manage your scheduled study sessions.
- **Progress Tracking:** Mark completed sessions and monitor study progress.
- **AI Study Coach:** Ask questions and receive personalized study guidance.
- **Plan Management:** Review and manage your generated study schedule.
- **CSV Export:** Export your study plan for external use.

## 🛠️ Tech Stack

- Python
- Streamlit
- Groq API
- Pandas
- HTML and CSS

## 🤖 AI Integration

Last Stretch uses the Groq API to generate personalized study schedules and provide AI-powered study assistance.

The AI helps organize study sessions, prioritize topics, and support students throughout their exam preparation.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd last-stretch
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API key

Create a `.streamlit` folder in the project directory and add a file named `secrets.toml`.

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

Alternatively, configure the `GROQ_API_KEY` environment variable.

### 4. Run the application

```bash
streamlit run app.py
```

## 🔐 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key required to access Groq's AI models |

Never commit API keys or your `secrets.toml` file to a public repository.

## 🎯 Project Objective

The objective of Last Stretch is to make exam preparation more organized, manageable, and personalized through AI.

It combines intelligent scheduling, progress monitoring, and study assistance into one application.

## 👨‍💻 Author

**Aryan Ali**

---

*Built with Python, Streamlit, and AI.*
