
import os
import json
import html
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st
from groq import Groq


# ============================================================
# 1. CONFIGURATION
# ============================================================

MODEL = "openai/gpt-oss-120b"

SESSION_TYPES = ["Learn", "Practice", "Revise", "Mock test"]

PALETTE = [
    "#FF6045",
    "#48B8A9",
    "#EAB85B",
    "#8795FF",
    "#C58BEA",
    "#91BE62",
]

MAX_DAYS = 45

st.set_page_config(
    page_title="Last Stretch",
    page_icon="🟥",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. COMPLETE VISUAL REDESIGN
# ============================================================

CSS = """
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800&display=swap');

:root {
    --bg: #11110F;
    --surface: #191916;
    --surface2: #22221E;
    --border: #34342F;
    --text: #F1EFE8;
    --muted: #929188;
    --accent: #FF6045;
    --green: #8EC7A0;
    --mono: 'DM Mono', monospace;
    --sans: 'DM Sans', sans-serif;
    --serif: 'Fraunces', serif;
}

.stApp {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
}

.block-container {
    max-width: 1320px;
    padding-top: 2.5rem;
    padding-bottom: 5rem;
}

#MainMenu,
footer,
[data-testid="stToolbar"] {
    visibility: hidden;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: #171715;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 7px 5px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    font-size: .9rem;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: var(--muted);
}

[data-testid="stMarkdownContainer"] p {
    color: var(--text);
}

h1, h2, h3, h4 {
    color: var(--text);
    font-family: var(--sans);
}

h1 {
    font-size: 2.7rem;
    font-weight: 800;
    letter-spacing: -.055em;
}

h2 {
    letter-spacing: -.035em;
}

.stCaption {
    color: var(--muted);
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTextArea"] textarea {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

[data-baseweb="select"] > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

[data-testid="stDateInput"] button,
[data-testid="stTimeInput"] button {
    color: var(--text) !important;
}

.stButton > button,
.stDownloadButton > button {
    background: var(--surface2);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
    min-height: 42px;
    font-family: var(--sans);
    font-weight: 600;
    transition: all .2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: var(--accent);
    color: var(--accent);
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: white !important;
}

[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 17px;
}

[data-testid="stMetricLabel"] {
    color: var(--muted);
}

[data-testid="stMetricValue"] {
    color: var(--text);
    font-family: var(--serif);
}

[data-testid="stProgressBar"] > div > div > div {
    background: var(--accent);
}

[data-testid="stProgressBar"] > div {
    background: var(--surface2);
}

[data-testid="stTabs"] button {
    font-family: var(--mono);
    font-size: .75rem;
}

.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
}

div[data-testid="stExpander"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 9px;
}

[data-testid="stDataFrame"],
[data-testid="stDataEditor"] {
    border: 1px solid var(--border);
    border-radius: 8px;
}

[data-testid="stChatMessage"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin-bottom: 12px;
}

[data-testid="stChatInput"] {
    border-color: var(--border);
}

[data-testid="stAlert"] {
    border-radius: 8px;
}

hr {
    border-color: var(--border);
}

.brand {
    font-family: var(--serif);
    font-size: 1.65rem;
    font-weight: 800;
    letter-spacing: -.05em;
}

.brand span {
    color: var(--accent);
}

.eyebrow {
    font-family: var(--mono);
    font-size: .69rem;
    letter-spacing: .16em;
    color: var(--muted);
    text-transform: uppercase;
}

.hero {
    background:
        radial-gradient(
            circle at 90% 20%,
            rgba(255,96,69,.12),
            transparent 35%
        ),
        var(--surface);
    border: 1px solid var(--border);
    border-radius: 13px;
    padding: 34px;
    margin-bottom: 25px;
}

.hero h1 {
    font-family: var(--serif);
    font-size: clamp(3.5rem, 8vw, 6rem);
    line-height: .95;
    margin: 12px 0;
}

.hero em {
    color: var(--accent);
    font-style: normal;
}

.hero p {
    color: var(--muted);
    max-width: 550px;
    font-size: 1rem;
}

.section-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border);
    padding-bottom: 11px;
    margin: 30px 0 17px;
}

.section-heading span {
    font-family: var(--mono);
    color: var(--muted);
    font-size: .69rem;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 12px;
}

.panel-accent {
    border-left: 3px solid var(--accent);
}

.subject-name {
    font-family: var(--serif);
    font-size: 1.5rem;
    font-weight: 700;
}

.big-number {
    font-family: var(--serif);
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -.06em;
}

.small-muted {
    color: var(--muted);
    font-size: .82rem;
}

.tag {
    display: inline-block;
    background: rgba(255,96,69,.12);
    color: var(--accent);
    border-radius: 5px;
    padding: 4px 9px;
    font-family: var(--mono);
    font-size: .68rem;
    margin: 3px;
}

.session-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 9px;
}

.session-card.done {
    opacity: .5;
}

.session-card.done .session-title {
    text-decoration: line-through;
}

.session-title {
    font-weight: 700;
    font-size: .95rem;
}

.ai-indicator {
    color: var(--accent);
    font-family: var(--mono);
    font-size: .7rem;
    letter-spacing: .13em;
}

.empty-state {
    padding: 35px 20px;
    text-align: center;
    border: 1px dashed var(--border);
    border-radius: 10px;
    color: var(--muted);
}

.stButton button:focus {
    box-shadow: none;
}

@media(max-width: 700px) {
    .hero {
        padding: 23px;
    }

    .hero h1 {
        font-size: 3.5rem;
    }
}

</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# 3. SESSION STATE
# ============================================================

DEFAULTS = {
    "page": "Dashboard",
    "plan": None,
    "info": {},
    "availability": [],
    "done": set(),
    "coach_messages": [],
    "quiz": [],
    "quiz_answers": {},
    "quiz_submitted": False,
    "quiz_score": None,
    "quiz_version": 0,
    "flashcards": [],
    "flashcard_version": 0,
    "analytics_report": "",
    "schedule_version": 0,
    "last_generation": None,
    "dropped": 0,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 4. GROQ CONNECTION
# ============================================================

def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY", "")


@st.cache_resource
def create_client(key):
    return Groq(api_key=key)


def get_client():
    key = get_api_key()

    if not key:
        st.error(
            "AI is not configured. Add GROQ_API_KEY "
            "to your Streamlit Secrets."
        )
        st.stop()

    return create_client(key)


def ai_request(system, user, json_mode=False, temperature=0.4):

    client = get_client()

    arguments = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": 8000,
    }

    if json_mode:
        arguments["response_format"] = {
            "type": "json_object"
        }

    response = client.chat.completions.create(**arguments)

    content = response.choices[0].message.content

    if json_mode:
        return json.loads(content)

    return content


# ============================================================
# 5. GENERAL HELPERS
# ============================================================

def section(title, subtitle=None):

    st.markdown(
        f"""
        <div class="section-heading">
            <span>{html.escape(title)}</span>
            <span>{html.escape(subtitle or "")}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hours_text(minutes):
    return f"{minutes / 60:.1f}h"


def subject_names():
    return list(st.session_state.info.keys())


def get_stats(plan=None):

    plan = plan if plan is not None else st.session_state.plan

    if plan is None or plan.empty:
        return 0, 0, 0

    total = int(plan["Minutes"].sum())

    completed = int(
        plan.loc[
            plan["id"].isin(st.session_state.done),
            "Minutes"
        ].sum()
    )

    percentage = round(completed / total * 100) if total else 0

    return total, completed, percentage


def current_subject_context():

    info = st.session_state.info

    if not info:
        return "No subjects have been added yet."

    return "\n".join(
        f"""
        Subject: {name}
        Exam: {details['exam']}
        Weak topics: {details['weak'] or 'Not specified'}
        """
        for name, details in info.items()
    )


def get_available_dates(start, end, days, hours):

    result = []
    current = start

    while current <= end:

        if current.weekday() in days and hours > 0:
            result.append((current, hours))

        current += timedelta(days=1)

    return result


def validate_json_list(data, key):

    result = data.get(key, [])

    return result if isinstance(result, list) else []


# ============================================================
# 6. AI STUDY PLAN GENERATOR
# ============================================================

def generate_schedule(subjects, availability, start_time, break_min):

    subject_data = "\n".join(
        f"""
        Subject: {s['Subject']}
        Exam: {s['exam']}
        Weak topics: {s['Weak topics'] or 'Not specified'}
        """
        for s in subjects
    )

    available_data = "\n".join(
        f"{d.isoformat()}: {h} available hours"
        for d, h in availability
    )

    system = """
You are the intelligent academic planning engine
for Last Stretch.

Your job is to produce a realistic personalized
study schedule.

PLANNING RULES:

1. Prioritize subjects with closer examinations.
2. Give weak topics additional attention.
3. Revisit weak topics at least twice when time permits.
4. Use spaced repetition.
5. Mix subjects across study days.
6. Each session must be between 25 and 90 minutes.
7. Never exceed available daily study hours.
8. Never schedule a subject on or after its exam.
9. Reserve the final 2-3 available study days before
   an exam primarily for revision and mock tests.
10. Use specific topic names.
11. Do not invent syllabus details.
12. Do not fill every available minute unnecessarily.
13. Distribute workload realistically.

SESSION TYPES:
Learn, Practice, Revise, Mock test.

Return ONLY valid JSON:

{
  "sessions": [
    {
      "date": "YYYY-MM-DD",
      "subject": "Physics",
      "topic": "Doppler effect numericals",
      "minutes": 60,
      "type": "Practice"
    }
  ]
}
"""

    user = f"""
TODAY: {date.today()}

SUBJECT INFORMATION:
{subject_data}

AVAILABLE STUDY DAYS:
{available_data}

DAILY START TIME:
{start_time}

BREAK BETWEEN SESSIONS:
{break_min} minutes

Create the complete personalized schedule.
"""

    result = ai_request(
        system,
        user,
        json_mode=True,
        temperature=0.3,
    )

    return validate_json_list(result, "sessions")


def clean_schedule(raw, subjects, availability, start_time, break_min):

    exam_dates = {
        s["Subject"]: s["exam"]
        for s in subjects
    }

    daily_limits = {
        d: int(h * 60)
        for d, h in availability
    }

    used = {}
    rows = []
    dropped = 0

    for session in sorted(
        raw,
        key=lambda x: str(x.get("date", ""))
    ):

        try:
            d = date.fromisoformat(session["date"])
            minutes = int(session["minutes"])
        except (ValueError, TypeError, KeyError):
            dropped += 1
            continue

        subject = str(
            session.get("subject", "")
        ).strip()

        topic = str(
            session.get("topic", "")
        ).strip()

        if (
            subject not in exam_dates
            or d not in daily_limits
            or d >= exam_dates[subject]
            or not 25 <= minutes <= 90
            or not topic
        ):
            dropped += 1
            continue

        if used.get(d, 0) + minutes > daily_limits[d]:
            dropped += 1
            continue

        used[d] = used.get(d, 0) + minutes

        session_type = session.get("type", "Learn")

        if session_type not in SESSION_TYPES:
            session_type = "Learn"

        rows.append({
            "Date": d,
            "Start": "",
            "Minutes": minutes,
            "Subject": subject,
            "Topic": topic,
            "Type": session_type,
        })

    cursor = {}

    for i, row in enumerate(rows):

        d = row["Date"]

        current = cursor.get(
            d,
            datetime.combine(d, start_time)
        )

        row["Start"] = current.strftime("%H:%M")

        cursor[d] = current + timedelta(
            minutes=row["Minutes"] + break_min
        )

        row["id"] = (
            f"v{st.session_state.schedule_version + 1}-{i}"
        )

    columns = [
        "Date",
        "Start",
        "Minutes",
        "Subject",
        "Topic",
        "Type",
        "id",
    ]

    return pd.DataFrame(rows, columns=columns), dropped


# ============================================================
# 7. AI STUDY COACH
# ============================================================

def ask_study_coach(question):

    total, completed, percentage = get_stats()

    progress = f"""
Planned study time: {hours_text(total)}
Completed study time: {hours_text(completed)}
Completion rate: {percentage}%
"""

    system = f"""
You are Last Stretch AI Study Coach.

You are an intelligent, patient, supportive academic mentor.

Your responsibilities:

- Explain difficult academic concepts.
- Help students understand rather than memorize.
- Create examples and practice questions.
- Recommend revision strategies.
- Help with exam preparation.
- Identify weak subjects.
- Suggest realistic next actions.
- Help students improve their study habits.

TEACHING STYLE:

1. Explain the underlying logic first.
2. Break complicated concepts into steps.
3. Use examples.
4. Avoid unnecessary jargon.
5. Ask questions when useful.
6. Never assume the student understands a concept.
7. Never invent syllabus information.
8. Be encouraging without giving unrealistic guarantees.

STUDENT SUBJECTS:

{current_subject_context()}

STUDENT PROGRESS:

{progress}
"""

    messages = [
        {"role": "system", "content": system}
    ]

    messages.extend(
        st.session_state.coach_messages[-12:]
    )

    messages.append({
        "role": "user",
        "content": question
    })

    client = get_client()

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.6,
        max_tokens=3000,
    )

    answer = response.choices[0].message.content

    st.session_state.coach_messages.extend([
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ])

    st.session_state.coach_messages = (
        st.session_state.coach_messages[-24:]
    )

    return answer


