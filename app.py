import html
import json
import os
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st
from groq import Groq

MODEL = "openai/gpt-oss-120b"
SESSION_TYPES = ["Learn", "Practice", "Revise", "Mock test"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MAX_DAYS = 45
PALETTE = ["#E8452C", "#2F6F6B", "#E9B44C", "#3B4FA3", "#8C5A9E", "#6B8F3A"]

st.set_page_config(page_title="Last Stretch", page_icon="🟥", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,800;1,9..144,500&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');
:root{--ink:#15130F;--paper:#F2EDE4;--card:#FBF8F2;--red:#E8452C;--mute:#6F6A5F;
--mono:'JetBrains Mono',monospace;--serif:'Fraunces',serif;}
.stApp{background:var(--paper);color:var(--ink);font-family:'Instrument Sans',sans-serif;}
[data-testid="stHeader"]{background:transparent;}
#MainMenu,footer,[data-testid="stToolbar"]{visibility:hidden;}
.block-container{max-width:1180px;padding-top:2rem;}
[data-testid="stSidebar"]{background:var(--card);border-right:2px solid var(--ink);}
[data-baseweb="input"] input{font-family:var(--mono);}
[data-testid="stAlert"]{border:2px solid var(--ink);border-radius:0;}

.mast{border-bottom:4px solid var(--ink);padding-bottom:18px;margin-bottom:8px;}
.kicker{font-family:var(--mono);font-size:.75rem;letter-spacing:.2em;color:var(--mute);}
.mast h1{font-family:var(--serif);font-weight:800;font-size:clamp(3.4rem,9vw,6.5rem);line-height:.88;margin:.3rem 0 .6rem;padding:0;letter-spacing:-.03em;}
.mast h1 em{color:var(--red);font-weight:500;}
.mast p{font-size:1.05rem;max-width:560px;margin:0;}

.sec{display:flex;justify-content:space-between;font-family:var(--mono);font-size:.75rem;letter-spacing:.14em;text-transform:uppercase;border-bottom:2px solid var(--ink);padding-bottom:6px;margin:2.4rem 0 1rem;}

.stButton>button,.stDownloadButton>button{border:2px solid var(--ink);border-radius:0;background:var(--card);color:var(--ink);font-family:var(--mono);font-weight:700;text-transform:uppercase;letter-spacing:.06em;box-shadow:4px 4px 0 var(--ink);transition:transform .08s,box-shadow .08s;}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translate(2px,2px);box-shadow:2px 2px 0 var(--ink);border-color:var(--ink);color:var(--ink);}
button[kind="primary"],button[data-testid="stBaseButton-primary"]{background:var(--red)!important;color:#fff!important;}

.cds{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;}
.cd{background:var(--card);border:2px solid var(--ink);box-shadow:6px 6px 0 var(--ink);padding:16px 18px;animation:rise .5s both;}
.cd.hot{background:var(--red);color:#fff;}
.cd .nm{font-family:var(--mono);font-weight:700;text-transform:uppercase;letter-spacing:.08em;font-size:.8rem;}
.sw{display:inline-block;width:11px;height:11px;background:var(--c);border:1.5px solid currentColor;margin-right:8px;}
.cd .num{font-family:var(--serif);font-weight:800;font-size:4.6rem;line-height:.95;margin-top:6px;}
.unit{font-family:var(--mono);font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;opacity:.75;}
.chips{margin:10px 0 12px;min-height:26px;}
.chip{display:inline-block;border:1.5px solid currentColor;border-radius:99px;padding:1px 10px;font-size:.76rem;margin:2px 5px 2px 0;}
.muted{font-style:italic;opacity:.6;font-size:.8rem;}
.bar{height:9px;border:1.5px solid currentColor;margin-bottom:6px;}
.bar i{display:block;height:100%;background:var(--c);}
.cd.hot .bar i{background:#fff;}

.strip{display:flex;gap:16px;overflow-x:auto;padding:6px 8px 26px 2px;}
.day{flex:0 0 218px;background:var(--card);border:2px solid var(--ink);box-shadow:5px 5px 0 var(--ink);padding:12px 14px;animation:rise .5s both;}
.day.today{outline:4px solid var(--red);outline-offset:3px;}
.day.past{opacity:.5;}
.day.exam{background:var(--ink);color:var(--paper);}
.dh{display:flex;align-items:baseline;gap:10px;margin-bottom:6px;}
.dn{font-family:var(--serif);font-weight:800;font-size:2.6rem;line-height:1;}
.dm{font-family:var(--mono);font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;}
.tag{margin-left:auto;background:var(--red);color:#fff;font-family:var(--mono);font-size:.62rem;padding:2px 6px;letter-spacing:.1em;}
.ex{border:2px solid var(--red);color:var(--red);font-family:var(--mono);font-weight:700;font-size:.78rem;padding:4px 8px;margin:6px 0;letter-spacing:.08em;}
.ses{display:flex;gap:9px;padding:8px 0;border-top:1px dashed #a39c8c;}
.ses .dot{flex:none;width:10px;height:10px;margin-top:5px;background:var(--c);border:1.5px solid currentColor;}
.ses .t{font-weight:600;font-size:.88rem;line-height:1.25;}
.ses .s{font-family:var(--mono);font-size:.64rem;text-transform:uppercase;letter-spacing:.05em;opacity:.7;margin-top:2px;}
.ses.done .t{text-decoration:line-through;opacity:.4;}
.load{height:7px;border:1.5px solid currentColor;margin-top:10px;}
.load i{display:block;height:100%;background:currentColor;}
.load.over i{background:var(--red);}

.empty{border:2px dashed var(--ink);padding:14px 16px;font-family:var(--serif);font-style:italic;font-size:1.1rem;}
.stamp{display:inline-block;border:3px solid var(--red);color:var(--red);font-family:var(--mono);font-weight:700;padding:6px 14px;transform:rotate(-3deg);letter-spacing:.12em;margin-top:12px;}
@keyframes rise{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:none;}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def esc(x):
    return html.escape(str(x))


def hrs(m):
    return f"{m / 60:.1f}h"


def sec(num, title, right=""):
    st.markdown(
        f'<div class="sec"><span>{num} — {esc(title)}</span><span>{esc(right)}</span></div>',
        unsafe_allow_html=True,
    )


def get_api_key():
    key = os.getenv("GROQ_API_KEY", "")
    try:
        key = key or st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass
    return key


# ---------- generation ----------
def build_availability(start, end, hours_by_weekday):
    out, d = [], start
    while d <= end:
        h = hours_by_weekday[d.weekday()]
        if h > 0:
            out.append((d, h))
        d += timedelta(days=1)
    return out


def ask_model(api_key, subjects, avail):
    client = Groq(api_key=api_key)
    subj_lines = "\n".join(
        f"- {s['Subject']} | exam: {s['exam']} | weak topics: {s['Weak topics'] or 'none listed'}"
        for s in subjects
    )
    avail_lines = "\n".join(f"{d.isoformat()} ({DAYS[d.weekday()]}): {h}h" for d, h in avail)
    system = (
        "You are a study planner. Build a day-by-day study schedule. Rules: "
        "give weak topics more total time and revisit them at least twice (spaced repetition); "
        "weight subjects with closer exams more heavily; "
        "mix subjects within a day; sessions are 25-90 minutes; "
        "never exceed a day's available hours; never schedule a subject on or after its exam date; "
        "the last 2-3 days before each exam should be Revise or Mock test. "
        "Topics must be specific (e.g. 'Doppler effect numericals'), not just the subject name. "
        'Return ONLY valid JSON: {"sessions":[{"date":"YYYY-MM-DD","subject":"...",'
        '"topic":"...","minutes":60,"type":"Learn|Practice|Revise|Mock test"}]}'
    )
    user = f"Today: {date.today().isoformat()}\n\nSUBJECTS:\n{subj_lines}\n\nAVAILABLE TIME:\n{avail_lines}"
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=8000,
    )
    return json.loads(resp.choices[0].message.content).get("sessions", [])


def clean_and_schedule(raw, subjects, avail, start_time, break_min, ver):
    exam = {s["Subject"]: s["exam"] for s in subjects}
    cap = {d: h * 60 for d, h in avail}
    used, kept = {}, []

    for s in sorted(raw, key=lambda x: str(x.get("date", ""))):
        try:
            d = date.fromisoformat(s["date"])
            mins = int(s["minutes"])
        except Exception:
            continue
        subj = s.get("subject")
        if subj not in exam or d not in cap or d >= exam[subj] or mins <= 0:
            continue
        if used.get(d, 0) + mins > cap[d]:
            continue
        used[d] = used.get(d, 0) + mins
        stype = s.get("type") if s.get("type") in SESSION_TYPES else "Learn"
        kept.append({"Date": d, "Subject": subj, "Topic": s.get("topic", ""), "Minutes": mins, "Type": stype})

    cursor = {}
    for n, row in enumerate(kept):
        d = row["Date"]
        t = cursor.get(d, datetime.combine(d, start_time))
        row["Start"] = t.strftime("%H:%M")
        cursor[d] = t + timedelta(minutes=row["Minutes"] + break_min)
        row["id"] = f"v{ver}-{n}"

    cols = ["Date", "Start", "Minutes", "Subject", "Topic", "Type", "id"]
    return pd.DataFrame(kept, columns=cols), len(raw) - len(kept)


# ---------- html builders (single-line on purpose: indented HTML turns into code blocks) ----------
def countdown_html(info, ed, done, colors, today):
    cards = []
    for i, (name, v) in enumerate(info.items()):
        left = (v["exam"] - today).days
        rows = ed[ed["Subject"] == name]
        planned = int(rows["Minutes"].sum())
        got = int(rows.loc[rows["id"].isin(done), "Minutes"].sum())
        pct = round(got / planned * 100) if planned else 0
        hot = " hot" if left <= 3 else ""
        chips = "".join(f'<span class="chip">{esc(w.strip())}</span>' for w in v["weak"].split(",") if w.strip())
        chips = chips or '<span class="muted">no weak topics listed. bold claim.</span>'
        unit = "day" if left == 1 else "days"
        cards.append(
            f'<div class="cd{hot}" style="--c:{colors[name]};animation-delay:{i * 70}ms">'
            f'<div class="nm"><span class="sw"></span>{esc(name)}</div>'
            f'<div class="num">{left}</div>'
            f'<div class="unit">{unit} to go · {v["exam"]:%d %b}</div>'
            f'<div class="chips">{chips}</div>'
            f'<div class="bar"><i style="width:{pct}%"></i></div>'
            f'<div class="unit">{hrs(got)} of {hrs(planned)} done</div>'
            f"</div>"
        )
    return f'<div class="cds">{"".join(cards)}</div>'


def board_html(ed, info, colors, cap, done, today):
    by_day = {d: g.sort_values("Start") for d, g in ed.groupby("Date")}
    exams = {}
    for n, v in info.items():
        exams.setdefault(v["exam"], []).append(n)
    out = []
    for i, d in enumerate(sorted(set(by_day) | set(exams))):
        g = by_day.get(d)
        cls = "day"
        if d in exams:
            cls += " exam"
        if d == today:
            cls += " today"
        elif d < today:
            cls += " past"
        used = int(g["Minutes"].sum()) if g is not None else 0
        limit = cap.get(d, 0)
        pct = min(100, round(used / limit * 100)) if limit else (100 if used else 0)
        over = " over" if used > limit else ""
        tag = '<span class="tag">TODAY</span>' if d == today else ""
        parts = [
            f'<div class="{cls}" style="animation-delay:{min(i, 12) * 40}ms">',
            f'<div class="dh"><span class="dn">{d.day}</span><span class="dm">{d:%a}<br>{d:%b}</span>{tag}</div>',
        ]
        for n in exams.get(d, []):
            parts.append(f'<div class="ex">EXAM · {esc(n)}</div>')
        if g is not None:
            for _, r in g.iterrows():
                dn = " done" if r["id"] in done else ""
                parts.append(
                    f'<div class="ses{dn}" style="--c:{colors.get(r["Subject"], "#888")}"><span class="dot"></span>'
                    f'<div><div class="t">{esc(r["Topic"] or r["Subject"])}</div>'
                    f'<div class="s">{esc(r["Subject"])} · {int(r["Minutes"])}m · {esc(r["Type"])}</div></div></div>'
                )
            parts.append(
                f'<div class="load{over}"><i style="width:{pct}%"></i></div>'
                f'<div class="unit">{hrs(used)} / {hrs(limit)}</div>'
            )
        parts.append("</div>")
        out.append("".join(parts))
    return f'<div class="strip">{"".join(out)}</div>'


# ---------- state ----------
st.session_state.setdefault("plan", None)
st.session_state.setdefault("ver", 0)
st.session_state.setdefault("dropped", 0)
st.session_state.setdefault("avail", [])
st.session_state.setdefault("info", {})
st.session_state.setdefault("done", set())

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("### Your week")
    api_key = st.text_input("Groq API key", value=get_api_key(), type="password")
    st.caption("Hours you can actually study. Not hours you wish you could.")
    hours = {}
    defaults = [2, 2, 2, 2, 2, 4, 4]
    for i, name in enumerate(DAYS):
        hours[i] = st.number_input(name, 0.0, 12.0, float(defaults[i]), 0.5, key=f"h_{i}")
    start_time = st.time_input("Daily start time", value=datetime.strptime("17:00", "%H:%M").time())
    break_min = st.slider("Break between sessions (min)", 0, 30, 10)

# ---------- masthead ----------
st.markdown(
    '<div class="mast"><div class="kicker">EXAM SEASON · STUDY PLANNER</div>'
    "<h1>Last<br><em>Stretch.</em></h1>"
    "<p>Tell it what you're up against. It builds the plan. You stop pretending you'll figure it out the night before.</p></div>",
    unsafe_allow_html=True,
)

# ---------- input ----------
sec("01", "What's on the line")
default_df = pd.DataFrame(
    [
        {"Subject": "Physics", "Exam date": date.today() + timedelta(days=14), "Weak topics": "Doppler effect, Optics"},
        {"Subject": "Chemistry", "Exam date": date.today() + timedelta(days=18), "Weak topics": "Organic reactions"},
    ]
)
subjects_df = st.data_editor(
    default_df,
    num_rows="dynamic",
    key="subjects_editor",
    column_config={
        "Exam date": st.column_config.DateColumn("Exam date", min_value=date.today() + timedelta(days=1)),
        "Weak topics": st.column_config.TextColumn("Weak topics (comma separated)"),
    },
)

if st.button("Build my plan", type="primary"):
    subjects = []
    for _, r in subjects_df.iterrows():
        if not str(r["Subject"]).strip() or pd.isna(r["Subject"]) or pd.isna(r["Exam date"]):
            continue
        subjects.append(
            {
                "Subject": str(r["Subject"]).strip(),
                "exam": pd.to_datetime(r["Exam date"]).date(),
                "Weak topics": "" if pd.isna(r["Weak topics"]) else str(r["Weak topics"]),
            }
        )

    if not api_key:
        st.error("No API key. Paste it in the sidebar.")
    elif not subjects:
        st.error("Add at least one subject with an exam date.")
    else:
        last_day = max(s["exam"] for s in subjects) - timedelta(days=1)
        today = date.today()
        if last_day < today:
            st.error("Every exam date has to be in the future.")
        elif (last_day - today).days > MAX_DAYS:
            st.error(f"Last exam is too far out. Keep it within {MAX_DAYS} days.")
        else:
            avail = build_availability(today, last_day, hours)
            if not avail:
                st.error("Zero study hours in that window. Fix the sidebar.")
            else:
                ver = st.session_state.ver + 1
                with st.spinner("Doing the math you've been avoiding..."):
                    try:
                        raw = ask_model(api_key, subjects, avail)
                        plan, dropped = clean_and_schedule(raw, subjects, avail, start_time, break_min, ver)
                        if plan.empty:
                            st.error("Model gave back garbage. Hit the button again.")
                        else:
                            st.session_state.plan = plan
                            st.session_state.dropped = dropped
                            st.session_state.avail = avail
                            st.session_state.info = {
                                s["Subject"]: {"exam": s["exam"], "weak": s["Weak topics"]} for s in subjects
                            }
                            st.session_state.done = set()
                            st.session_state.ver = ver
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

# ---------- plan ----------
if st.session_state.plan is not None:
    today = date.today()
    ver = st.session_state.ver
    info = st.session_state.info
    done = st.session_state.done
    colors = {n: PALETTE[i % len(PALETTE)] for i, n in enumerate(info)}
    cap = {d: h * 60 for d, h in st.session_state.avail}

    # placeholders: filled after the editor runs, but shown above it
    c_today = st.container()
    c_cd = st.container()
    c_board = st.container()

    sec("05", "Edit anything", "dates · times · topics · add or delete rows")
    if st.session_state.dropped:
        st.caption(f"{st.session_state.dropped} AI sessions got cut for breaking your hour limits or exam dates.")

    edited = st.data_editor(
        st.session_state.plan,
        num_rows="dynamic",
        key=f"plan_editor_{ver}",
        column_config={
            "id": None,
            "Date": st.column_config.DateColumn("Date", required=True),
            "Start": st.column_config.TextColumn("Start (HH:MM)"),
            "Minutes": st.column_config.NumberColumn("Minutes", min_value=5, max_value=240, step=5),
            "Subject": st.column_config.SelectboxColumn("Subject", options=list(info.keys())),
            "Type": st.column_config.SelectboxColumn("Type", options=SESSION_TYPES),
        },
    )

    ed = edited.dropna(subset=["Date", "Minutes", "Subject"]).copy()
    if ed.empty:
        st.info("Plan is empty. Add a row or rebuild.")
        st.stop()
    ed["Date"] = pd.to_datetime(ed["Date"]).dt.date
    ed["Minutes"] = ed["Minutes"].astype(int)
    ed["Start"] = ed["Start"].fillna("")
    ed["Topic"] = ed["Topic"].fillna("")
    ed["Type"] = ed["Type"].fillna("Learn")
    ed["id"] = [i if isinstance(i, str) else f"v{ver}-n{ix}" for ix, i in zip(ed.index, ed["id"])]

    # ---- 02 today ----
    with c_today:
        sec("02", "Today", f"{today:%A, %d %b}")
        rows = ed[ed["Date"] == today].sort_values("Start")
        if rows.empty:
            st.markdown('<div class="empty">Nothing on the schedule today. Suspicious.</div>', unsafe_allow_html=True)
        else:
            for _, r in rows.iterrows():
                label = f"**{r['Topic'] or r['Subject']}** · {r['Subject']} · {r['Minutes']} min · {r['Start']}"
                v = st.checkbox(label, value=r["id"] in done, key=f"done_{r['id']}")
                (done.add if v else done.discard)(r["id"])
            if rows["id"].isin(done).all():
                st.markdown('<div class="stamp">DONE. GO TOUCH GRASS.</div>', unsafe_allow_html=True)

    # ---- 03 countdown ----
    with c_cd:
        sec("03", "The clock")
        st.markdown(countdown_html(info, ed, done, colors, today), unsafe_allow_html=True)

    # ---- 04 board ----
    with c_board:
        total = int(ed["Minutes"].sum())
        got = int(ed.loc[ed["id"].isin(done), "Minutes"].sum())
        sec("04", "The board", f"{round(got / total * 100) if total else 0}% done · {hrs(total)} planned")
        st.markdown(board_html(ed, info, colors, cap, done, today), unsafe_allow_html=True)

    # ---- checks + export ----
    for d, mins in ed.groupby("Date")["Minutes"].sum().items():
        limit = cap.get(d, 0)
        if mins > limit:
            st.warning(f"{d}: you booked {mins / 60:.1f}h but only have {limit / 60:.1f}h. Pick one.")
    for _, r in ed.iterrows():
        ex = info.get(r["Subject"], {}).get("exam")
        if ex and r["Date"] >= ex:
            st.warning(f"{r['Subject']} session on {r['Date']} is on or after the exam ({ex}).")

    out = ed.assign(Done=ed["id"].isin(done)).drop(columns=["id"]).sort_values(["Date", "Start"])
    st.download_button("Download CSV", out.to_csv(index=False), file_name="last_stretch.csv", mime="text/csv")
