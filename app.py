
import os
import json
import html
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st
from groq import Groq

# =========================================================
# CONFIGURATION
# =========================================================

MODEL = "openai/gpt-oss-120b"

SESSION_TYPES = ["Learn", "Practice", "Revise", "Mock test"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MAX_DAYS = 45

PALETTE = [
    "#FF5A3C", "#3FB8AF", "#F2B94B",
    "#7B8CFF", "#C77DFF", "#8FCB4A"
]

st.set_page_config(
    page_title="Last Stretch",
    page_icon="🟥",
    layout="wide"
)

# =========================================================
# DESIGN
# =========================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    --bg: #121110;
    --card: #1C1A17;
    --ink: #F2EDE4;
    --line: #F2EDE4;
    --sh: #34302A;
    --red: #FF5A3C;
    --mute: #9A9488;
    --mono: 'JetBrains Mono', monospace;
    --serif: 'Fraunces', serif;
}

.stApp {
    background: var(--bg);
    color: var(--ink);
    font-family: 'Instrument Sans', sans-serif;
}

.stApp label p,
[data-testid="stMarkdownContainer"] p {
    color: var(--ink);
}

[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer, [data-testid="stToolbar"] {
    visibility: hidden;
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    background: var(--card);
    border-right: 2px solid var(--line);
}

[data-testid="stSidebar"] * {
    color: var(--ink);
}

[data-baseweb="input"],
[data-baseweb="select"] > div {
    background: var(--card) !important;
    border-radius: 0 !important;
    border: 1px solid var(--line) !important;
}

input, textarea {
    color: var(--ink) !important;
}

.stButton > button,
.stDownloadButton > button {
    border: 2px solid var(--line);
    border-radius: 0;
    background: var(--card);
    color: var(--ink);
    font-family: var(--mono);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .05em;
    box-shadow: 4px 4px 0 var(--sh);
    transition: .15s;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translate(2px, 2px);
    box-shadow: 2px 2px 0 var(--sh);
    border-color: var(--red);
}

button[kind="primary"] {
    background: var(--red) !important;
    color: white !important;
    border-color: var(--red) !important;
}

.mast {
    border-bottom: 4px solid var(--line);
    padding-bottom: 20px;
    margin-bottom: 25px;
}

.kicker {
    font-family: var(--mono);
    font-size: .75rem;
    letter-spacing: .2em;
    color: var(--mute);
}

.mast h1 {
    font-family: var(--serif);
    font-size: clamp(3.5rem, 9vw, 6.5rem);
    line-height: .9;
    margin: .4rem 0;
    letter-spacing: -.04em;
    color: var(--ink);
}

.mast h1 em {
    color: var(--red);
}

.mast p {
    font-size: 1.05rem;
    max-width: 600px;
}

.sec {
    display: flex;
    justify-content: space-between;
    font-family: var(--mono);
    font-size: .75rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    border-bottom: 2px solid var(--line);
    padding-bottom: 7px;
    margin: 2rem 0 1rem;
}

.sec span:last-child {
    color: var(--mute);
}

.metric-card {
    background: var(--card);
    border: 2px solid var(--line);
    box-shadow: 5px 5px 0 var(--sh);
    padding: 18px;
    min-height: 125px;
}

.metric-label {
    font-family: var(--mono);
    font-size: .7rem;
    color: var(--mute);
    text-transform: uppercase;
    letter-spacing: .08em;
}

.metric-number {
    font-family: var(--serif);
    font-size: 2.8rem;
    font-weight: 800;
    margin-top: 8px;
}

.ai-card {
    background: var(--card);
    border: 1px solid var(--line);
    padding: 18px;
    margin-bottom: 12px;
}

.ai-label {
    font-family: var(--mono);
    color: var(--red);
    font-size: .72rem;
    letter-spacing: .12em;
}

.chat-hint {
    color: var(--mute);
    font-size: .85rem;
}

.stProgress > div > div > div {
    background: var(--red);
}

[data-testid="stMetric"] {
    background: var(--card);
    border: 1px solid var(--line);
    padding: 15px;
}

[data-testid="stMetricLabel"] {
    color: var(--mute);
}

[data-testid="stMetricValue"] {
    color: var(--ink);
    font-family: var(--serif);
}

.stTabs [data-baseweb="tab"] {
    font-family: var(--mono);
    text-transform: uppercase;
    font-size: .75rem;
}

.stTabs [aria-selected="true"] {
    color: var(--red) !important;
}

div[data-testid="stExpander"] {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 0;
}

.stAlert {
    border-radius: 0;
}

@keyframes rise {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# =========================================================
# API CONNECTION
# =========================================================

def get_api_key():
    """Get the API key from Streamlit Secrets or environment."""

    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY", "")


@st.cache_resource
def get_client(api_key):
    return Groq(api_key=api_key)


def get_ai_client():
    key = get_api_key()

    if not key:
        st.error(
            "Groq API key is not configured. "
            "Add GROQ_API_KEY to Streamlit Secrets."
        )
        st.stop()

    return get_client(key)


# =========================================================
# AI UTILITIES
# =========================================================

def ai_request(system, user, json_mode=False, temperature=0.4):
    client = get_ai_client()

    args = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        "temperature": temperature,
        "max_tokens": 8000
    }

    if json_mode:
        args["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**args)

    content = response.choices[0].message.content

    if json_mode:
        return json.loads(content)

    return content


def safe_list(data, key):
    result = data.get(key, [])
    return result if isinstance(result, list) else []


# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "plan": None,
    "info": {},
    "avail": [],
    "done": set(),
    "coach_messages": [],
    "quiz": None,
    "flashcards": [],
    "ver": 0,
    "dropped": 0
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def hrs(minutes):
    return f"{minutes / 60:.1f}h"


def section(number, title, right=""):
    st.markdown(
        f'<div class="sec"><span>{number} — {html.escape(title)}</span>'
        f'<span>{html.escape(right)}</span></div>',
        unsafe_allow_html=True
    )


def build_availability(start, end, hours):
    result = []
    current = start

    while current <= end:
        available = hours[current.weekday()]

        if available > 0:
            result.append((current, available))

        current += timedelta(days=1)

    return result


def subject_context():
    info = st.session_state.info

    return "\n".join(
        f"{name}: Exam {details['exam']}, "
        f"Weak topics: {details['weak'] or 'Not specified'}"
        for name, details in info.items()
    )


# =========================================================
# AI STUDY SCHEDULE
# =========================================================

def generate_schedule(subjects, availability, start_time, break_min):
    subject_lines = "\n".join(
        f"- {s['Subject']} | Exam: {s['exam']} | "
        f"Weak topics: {s['Weak topics'] or 'None specified'}"
        for s in subjects
    )

    available_lines = "\n".join(
        f"{d.isoformat()} ({DAYS[d.weekday()]}): {h} hours"
        for d, h in availability
    )

    system = """
You are Last Stretch, an expert AI academic planner.

Create a realistic, personalized day-by-day study schedule.

RULES:
1. Prioritize weak topics.
2. Give weak topics spaced repetition.
3. Prioritize subjects with closer exams.
4. Mix subjects throughout the week.
5. Each session must be 25-90 minutes.
6. Never exceed the available daily hours.
7. Never schedule a subject on or after its exam.
8. Use the final 2-3 available days before an exam for revision or mock tests.
9. Use specific topics, not generic subject names.
10. Include Learn, Practice, Revise and Mock test sessions where appropriate.
11. Distribute sessions sensibly.
12. Do not invent topics when a subject's syllabus is unknown. Use its supplied weak topics or clearly labeled general practice.

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

SUBJECTS:
{subject_lines}

AVAILABLE STUDY TIME:
{available_lines}

Create the complete study plan.
"""

    result = ai_request(system, user, json_mode=True)

    return safe_list(result, "sessions")


def clean_schedule(raw, subjects, availability, start_time, break_min):
    exam_dates = {s["Subject"]: s["exam"] for s in subjects}
    available_minutes = {d: int(h * 60) for d, h in availability}

    used = {}
    rows = []
    dropped = 0

    for session in sorted(raw, key=lambda x: str(x.get("date", ""))):
        try:
            d = date.fromisoformat(session["date"])
            minutes = int(session["minutes"])
        except (ValueError, TypeError, KeyError):
            dropped += 1
            continue

        subject = session.get("subject", "").strip()

        if (
            subject not in exam_dates
            or d not in available_minutes
            or d >= exam_dates[subject]
            or not 25 <= minutes <= 90
        ):
            dropped += 1
            continue

        if used.get(d, 0) + minutes > available_minutes[d]:
            dropped += 1
            continue

        used[d] = used.get(d, 0) + minutes

        session_type = session.get("type", "Learn")

        if session_type not in SESSION_TYPES:
            session_type = "Learn"

        topic = str(session.get("topic", "")).strip()

        rows.append({
            "Date": d,
            "Subject": subject,
            "Topic": topic or subject,
            "Minutes": minutes,
            "Type": session_type
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

        row["id"] = f"v{st.session_state.ver + 1}-{i}"

    columns = [
        "Date", "Start", "Minutes",
        "Subject", "Topic", "Type", "id"
    ]

    return pd.DataFrame(rows, columns=columns), dropped


# =========================================================
# DASHBOARD HELPERS
# =========================================================

def get_plan_stats(plan):
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


# =========================================================
# AI STUDY COACH
# =========================================================

def study_coach(question):
    context = subject_context()

    plan = st.session_state.plan

    total, completed, percentage = get_plan_stats(plan)

    progress = f"""
TOTAL PLANNED: {hrs(total)}
COMPLETED: {hrs(completed)}
PROGRESS: {percentage}%

COMPLETED SESSION IDS:
{list(st.session_state.done)}
"""

    system = f"""
You are Last Stretch AI Study Coach.

You are a supportive, intelligent academic mentor.

Help students:
- Understand difficult academic concepts.
- Plan their revision.
- Improve weak subjects.
- Prepare for upcoming exams.
- Build consistent study habits.
- Understand their progress.

Use clear, student-friendly language.

Be specific and practical.
Never pretend to know a syllabus that has not been provided.
Do not make unsupported claims about exam readiness.

STUDENT SUBJECTS:
{context}

STUDENT PROGRESS:
{progress}
"""

    history = st.session_state.coach_messages[-10:]

    messages = [{"role": "system", "content": system}]

    for item in history:
        messages.append(item)

    messages.append({
        "role": "user",
        "content": question
    })

    client = get_ai_client()

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.6,
        max_tokens=3000
    )

    answer = response.choices[0].message.content

    st.session_state.coach_messages.extend([
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer}
    ])

    st.session_state.coach_messages = (
        st.session_state.coach_messages[-20:]
    )

    return answer


# =========================================================
# AI QUIZ GENERATOR
# =========================================================

def generate_quiz(subject, topic, difficulty, count):
    system = """
You are an expert academic assessment designer.

Create educational questions that test actual understanding.

Questions must be clear, accurate and appropriate to the selected difficulty.

Return ONLY valid JSON:

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
Number of questions: {count}

Create original questions.
Make sure each question has exactly four options.
"""

    result = ai_request(system, user, json_mode=True)

    return safe_list(result, "questions")


# =========================================================
# AI FLASHCARDS
# =========================================================

def generate_flashcards(subject, topic, count):
    system = """
You are an expert educational flashcard creator.

Create useful flashcards for active recall.

Each card must have:
- A concise question or concept on the front.
- An accurate and understandable answer on the back.

Avoid vague questions.

Return ONLY valid JSON:

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
Number of flashcards: {count}

Create useful revision cards.
"""

    result = ai_request(system, user, json_mode=True)

    return safe_list(result, "flashcards")


# =========================================================
# AI PROGRESS ANALYSIS
# =========================================================

def analyze_progress(plan):
    total, completed, percentage = get_plan_stats(plan)

    summary = plan.copy()

    summary["Completed"] = summary["id"].isin(
        st.session_state.done
    )

    subject_stats = []

    for subject, group in summary.groupby("Subject"):
        planned = int(group["Minutes"].sum())
        done = int(group.loc[group["Completed"], "Minutes"].sum())

        subject_stats.append({
            "subject": subject,
            "planned_minutes": planned,
            "completed_minutes": done
        })

    system = """
You are an academic performance analyst.

Analyze the student's actual study statistics.

Identify:
1. Subjects receiving insufficient attention.
2. Completion patterns.
3. Possible scheduling problems.
4. Practical recommendations.
5. Three specific next actions.

Do not invent performance or test scores.
Do not claim the student has mastered a topic simply because a session was completed.

Be honest and constructive.
"""

    user = f"""
Overall completion: {percentage}%

Planned study time: {total} minutes.
Completed study time: {completed} minutes.

SUBJECT BREAKDOWN:
{json.dumps(subject_stats, indent=2)}

Give a personalized progress analysis.
"""

    return ai_request(system, user)


# =========================================================
# ADAPTIVE RESCHEDULING
# =========================================================

def adaptive_reschedule(plan, info, hours, start_time, break_min):
    today = date.today()

    unfinished = plan[
        ~plan["id"].isin(st.session_state.done)
    ].copy()

    remaining_subjects = [
        {
            "Subject": name,
            "exam": details["exam"],
            "Weak topics": details["weak"]
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

    availability = build_availability(
        today, last_day, hours
    )

    if not availability:
        return None

    previous = unfinished[
        ["Date", "Subject", "Topic", "Minutes", "Type"]
    ].copy()

    system = """
You are an adaptive study planner.

Rebuild a study schedule based on the remaining unfinished work.

Rules:
- Completed sessions must not be scheduled again.
- Prioritize unfinished topics.
- Respect exam dates.
- Use available hours.
- Each session must be 25-90 minutes.
- Never schedule a subject on or after its exam.
- Use revision and mock tests near exams.
- Preserve the student's original learning priorities.

Return ONLY valid JSON:

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
{subject_context()}

UNFINISHED SESSIONS:
{previous.to_json(orient="records", date_format="iso")}

AVAILABLE TIME:
{[(d.isoformat(), h) for d, h in availability]}

Rebuild the remaining schedule.
"""

    result = ai_request(system, user, json_mode=True)

    raw = safe_list(result, "sessions")

    return clean_schedule(
        raw,
        remaining_subjects,
        availability,
        start_time,
        break_min
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("### LAST STRETCH")
    st.caption("YOUR PERSONAL AI STUDY SYSTEM")

    st.divider()

    st.markdown("### Your weekly availability")

    st.caption(
        "Set the hours you can realistically study each day."
    )

    defaults = [2, 2, 2, 2, 2, 4, 4]

    hours = {}

    for i, day in enumerate(DAYS):
        hours[i] = st.number_input(
            day,
            min_value=0.0,
            max_value=12.0,
            value=float(defaults[i]),
            step=0.5,
            key=f"hours_{i}"
        )

    st.divider()

    start_time = st.time_input(
        "Daily start time",
        value=datetime.strptime(
            "17:00", "%H:%M"
        ).time()
    )

    break_min = st.slider(
        "Break between sessions",
        0, 30, 10
    )

    st.divider()

    st.caption("POWERED BY GROQ")
    st.caption("AI MODEL · GPT-OSS 120B")


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="mast">
        <div class="kicker">
            EXAM SEASON · YOUR AI STUDY COMPANION
        </div>
        <h1>Last<br><em>Stretch.</em></h1>
        <p>
            Your exams aren't going to prepare themselves.
            Plan smarter, understand better, and make
            every study session count.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MAIN TABS
# =========================================================

tabs = st.tabs([
    "01 · Dashboard",
    "02 · Study Coach",
    "03 · Practice Lab",
    "04 · Flashcards",
    "05 · Analytics"
])


# =========================================================
# TAB 1: DASHBOARD
# =========================================================

with tabs[0]:

    section("01", "Your subjects")

    default_df = pd.DataFrame([
        {
            "Subject": "Physics",
            "Exam date": date.today() + timedelta(days=14),
            "Weak topics": "Doppler effect, Optics"
        },
        {
            "Subject": "Chemistry",
            "Exam date": date.today() + timedelta(days=18),
            "Weak topics": "Organic reactions"
        }
    ])

    subjects_df = st.data_editor(
        default_df,
        num_rows="dynamic",
        use_container_width=True,
        key="subjects_editor",
        column_config={
            "Subject": st.column_config.TextColumn(
                "Subject",
                required=True
            ),
            "Exam date": st.column_config.DateColumn(
                "Exam date",
                min_value=date.today() + timedelta(days=1),
                required=True
            ),
            "Weak topics": st.column_config.TextColumn(
                "Weak topics (comma separated)"
            )
        }
    )

    if st.button(
        "Generate my AI study plan",
        type="primary",
        use_container_width=True
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
                )
            })

        if not subjects:
            st.error("Add at least one valid subject.")

        elif len({
            s["Subject"] for s in subjects
        }) != len(subjects):
            st.error("Subject names must be unique.")

        else:
            last_day = max(
                s["exam"] for s in subjects
            ) - timedelta(days=1)

            today = date.today()

            if last_day < today:
                st.error("All exams must be in the future.")

            elif (last_day - today).days > MAX_DAYS:
                st.error(
                    f"Keep your last exam within {MAX_DAYS} days."
                )

            else:
                availability = build_availability(
                    today, last_day, hours
                )

                if not availability:
                    st.error("You have no available study hours.")

                else:
                    with st.spinner(
                        "AI is analyzing your subjects and building your plan..."
                    ):
                        try:
                            raw = generate_schedule(
                                subjects,
                                availability,
                                start_time,
                                break_min
                            )

                            st.session_state.ver += 1

                            plan, dropped = clean_schedule(
                                raw,
                                subjects,
                                availability,
                                start_time,
                                break_min
                            )

                            if plan.empty:
                                st.error(
                                    "The AI could not generate a valid schedule. "
                                    "Try again or check your available hours."
                                )

                            else:
                                st.session_state.plan = plan
                                st.session_state.info = {
                                    s["Subject"]: {
                                        "exam": s["exam"],
                                        "weak": s["Weak topics"]
                                    }
                                    for s in subjects
                                }

                                st.session_state.avail = availability
                                st.session_state.done = set()
                                st.session_state.dropped = dropped

                                st.success(
                                    "Your personalized study plan is ready!"
                                )

                        except Exception as e:
                            st.error(f"Schedule generation failed: {e}")

    # DISPLAY GENERATED PLAN

    if st.session_state.plan is not None:

        plan = st.session_state.plan.copy()

        plan_editor = st.data_editor(
            plan,
            num_rows="dynamic",
            use_container_width=True,
            key=f"plan_editor_{st.session_state.ver}",
            column_config={
                "id": None,
                "Date": st.column_config.DateColumn(
                    "Date",
                    required=True
                ),
                "Start": st.column_config.TextColumn(
                    "Start (HH:MM)"
                ),
                "Minutes": st.column_config.NumberColumn(
                    "Minutes",
                    min_value=5,
                    max_value=240,
                    step=5
                ),
                "Subject": st.column_config.SelectboxColumn(
                    "Subject",
                    options=list(st.session_state.info.keys())
                ),
                "Type": st.column_config.SelectboxColumn(
                    "Type",
                    options=SESSION_TYPES
                )
            }
        )

        plan_editor = plan_editor.dropna(
            subset=["Date", "Minutes", "Subject"]
        ).copy()

        plan_editor["Date"] = pd.to_datetime(
            plan_editor["Date"]
        ).dt.date

        plan_editor["Minutes"] = plan_editor["Minutes"].astype(int)

        plan_editor["Topic"] = (
            plan_editor["Topic"].fillna("")
        )

        plan_editor["Start"] = (
            plan_editor["Start"].fillna("17:00")
        )

        plan_editor["Type"] = (
            plan_editor["Type"].fillna("Learn")
        )

        original_ids = set(plan["id"])

        for i, index in enumerate(plan_editor.index):
            existing = plan_editor.at[index, "id"]

            if not isinstance(existing, str) or not existing:
                plan_editor.at[index, "id"] = (
                    f"v{st.session_state.ver}-edit-{i}"
                )

        if not plan_editor["id"].is_unique:
            plan_editor["id"] = [
                f"v{st.session_state.ver}-row-{i}"
                for i in range(len(plan_editor))
            ]

        # Save edits while retaining only valid completion IDs.
        st.session_state.plan = plan_editor

        valid_ids = set(plan_editor["id"])
        st.session_state.done.intersection_update(valid_ids)

        section(
            "02",
            "Today's mission",
            date.today().strftime("%A · %d %B")
        )

        today_rows = plan_editor[
            plan_editor["Date"] == date.today()
        ].sort_values("Start")

        if today_rows.empty:
            st.info("No sessions scheduled for today.")

        else:
            for _, row in today_rows.iterrows():

                session_id = row["id"]

                checked = st.checkbox(
                    f"{row['Start']} · {row['Topic']} "
                    f"— {row['Subject']} · {row['Minutes']} min",
                    value=session_id in st.session_state.done,
                    key=f"done_{session_id}"
                )

                if checked:
                    st.session_state.done.add(session_id)
                else:
                    st.session_state.done.discard(session_id)

            if all(
                row["id"] in st.session_state.done
                for _, row in today_rows.iterrows()
            ):
                st.success("All today's sessions completed!")

        # Refresh completion data after today's checkboxes.
        total, completed, percentage = get_plan_stats(plan_editor)

        section("03", "Your progress")

        a, b, c = st.columns(3)

        a.metric("Planned", hrs(total))
        b.metric("Completed", hrs(completed))
        c.metric("Progress", f"{percentage}%")

        st.progress(percentage / 100)

        section("04", "Upcoming exams")

        today = date.today()

        for name, details in st.session_state.info.items():

            remaining = (details["exam"] - today).days

            st.markdown(
                f"""
                <div class="ai-card">
                    <div class="ai-label">
                        {html.escape(name.upper())}
                    </div>
                    <h2>{remaining} DAYS LEFT</h2>
                    <p>Exam date: {details['exam']}</p>
                    <p>
                        Weak topics:
                        {html.escape(details['weak'] or 'Not specified')}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        section("05", "Adaptive planning")

        st.write(
            "Missed sessions? Let AI rebuild the remaining schedule "
            "around your current progress."
        )

        if st.button(
            "Rebuild my remaining schedule",
            use_container_width=True
        ):

            with st.spinner("AI is reorganizing your remaining sessions..."):

                try:
                    result = adaptive_reschedule(
                        plan_editor,
                        st.session_state.info,
                        hours,
                        start_time,
                        break_min
                    )

                    if result is None or result[0].empty:
                        st.warning(
                            "No valid remaining sessions could be generated."
                        )

                    else:
                        new_plan, dropped = result

                        completed_rows = plan_editor[
                            plan_editor["id"].isin(
                                st.session_state.done
                            )
                        ].copy()

                        st.session_state.ver += 1

                        new_plan["id"] = [
                            f"v{st.session_state.ver}-new-{i}"
                            for i in range(len(new_plan))
                        ]

                        combined = pd.concat(
                            [completed_rows, new_plan],
                            ignore_index=True
                        )

                        st.session_state.plan = combined
                        st.session_state.dropped = dropped

                        st.rerun()

                except Exception as e:
                    st.error(f"Rescheduling failed: {e}")

        section("06", "Export")

        export = plan_editor.copy()

        export["Done"] = export["id"].isin(
            st.session_state.done
        )

        export = export.drop(columns=["id"])

        st.download_button(
            "Download study plan CSV",
            data=export.to_csv(index=False),
            file_name="last_stretch_study_plan.csv",
            mime="text/csv",
            use_container_width=True
        )


# =========================================================
# TAB 2: AI STUDY COACH
# =========================================================

with tabs[1]:

    section("01", "Your AI study coach")

    st.markdown(
        """
        <div class="ai-card">
            <div class="ai-label">LAST STRETCH INTELLIGENCE</div>
            <h2>Think it through. Learn it properly.</h2>
            <p>
                Ask questions, get explanations, work through
                difficult concepts and receive personalized
                study recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.info:
        st.info("Generate a study plan first to personalize your coach.")

    for message in st.session_state.coach_messages:

        with st.chat_message(
            message["role"]
        ):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Ask your study coach anything..."
    )

    if prompt:

        st.session_state.coach_messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        # Remove the newly added message before calling the function,
        # because study_coach appends both messages itself.
        st.session_state.coach_messages.pop()

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:
                    answer = study_coach(prompt)
                    st.markdown(answer)

                except Exception as e:
                    st.error(f"Coach error: {e}")


# =========================================================
# TAB 3: PRACTICE LAB
# =========================================================

with tabs[2]:

    section("01", "AI practice lab")

    st.write(
        "Turn your weak topics into original practice questions."
    )

    subject_options = list(
        st.session_state.info.keys()
    )

    subject = st.selectbox(
        "Select subject",
        subject_options if subject_options else ["General"]
    )

    topic = st.text_input(
        "Topic",
        placeholder="e.g. Doppler effect, Organic chemistry..."
    )

    col1, col2 = st.columns(2)

    with col1:
        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard", "Exam level"]
        )

    with col2:
        count = st.select_slider(
            "Number of questions",
            options=[3, 5, 10, 15],
            value=5
        )

    if st.button(
        "Generate AI quiz",
        type="primary",
        use_container_width=True
    ):

        if not topic.strip():
            st.warning("Enter a topic first.")

        else:

            with st.spinner("Creating your quiz..."):

                try:
                    st.session_state.quiz = generate_quiz(
                        subject,
                        topic,
                        difficulty,
                        count
                    )

                    st.session_state.quiz_answers = {}

                except Exception as e:
                    st.error(f"Quiz generation failed: {e}")

    quiz = st.session_state.quiz

    if quiz:

        section("02", "Your questions")

        selected = {}

        for i, question in enumerate(quiz):

            st.markdown(
                f"### Question {i + 1}"
            )

            st.write(question["question"])

            options = question.get("options", {})

            labels = [
                f"{key}. {value}"
                for key, value in options.items()
            ]

            selected[i] = st.radio(
                f"Choose your answer for question {i + 1}",
                labels,
                index=None,
                key=f"quiz_answer_{st.session_state.ver}_{i}"
            )

            st.divider()

        if st.button(
            "Submit my answers",
            type="primary",
            use_container_width=True
        ):

            score = 0

            for i, question in enumerate(quiz):

                chosen = selected.get(i)

                correct = question["answer"].strip().upper()

                if chosen and chosen.split(".")[0] == correct:
                    score += 1

            st.session_state.quiz_score = score
            st.session_state.quiz_submitted = True

        if st.session_state.get("quiz_submitted", False):

            score = st.session_state.quiz_score

            st.success(
                f"You scored {score}/{len(quiz)} "
                f"({round(score / len(quiz) * 100)}%)."
            )

            for i, question in enumerate(quiz):

                answer = question["answer"].upper()
                explanation = question.get("explanation", "")

                st.markdown(f"**Question {i + 1}**")

                st.write(
                    f"Correct answer: {answer}. "
                    f"{question['options'].get(answer, '')}"
                )

                st.info(explanation)

    st.caption(
        "Questions are AI-generated. Review explanations and verify "
        "important syllabus-specific material."
    )


# =========================================================
# TAB 4: FLASHCARDS
# =========================================================

with tabs[3]:

    section("01", "AI revision centre")

    st.write(
        "Create active-recall flashcards for your most difficult topics."
    )

    flash_subject = st.selectbox(
        "Subject",
        subject_options if subject_options else ["General"],
        key="flash_subject"
    )

    flash_topic = st.text_input(
        "Revision topic",
        placeholder="Enter a topic to revise",
        key="flash_topic"
    )

    flash_count = st.select_slider(
        "Number of flashcards",
        options=[5, 10, 15, 20],
        value=10
    )

    if st.button(
        "Generate flashcards",
        type="primary",
        use_container_width=True
    ):

        if not flash_topic.strip():
            st.warning("Enter a topic.")

        else:

            with st.spinner("Creating your revision cards..."):

                try:
                    st.session_state.flashcards = generate_flashcards(
                        flash_subject,
                        flash_topic,
                        flash_count
                    )

                except Exception as e:
                    st.error(f"Flashcard generation failed: {e}")

    if st.session_state.flashcards:

        section("02", "Your flashcards")

        st.caption(
            "Try answering each question before revealing its answer."
        )

        for i, card in enumerate(
            st.session_state.flashcards
        ):

            with st.expander(
                f"CARD {i + 1:02d} · {card['front']}"
            ):

                st.markdown(
                    f"**QUESTION**\n\n{card['front']}"
                )

                st.divider()

                st.markdown(
                    f"**ANSWER**\n\n{card['back']}"
                )

        flash_export = pd.DataFrame(
            st.session_state.flashcards
        )

        st.download_button(
            "Export flashcards",
            flash_export.to_csv(index=False),
            file_name="last_stretch_flashcards.csv",
            mime="text/csv",
            use_container_width=True
        )


# =========================================================
# TAB 5: ANALYTICS
# =========================================================

with tabs[4]:

    section("01", "Study analytics")

    plan = st.session_state.plan

    if plan is None or plan.empty:

        st.info(
            "Generate a study plan to unlock your analytics."
        )

    else:

        analysis_plan = plan.copy()

        analysis_plan["Completed"] = (
            analysis_plan["id"].isin(
                st.session_state.done
            )
        )

        total, completed, percentage = get_plan_stats(
            analysis_plan
        )

        a, b, c = st.columns(3)

        a.metric("Total planned", hrs(total))
        b.metric("Time completed", hrs(completed))
        c.metric("Completion rate", f"{percentage}%")

        section("02", "Subject breakdown")

        breakdown = (
            analysis_plan.groupby("Subject")
            .apply(
                lambda g: pd.Series({
                    "Planned": int(g["Minutes"].sum()),
                    "Completed": int(
                        g.loc[g["Completed"], "Minutes"].sum()
                    )
                }),
                include_groups=False
            )
            .reset_index()
        )

        if not breakdown.empty:

            breakdown["Completion %"] = (
                breakdown["Completed"]
                / breakdown["Planned"]
                * 100
            ).round(1)

            st.dataframe(
                breakdown,
                use_container_width=True,
                hide_index=True
            )

            chart_data = breakdown.set_index(
                "Subject"
            )[["Planned", "Completed"]]

            st.bar_chart(chart_data)

        section("03", "Daily study activity")

        daily = (
            analysis_plan.groupby("Date")
            .apply(
                lambda g: pd.Series({
                    "Planned": int(g["Minutes"].sum()),
                    "Completed": int(
                        g.loc[g["Completed"], "Minutes"].sum()
                    )
                }),
                include_groups=False
            )
            .reset_index()
        )

        if not daily.empty:

            daily["Date"] = daily["Date"].astype(str)

            st.line_chart(
                daily.set_index("Date")[
                    ["Planned", "Completed"]
                ]
            )

        section("04", "AI performance insights")

        st.write(
            "Let AI interpret your study patterns and recommend "
            "what to improve."
        )

        if st.button(
            "Analyze my study performance",
            type="primary",
            use_container_width=True
        ):

            with st.spinner(
                "AI is analyzing your study performance..."
            ):

                try:
                    report = analyze_progress(analysis_plan)

                    st.session_state.analytics_report = report

                except Exception as e:
                    st.error(f"Analysis failed: {e}")

        if st.session_state.get("analytics_report"):

            st.markdown(
                st.session_state.analytics_report
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:20px;">
        <div class="kicker">LAST STRETCH · STUDY SMARTER</div>
        <p style="color:#9A9488; font-size:.8rem;">
            Built for the days that matter.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