# ============================================================
# 8. AI QUIZ GENERATOR
# ============================================================

def generate_quiz(subject, topic, difficulty, count):

    system = """
You are an expert academic assessment designer.

Generate original educational questions.

Every question must:
- Test actual understanding.
- Have four distinct options.
- Have exactly one correct answer.
- Have an accurate explanation.
- Match the requested difficulty.

Return ONLY JSON:

{
  "questions": [
    {
      "question": "Question text",
      "options": {
        "A": "Option one",
        "B": "Option two",
        "C": "Option three",
        "D": "Option four"
      },
      "answer": "A",
      "explanation": "Detailed explanation"
    }
  ]
}
"""

    user = f"""
Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}
Question count: {count}

Create the questions.
"""

    result = ai_request(
        system,
        user,
        json_mode=True,
        temperature=0.5,
    )

    questions = validate_json_list(result, "questions")

    valid = []

    for q in questions:

        options = q.get("options", {})
        answer = str(q.get("answer", "")).upper()

        if (
            isinstance(options, dict)
            and set(options.keys()) == {"A", "B", "C", "D"}
            and answer in options
            and q.get("question")
        ):
            valid.append(q)

    return valid


# ============================================================
# 9. AI FLASHCARDS
# ============================================================

def generate_flashcards(subject, topic, count):

    system = """
You are an expert educational flashcard designer.

Create active-recall flashcards.

Each card must contain:
- A clear question or concept.
- A correct, concise explanation.
- Useful information for revision.

Avoid vague questions.

Return ONLY JSON:

{
  "flashcards": [
    {
      "front": "What is...",
      "back": "It is..."
    }
  ]
}
"""

    user = f"""
Subject: {subject}
Topic: {topic}
Number of cards: {count}

Create the flashcards.
"""

    result = ai_request(
        system,
        user,
        json_mode=True,
        temperature=0.4,
    )

    cards = validate_json_list(result, "flashcards")

    return [
        c for c in cards
        if c.get("front") and c.get("back")
    ]


# ============================================================
# 10. AI PROGRESS ANALYSIS
# ============================================================

def generate_progress_analysis(plan):

    total, completed, percentage = get_stats(plan)

    data = plan.copy()

    data["Completed"] = data["id"].isin(
        st.session_state.done
    )

    breakdown = []

    for subject, group in data.groupby("Subject"):

        breakdown.append({
            "subject": subject,
            "planned_minutes": int(group["Minutes"].sum()),
            "completed_minutes": int(
                group.loc[
                    group["Completed"],
                    "Minutes"
                ].sum()
            ),
            "sessions_completed": int(
                group["Completed"].sum()
            ),
            "total_sessions": len(group),
        })

    system = """
You are an academic performance analyst.

Analyze the supplied study data.

Provide:

1. Overall performance summary.
2. Subject-by-subject analysis.
3. Subjects needing more attention.
4. Study consistency observations.
5. Potential planning issues.
6. Three specific next actions.

IMPORTANT:

- A completed session does not prove mastery.
- Do not invent examination scores.
- Do not claim the student is exam-ready without test results.
- Distinguish completed study time from actual learning outcomes.
- Make recommendations based on the supplied data.

Use headings and clear bullet points.
"""

    user = f"""
Overall completion: {percentage}%

Planned minutes: {total}
Completed minutes: {completed}

SUBJECT STATISTICS:

{json.dumps(breakdown, indent=2)}

STUDENT EXAM INFORMATION:

{current_subject_context()}

Analyze this student's study progress.
"""

    return ai_request(
        system,
        user,
        temperature=0.4,
    )


# ============================================================
# 11. ADAPTIVE RESCHEDULING
# ============================================================

def rebuild_schedule(
    plan,
    info,
    available_days,
    daily_hours,
    start_time,
    break_min,
):

    today = date.today()

    unfinished = plan[
        ~plan["id"].isin(st.session_state.done)
    ].copy()

    remaining_subjects = [
        {
            "Subject": name,
            "exam": details["exam"],
            "Weak topics": details["weak"],
        }
        for name, details in info.items()
        if details["exam"] > today
    ]

    if not remaining_subjects:
        return None

    last_day = max(
        s["exam"] for s in remaining_subjects
    ) - timedelta(days=1)

    if last_day < today:
        return None

    availability = get_available_dates(
        today,
        last_day,
        available_days,
        daily_hours,
    )

    if not availability:
        return None

    system = """
You are an adaptive academic planning engine.

Rebuild a student's remaining study schedule.

The student has missed or changed some study sessions.

RULES:

1. Do not repeat completed sessions.
2. Prioritize unfinished topics.
3. Prioritize weak subjects.
4. Respect exam dates.
5. Never exceed available daily study time.
6. Use 25-90 minute sessions.
7. Use revision and mock tests near exams.
8. Do not invent syllabus details.
9. Distribute work realistically.

Return ONLY JSON:

{
 "sessions": [
   {
     "date": "YYYY-MM-DD",
     "subject": "Physics",
     "topic": "Optics",
     "minutes": 60,
     "type": "Practice"
   }
 ]
}
"""

    user = f"""
TODAY: {today}

SUBJECTS:
{current_subject_context()}

UNFINISHED SESSIONS:
{unfinished[
    ['Date', 'Subject', 'Topic', 'Minutes', 'Type']
].to_json(orient='records', date_format='iso')}

AVAILABLE STUDY TIME:
{[(d.isoformat(), h) for d, h in availability]}

Rebuild the remaining schedule.
"""

    result = ai_request(
        system,
        user,
        json_mode=True,
        temperature=0.3,
    )

    raw = validate_json_list(result, "sessions")

    return clean_schedule(
        raw,
        remaining_subjects,
        availability,
        start_time,
        break_min,
    )


# ============================================================
# 12. SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="brand">Last<span>Stretch.</span></div>',
        unsafe_allow_html=True,
    )

    st.caption("YOUR PERSONAL AI STUDY COMPANION")

    st.divider()

    pages = [
        "Dashboard",
        "Study Plan",
        "AI Study Coach",
        "Practice Lab",
        "Flashcards",
        "Analytics",
    ]

    selected = st.radio(
        "NAVIGATION",
        pages,
        index=pages.index(st.session_state.page),
        label_visibility="collapsed",
        key="main_navigation",
    )

    st.session_state.page = selected

    st.divider()

    st.markdown(
        '<div class="eyebrow">POWERED BY GROQ</div>',
        unsafe_allow_html=True,
    )

    st.caption("GPT-OSS 120B")

    if st.session_state.plan is not None:

        _, _, percentage = get_stats()

        st.markdown(
            f"""
            <div class="panel">
                <div class="eyebrow">YOUR PROGRESS</div>
                <div class="big-number">{percentage}%</div>
                <div class="small-muted">Study plan completed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption("Built for the days that matter.")


# ============================================================
# 13. DASHBOARD
# ============================================================

def render_dashboard():

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">YOUR PERSONAL STUDY SYSTEM</div>
            <h1>Make every<br><em>day count.</em></h1>
            <p>
                Less guessing. Better preparation.
                An AI study companion that helps you
                understand what matters and stay on track.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    plan = st.session_state.plan

    total, completed, percentage = get_stats(plan)

    subjects = st.session_state.info

    # METRICS

    a, b, c, d = st.columns(4)

    a.metric("Subjects", len(subjects))
    b.metric("Study planned", hours_text(total))
    c.metric("Completed", hours_text(completed))
    d.metric("Progress", f"{percentage}%")

    section("01", "Your preparation")

    if not subjects:

        st.markdown(
            """
            <div class="empty-state">
                <h3>Your next chapter starts here.</h3>
                <p>
                    Add your subjects and exam dates to create
                    your personalized AI study plan.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Create my study plan",
            type="primary",
        ):
            st.session_state.page = "Study Plan"
            st.rerun()

        return

    # EXAM COUNTDOWNS

    columns = st.columns(min(len(subjects), 3))

    for i, (name, details) in enumerate(subjects.items()):

        remaining = (
            details["exam"] - date.today()
        ).days

        with columns[i % len(columns)]:

            st.markdown(
                f"""
                <div class="panel">
                    <div class="eyebrow">
                        {html.escape(name)}
                    </div>
                    <div class="big-number">
                        {remaining}
                    </div>
                    <div class="small-muted">
                        DAYS UNTIL EXAM
                    </div>
                    <p>{details['exam'].strftime('%d %B %Y')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # TODAY

    section("02", "Today's focus")

    if plan is None or plan.empty:

        st.info("Your study plan has not been generated yet.")

    else:

        today_rows = plan[
            plan["Date"] == date.today()
        ].sort_values("Start")

        if today_rows.empty:

            st.markdown(
                '<div class="empty-state">No study sessions scheduled today.</div>',
                unsafe_allow_html=True,
            )

        else:

            for _, row in today_rows.iterrows():

                session_id = row["id"]

                checked = st.checkbox(
                    f"{row['Start']}  ·  {row['Topic']}  ·  "
                    f"{row['Subject']}  ·  {row['Minutes']} min",
                    value=session_id in st.session_state.done,
                    key=f"dashboard_{session_id}",
                )

                if checked:
                    st.session_state.done.add(session_id)
                else:
                    st.session_state.done.discard(session_id)

    # AI RECOMMENDATION

    section("03", "Your AI assistant")

    st.markdown(
        """
        <div class="panel panel-accent">
            <div class="ai-indicator">AI STUDY COMPANION</div>
            <h3>Not sure what to study next?</h3>
            <p class="small-muted">
                Get personalized recommendations, understand
                difficult concepts and identify your next priority.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    prompt_columns = st.columns(3)

    prompts = [
        "What should I prioritize today?",
        "How should I revise my weakest subject?",
        "Give me a strategy for my upcoming exams.",
    ]

    for i, prompt in enumerate(prompts):

        with prompt_columns[i]:

            if st.button(
                prompt,
                key=f"dashboard_prompt_{i}",
                use_container_width=True,
            ):

                st.session_state.coach_prompt = prompt
                st.session_state.page = "AI Study Coach"
                st.rerun()

    # QUICK ACTIONS

    section("04", "Quick access")

    quick = st.columns(3)

    actions = [
        ("Build study plan", "Study Plan"),
        ("Practice questions", "Practice Lab"),
        ("Revise with flashcards", "Flashcards"),
    ]

    for i, (label, page) in enumerate(actions):

        with quick[i]:

            if st.button(
                label,
                key=f"quick_{i}",
                use_container_width=True,
            ):

                st.session_state.page = page
                st.rerun()


# ============================================================
# 14. STUDY PLAN PAGE
# ============================================================

def render_study_plan():

    st.title("Your study plan")

    st.caption(
        "Tell us what you're preparing for. AI handles the planning."
    )

    section("01", "Your subjects")

    default_subjects = pd.DataFrame([
        {
            "Subject": "Physics",
            "Exam date": date.today() + timedelta(days=14),
            "Weak topics": "Doppler effect, Optics",
        },
        {
            "Subject": "Chemistry",
            "Exam date": date.today() + timedelta(days=18),
            "Weak topics": "Organic reactions",
        },
    ])

    subjects_df = st.data_editor(
        default_subjects,
        num_rows="dynamic",
        use_container_width=True,
        key="subject_editor",
        column_config={
            "Subject": st.column_config.TextColumn(
                "Subject",
                required=True,
            ),
            "Exam date": st.column_config.DateColumn(
                "Exam date",
                min_value=date.today() + timedelta(days=1),
                required=True,
            ),
            "Weak topics": st.column_config.TextColumn(
                "Weak topics (comma separated)",
            ),
        },
    )

    # AVAILABILITY IS ONLY REQUESTED HERE.
    # NOTHING IS FIXED IN THE SIDEBAR.

    section("02", "Your available study time")

    st.write(
        "How much time can you realistically dedicate "
        "to studying on each study day?"
    )

    col1, col2 = st.columns(2)

    with col1:

        daily_hours = st.slider(
            "Hours per study day",
            min_value=0.5,
            max_value=12.0,
            value=2.0,
            step=0.5,
        )

        start_time = st.time_input(
            "Preferred starting time",
            value=datetime.strptime(
                "17:00", "%H:%M"
            ).time(),
        )

    with col2:

        study_days = st.multiselect(
            "Days you can study",
            options=[
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
            default=[
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
        )

        break_min = st.slider(
            "Break between sessions",
            0,
            30,
            10,
        )

    day_mapping = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }

    available_days = [
        day_mapping[d] for d in study_days
    ]

    st.info(
        "These settings apply to this plan only. "
        "You can change them whenever you regenerate or "
        "adapt your schedule."
    )

    if st.button(
        "Generate my personalized plan",
        type="primary",
        use_container_width=True,
    ):

        subjects = []

        for _, row in subjects_df.iterrows():

            if (
                pd.isna(row["Subject"])
                or not str(row["Subject"]).strip()
                or pd.isna(row["Exam date"])
            ):
                continue

            subjects.append({
                "Subject": str(row["Subject"]).strip(),
                "exam": pd.to_datetime(
                    row["Exam date"]
                ).date(),
                "Weak topics": (
                    ""
                    if pd.isna(row["Weak topics"])
                    else str(row["Weak topics"])
                ),
            })

        if not subjects:

            st.error("Add at least one valid subject.")

        elif len({
            s["Subject"].casefold()
            for s in subjects
        }) != len(subjects):

            st.error("Subject names must be unique.")

        elif not available_days:

            st.error("Select at least one study day.")

        else:

            today = date.today()

            last_day = max(
                s["exam"] for s in subjects
            ) - timedelta(days=1)

            if last_day < today:

                st.error("All examination dates must be in the future.")

            elif (last_day - today).days > MAX_DAYS:

                st.error(
                    f"Keep your last examination within {MAX_DAYS} days."
                )

            else:

                availability = get_available_dates(
                    today,
                    last_day,
                    available_days,
                    daily_hours,
                )

                if not availability:

                    st.error("No available study dates found.")

                else:

                    with st.spinner(
                        "AI is analyzing your subjects, "
                        "weak topics and examination dates..."
                    ):

                        try:

                            raw = generate_schedule(
                                subjects,
                                availability,
                                start_time,
                                break_min,
                            )

                            st.session_state.schedule_version += 1

                            plan, dropped = clean_schedule(
                                raw,
                                subjects,
                                availability,
                                start_time,
                                break_min,
                            )

                            if plan.empty:

                                st.error(
                                    "AI could not create a valid schedule. "
                                    "Try increasing your available hours."
                                )

                            else:

                                st.session_state.plan = plan

                                st.session_state.info = {
                                    s["Subject"]: {
                                        "exam": s["exam"],
                                        "weak": s["Weak topics"],
                                    }
                                    for s in subjects
                                }

                                st.session_state.availability = {
                                    "days": available_days,
                                    "hours": daily_hours,
                                    "start_time": start_time,
                                    "break": break_min,
                                }

                                st.session_state.done = set()

                                st.session_state.dropped = dropped

                                st.session_state.last_generation = datetime.now()

                                st.success(
                                    "Your personalized study plan is ready!"
                                )

                                st.rerun()

                        except Exception as e:

                            st.error(f"Generation failed: {e}")

    # DISPLAY CURRENT PLAN

    plan = st.session_state.plan

    if plan is None:
        return

    section("03", "Your generated schedule")

    if st.session_state.dropped:

        st.caption(
            f"{st.session_state.dropped} invalid AI-generated "
            "sessions were excluded."
        )

    st.caption(
        "Edit dates, topics, times, subjects and durations below."
    )

    edited = st.data_editor(
        plan,
        num_rows="dynamic",
        use_container_width=True,
        key=f"editable_plan_{st.session_state.schedule_version}",
        column_config={
            "id": None,
            "Date": st.column_config.DateColumn(
                "Date",
                required=True,
            ),
            "Start": st.column_config.TextColumn(
                "Start",
                required=True,
            ),
            "Minutes": st.column_config.NumberColumn(
                "Minutes",
                min_value=5,
                max_value=240,
                step=5,
                required=True,
            ),
            "Subject": st.column_config.SelectboxColumn(
                "Subject",
                options=list(st.session_state.info.keys()),
                required=True,
            ),
            "Topic": st.column_config.TextColumn(
                "Topic",
                required=True,
            ),
            "Type": st.column_config.SelectboxColumn(
                "Type",
                options=SESSION_TYPES,
            ),
        },
    )

    edited = edited.dropna(
        subset=["Date", "Minutes", "Subject"]
    ).copy()

    edited["Date"] = pd.to_datetime(
        edited["Date"]
    ).dt.date

    edited["Minutes"] = edited["Minutes"].astype(int)

    edited["Topic"] = edited["Topic"].fillna("")

    edited["Start"] = edited["Start"].fillna("")

    edited["Type"] = edited["Type"].fillna("Learn")

    if edited["id"].duplicated().any():

        edited["id"] = [
            f"edit-{st.session_state.schedule_version}-{i}"
            for i in range(len(edited))
        ]

    st.session_state.plan = edited

    valid_ids = set(edited["id"])

    st.session_state.done.intersection_update(valid_ids)

    # VALIDATION

    limits = {}

    availability = st.session_state.availability

    if availability:

        for d, h in get_available_dates(
            date.today(),
            max(
                details["exam"]
                for details in st.session_state.info.values()
            ) - timedelta(days=1),
            availability["days"],
            availability["hours"],
        ):

            limits[d] = int(h * 60)

    for d, group in edited.groupby("Date"):

        booked = int(group["Minutes"].sum())
        allowed = limits.get(d, 0)

        if booked > allowed:

            st.warning(
                f"{d}: {booked} minutes booked, "
                f"but only {allowed} minutes available."
            )

    for _, row in edited.iterrows():

        exam = st.session_state.info.get(
            row["Subject"], {}
        ).get("exam")

        if exam and row["Date"] >= exam:

            st.warning(
                f"{row['Subject']} has a session on or after "
                f"its examination date."
            )

    section("04", "Adaptive planning")

    st.write(
        "Missed sessions? Let AI reorganize your remaining workload."
    )

    if st.button(
        "Adapt my study plan",
        use_container_width=True,
    ):

        if not availability:

            st.error("Generate a study plan first.")

        else:

            with st.spinner(
                "AI is rebuilding your remaining study plan..."
            ):

                try:

                    result = rebuild_schedule(
                        edited,
                        st.session_state.info,
                        availability["days"],
                        availability["hours"],
                        availability["start_time"],
                        availability["break"],
                    )

                    if result is None or result[0].empty:

                        st.warning(
                            "No valid remaining sessions could be generated."
                        )

                    else:

                        new_plan, dropped = result

                        completed_rows = edited[
                            edited["id"].isin(
                                st.session_state.done
                            )
                        ].copy()

                        st.session_state.schedule_version += 1

                        new_plan["id"] = [
                            f"adapted-{st.session_state.schedule_version}-{i}"
                            for i in range(len(new_plan))
                        ]

                        combined = pd.concat(
                            [completed_rows, new_plan],
                            ignore_index=True,
                        )

                        st.session_state.plan = combined

                        st.session_state.dropped = dropped

                        st.rerun()

                except Exception as e:

                    st.error(f"Rescheduling failed: {e}")

    section("05", "Export your schedule")

    export = edited.copy()

    export["Completed"] = export["id"].isin(
        st.session_state.done
    )

    export = export.drop(columns=["id"])

    st.download_button(
        "Download CSV",
        export.to_csv(index=False),
        file_name="last_stretch_plan.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# 15. AI STUDY COACH PAGE
# ============================================================

def render_coach():

    st.title("AI Study Coach")

    st.caption(
        "A study partner that understands your preparation."
    )

    st.markdown(
        """
        <div class="panel panel-accent">
            <div class="ai-indicator">LAST STRETCH INTELLIGENCE</div>
            <h2>Let's figure it out.</h2>
            <p class="small-muted">
                Ask questions, understand difficult concepts,
                revise topics or get personalized study advice.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.info:

        st.info(
            "Create a study plan to give your AI coach "
            "information about your subjects and exams."
        )

    for message in st.session_state.coach_messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    initial_prompt = st.session_state.pop(
        "coach_prompt",
        None,
    )

    prompt = st.chat_input(
        "Ask anything about your studies..."
    )

    if initial_prompt and not prompt:
        prompt = initial_prompt

    if prompt:

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    answer = ask_study_coach(prompt)

                    st.markdown(answer)

                except Exception as e:

                    st.error(f"AI coach error: {e}")

    if st.session_state.coach_messages:

        if st.button("Clear conversation"):

            st.session_state.coach_messages = []

            st.rerun()


# ============================================================
# 16. PRACTICE LAB PAGE
# ============================================================

def render_practice():

    st.title("Practice Lab")

    st.caption(
        "Turn difficult topics into personalized assessments."
    )

    section("01", "Build your quiz")

    subjects = subject_names()

    col1, col2 = st.columns(2)

    with col1:

        subject = st.selectbox(
            "Subject",
            subjects if subjects else ["General"],
        )

        topic = st.text_input(
            "Topic",
            placeholder="e.g. Newton's laws, Organic chemistry",
        )

    with col2:

        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard", "Exam level"],
        )

        count = st.select_slider(
            "Number of questions",
            options=[3, 5, 10, 15],
            value=5,
        )

    if st.button(
        "Generate AI quiz",
        type="primary",
        use_container_width=True,
    ):

        if not topic.strip():

            st.warning("Enter a topic first.")

        else:

            with st.spinner(
                "AI is creating your questions..."
            ):

                try:

                    quiz = generate_quiz(
                        subject,
                        topic,
                        difficulty,
                        count,
                    )

                    if not quiz:

                        st.error("No valid questions were generated.")

                    else:

                        st.session_state.quiz = quiz

                        st.session_state.quiz_version += 1

                        st.session_state.quiz_answers = {}

                        st.session_state.quiz_submitted = False

                        st.session_state.quiz_score = None

                        st.rerun()

                except Exception as e:

                    st.error(f"Quiz generation failed: {e}")

    quiz = st.session_state.quiz

    if not quiz:
        return

    section("02", "Your assessment")

    st.caption(
        f"{len(quiz)} questions · "
        "Choose the best answer for each."
    )

    answers = {}

    for i, question in enumerate(quiz):

        st.markdown(
            f"### {i + 1:02d}. {question['question']}"
        )

        options = question["options"]

        selected = st.radio(
            f"Answer {i + 1}",
            options=list(options.keys()),
            format_func=lambda x, opts=options: (
                f"{x}. {opts[x]}"
            ),
            index=None,
            key=f"quiz_{st.session_state.quiz_version}_{i}",
            disabled=st.session_state.quiz_submitted,
        )

        answers[i] = selected

        st.divider()

    if not st.session_state.quiz_submitted:

        if st.button(
            "Submit answers",
            type="primary",
            use_container_width=True,
        ):

            if any(v is None for v in answers.values()):

                st.warning("Answer every question before submitting.")

            else:

                score = sum(
                    answers[i] == question["answer"].upper()
                    for i, question in enumerate(quiz)
                )

                st.session_state.quiz_answers = answers

                st.session_state.quiz_score = score

                st.session_state.quiz_submitted = True

                st.rerun()

    if st.session_state.quiz_submitted:

        score = st.session_state.quiz_score

        percentage = round(
            score / len(quiz) * 100
        )

        st.markdown(
            f"""
            <div class="panel panel-accent">
                <div class="eyebrow">YOUR RESULT</div>
                <div class="big-number">
                    {score}/{len(quiz)}
                </div>
                <h3>{percentage}% correct</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        section("03", "Answer explanations")

        for i, question in enumerate(quiz):

            correct = question["answer"].upper()

            chosen = st.session_state.quiz_answers[i]

            if chosen == correct:

                st.success(f"Question {i + 1}: Correct")

            else:

                st.error(
                    f"Question {i + 1}: Incorrect. "
                    f"Correct answer: {correct}"
                )

            st.write(question["explanation"])

        if st.button(
            "Create another quiz",
            use_container_width=True,
        ):

            st.session_state.quiz = []

            st.session_state.quiz_submitted = False

            st.session_state.quiz_answers = {}

            st.rerun()


# ============================================================
# 17. FLASHCARDS PAGE
# ============================================================

def render_flashcards():

    st.title("Revision Centre")

    st.caption(
        "Learn through active recall, not passive reading."
    )

    section("01", "Generate flashcards")

    subjects = subject_names()

    col1, col2 = st.columns(2)

    with col1:

        subject = st.selectbox(
            "Subject",
            subjects if subjects else ["General"],
            key="flash_subject",
        )

        topic = st.text_input(
            "Topic to revise",
            placeholder="Enter your topic",
        )

    with col2:

        count = st.select_slider(
            "Number of cards",
            options=[5, 10, 15, 20],
            value=10,
        )

        st.markdown(
            '<div class="small-muted">'
            'AI-generated active recall cards'
            '</div>',
            unsafe_allow_html=True,
        )

    if st.button(
        "Generate flashcards",
        type="primary",
        use_container_width=True,
    ):

        if not topic.strip():

            st.warning("Enter a topic.")

        else:

            with st.spinner(
                "Creating your revision cards..."
            ):

                try:

                    cards = generate_flashcards(
                        subject,
                        topic,
                        count,
                    )

                    st.session_state.flashcards = cards

                    st.session_state.flashcard_version += 1

                    if not cards:
                        st.error("No flashcards were generated.")
                    else:
                        st.rerun()

                except Exception as e:

                    st.error(f"Flashcard generation failed: {e}")

    cards = st.session_state.flashcards

    if not cards:
        return

    section("02", "Your revision cards")

    st.caption(
        "Try answering each question before revealing its answer."
    )

    for i, card in enumerate(cards):

        with st.expander(
            f"FLASHCARD {i + 1:02d}  ·  {card['front']}"
        ):

            st.markdown(
                f"**QUESTION**\n\n{card['front']}"
            )

            st.divider()

            if st.button(
                "Reveal answer",
                key=f"reveal_{st.session_state.flashcard_version}_{i}",
            ):

                st.session_state[
                    f"revealed_{st.session_state.flashcard_version}_{i}"
                ] = True

            if st.session_state.get(
                f"revealed_{st.session_state.flashcard_version}_{i}",
                False,
            ):

                st.markdown(
                    f"**ANSWER**\n\n{card['back']}"
                )

    st.download_button(
        "Export flashcards",
        pd.DataFrame(cards).to_csv(index=False),
        file_name="last_stretch_flashcards.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# 18. ANALYTICS PAGE
# ============================================================

def render_analytics():

    st.title("Study analytics")

    st.caption(
        "Understand your study habits and identify where to improve."
    )

    plan = st.session_state.plan

    if plan is None or plan.empty:

        st.markdown(
            """
            <div class="empty-state">
                <h3>Your analytics will appear here.</h3>
                <p>Generate a study plan and complete sessions to get started.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    total, completed, percentage = get_stats(plan)

    a, b, c = st.columns(3)

    a.metric("Planned time", hours_text(total))

    b.metric("Completed time", hours_text(completed))

    c.metric("Completion rate", f"{percentage}%")

    st.progress(percentage / 100)

    data = plan.copy()

    data["Completed"] = data["id"].isin(
        st.session_state.done
    )

    # SUBJECT ANALYSIS

    section("01", "Subject breakdown")

    breakdown = []

    for subject, group in data.groupby("Subject"):

        planned = int(group["Minutes"].sum())

        done = int(
            group.loc[
                group["Completed"],
                "Minutes"
            ].sum()
        )

        breakdown.append({
            "Subject": subject,
            "Planned (min)": planned,
            "Completed (min)": done,
            "Completion (%)": (
                round(done / planned * 100, 1)
                if planned else 0
            ),
        })

    breakdown_df = pd.DataFrame(breakdown)

    st.dataframe(
        breakdown_df,
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(
        breakdown_df.set_index("Subject")[
            ["Planned (min)", "Completed (min)"]
        ]
    )

    # DAILY ANALYSIS

    section("02", "Daily activity")

    daily = []

    for d, group in data.groupby("Date"):

        daily.append({
            "Date": str(d),
            "Planned": int(group["Minutes"].sum()),
            "Completed": int(
                group.loc[
                    group["Completed"],
                    "Minutes"
                ].sum()
            ),
        })

    daily_df = pd.DataFrame(daily)

    if not daily_df.empty:

        st.line_chart(
            daily_df.set_index("Date")[
                ["Planned", "Completed"]
            ]
        )

    # SESSION TYPES

    section("03", "Study methods")

    type_data = (
        data.groupby("Type")["Minutes"]
        .sum()
        .reset_index()
    )

    st.bar_chart(
        type_data.set_index("Type")
    )

    # AI ANALYSIS

    section("04", "AI performance report")

    st.markdown(
        """
        <div class="panel">
            <div class="ai-indicator">AI-POWERED INSIGHTS</div>
            <h3>Go beyond the numbers.</h3>
            <p class="small-muted">
                Let AI analyze your completed sessions,
                subject allocation and study consistency.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Generate my AI performance report",
        type="primary",
        use_container_width=True,
    ):

        with st.spinner(
            "Analyzing your study performance..."
        ):

            try:

                report = generate_progress_analysis(plan)

                st.session_state.analytics_report = report

            except Exception as e:

                st.error(f"Analysis failed: {e}")

    if st.session_state.analytics_report:

        st.markdown(
            st.session_state.analytics_report
        )


# ============================================================
# 19. PAGE ROUTER
# ============================================================

page = st.session_state.page

if page == "Dashboard":

    render_dashboard()

elif page == "Study Plan":

    render_study_plan()

elif page == "AI Study Coach":

    render_coach()

elif page == "Practice Lab":

    render_practice()

elif page == "Flashcards":

    render_flashcards()

elif page == "Analytics":

    render_analytics()


# ============================================================
# 20. FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center;padding:20px;">
        <div class="eyebrow">LAST STRETCH</div>
        <p style="color:#929188;font-size:.8rem;">
            Study smarter. Show up. Make it count.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
