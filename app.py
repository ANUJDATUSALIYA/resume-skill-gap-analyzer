import io
from html import escape

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pypdf import PdfReader

from skill_analyzer import compare_resume_to_jd, radar_values, score_multiple_jobs, summarize_clusters


SAMPLE_RESUME = """
Anuj Kumar
Python Developer and Data Analyst

Skills: Python, SQL, HTML, CSS, JavaScript, Pandas, NumPy, Git, Streamlit,
data analysis, data visualization, MySQL.

Projects:
- Smart grocery recommendation system using Python and pandas.
- Sales dashboard using Excel and Power BI.
"""

SAMPLE_JD = """
We are hiring a Junior Data Scientist.

Required skills: Python, SQL, Machine Learning, Pandas, NumPy, Scikit-learn,
data visualization, statistics, NLP, AWS, Git.

The candidate should build models, clean datasets, create dashboards, and
deploy machine learning prototypes.
"""

SAMPLE_MULTI_JDS = {
    "Data Scientist": SAMPLE_JD,
    "Frontend Developer": "Required: HTML, CSS, JavaScript, React, Git, UI UX, testing.",
    "Cloud Data Engineer": "Required: Python, SQL, AWS, Docker, Spark, Hadoop, Linux.",
}

SKILL_LOGOS = {
    "python": ("Py", "#3776ab", "#ffffff"),
    "java": ("J", "#e11d48", "#ffffff"),
    "c++": ("C++", "#00599c", "#ffffff"),
    "c#": ("C#", "#68217a", "#ffffff"),
    "javascript": ("JS", "#f7df1e", "#111827"),
    "typescript": ("TS", "#3178c6", "#ffffff"),
    "html": ("H5", "#e34f26", "#ffffff"),
    "css": ("C3", "#1572b6", "#ffffff"),
    "react": ("R", "#61dafb", "#0f172a"),
    "angular": ("A", "#dd0031", "#ffffff"),
    "node.js": ("N", "#339933", "#ffffff"),
    "express": ("Ex", "#111827", "#ffffff"),
    "django": ("Dj", "#092e20", "#ffffff"),
    "flask": ("Fl", "#111827", "#ffffff"),
    "fastapi": ("FA", "#009688", "#ffffff"),
    "sql": ("SQL", "#2563eb", "#ffffff"),
    "mysql": ("My", "#00758f", "#ffffff"),
    "postgresql": ("Pg", "#336791", "#ffffff"),
    "mongodb": ("MDB", "#47a248", "#ffffff"),
    "oracle": ("Ora", "#f80000", "#ffffff"),
    "excel": ("XL", "#217346", "#ffffff"),
    "power bi": ("BI", "#f2c811", "#111827"),
    "tableau": ("Tb", "#2563eb", "#ffffff"),
    "data analysis": ("DA", "#0f766e", "#ffffff"),
    "data visualization": ("DV", "#7c3aed", "#ffffff"),
    "statistics": ("St", "#0891b2", "#ffffff"),
    "machine learning": ("ML", "#f97316", "#ffffff"),
    "deep learning": ("DL", "#dc2626", "#ffffff"),
    "natural language processing": ("NLP", "#7c3aed", "#ffffff"),
    "nlp": ("NLP", "#7c3aed", "#ffffff"),
    "computer vision": ("CV", "#9333ea", "#ffffff"),
    "scikit-learn": ("SK", "#f59e0b", "#111827"),
    "pandas": ("Pd", "#150458", "#ffffff"),
    "numpy": ("Num", "#4dabcf", "#0f172a"),
    "tensorflow": ("TF", "#ff6f00", "#ffffff"),
    "keras": ("Kr", "#d00000", "#ffffff"),
    "pytorch": ("PT", "#ee4c2c", "#ffffff"),
    "aws": ("AWS", "#ff9900", "#111827"),
    "azure": ("Az", "#0078d4", "#ffffff"),
    "google cloud": ("GCP", "#4285f4", "#ffffff"),
    "docker": ("D", "#2496ed", "#ffffff"),
    "kubernetes": ("K8s", "#326ce5", "#ffffff"),
    "git": ("Git", "#f05032", "#ffffff"),
    "github": ("GH", "#24292f", "#ffffff"),
    "linux": ("Lx", "#facc15", "#111827"),
    "rest api": ("API", "#0f766e", "#ffffff"),
    "api": ("API", "#0f766e", "#ffffff"),
    "streamlit": ("St", "#ff4b4b", "#ffffff"),
    "matplotlib": ("Mt", "#11557c", "#ffffff"),
    "seaborn": ("Sb", "#4c72b0", "#ffffff"),
    "big data": ("BD", "#9333ea", "#ffffff"),
    "spark": ("Sp", "#e25a1c", "#ffffff"),
    "hadoop": ("Hd", "#facc15", "#111827"),
    "devops": ("DO", "#2563eb", "#ffffff"),
    "agile": ("Ag", "#16a34a", "#ffffff"),
    "testing": ("QA", "#db2777", "#ffffff"),
    "selenium": ("Se", "#43b02a", "#ffffff"),
    "cybersecurity": ("Sec", "#334155", "#ffffff"),
    "networking": ("Net", "#0284c7", "#ffffff"),
    "android": ("And", "#3ddc84", "#0f172a"),
    "flutter": ("Fl", "#02569b", "#ffffff"),
    "firebase": ("Fb", "#ffca28", "#111827"),
    "ui ux": ("UX", "#ec4899", "#ffffff"),
    "figma": ("Fi", "#a259ff", "#ffffff"),
    "project management": ("PM", "#64748b", "#ffffff"),
}


st.set_page_config(
    page_title="Resume Skill Gap Analyzer",
    page_icon="RS",
    layout="wide",
)


def read_pdf(uploaded_file):
    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def display_skill_name(skill):
    special_names = {
        "api": "API",
        "aws": "AWS",
        "azure": "Azure",
        "c#": "C#",
        "c++": "C++",
        "css": "CSS",
        "git": "Git",
        "github": "GitHub",
        "google cloud": "Google Cloud",
        "html": "HTML",
        "javascript": "JavaScript",
        "mysql": "MySQL",
        "nlp": "NLP",
        "node.js": "Node.js",
        "numpy": "NumPy",
        "pandas": "Pandas",
        "postgresql": "PostgreSQL",
        "power bi": "Power BI",
        "rest api": "REST API",
        "scikit-learn": "Scikit-learn",
        "sql": "SQL",
        "ui ux": "UI UX",
    }
    normalized = skill.strip().lower()
    return special_names.get(normalized, skill.title())


def skill_logo(skill):
    normalized = skill.strip().lower()
    mark, bg, fg = SKILL_LOGOS.get(normalized, (display_skill_name(skill)[:2].upper(), "#475569", "#ffffff"))
    return (
        f"<span class='skill-logo' style='background:{bg};color:{fg}' "
        f"title='{escape(display_skill_name(skill))} logo'>{escape(mark)}</span>"
    )


def chip_list(values, kind="neutral", show_logo=True):
    if not values:
        st.caption("None found")
        return

    colors = {
        "match": ("#e8fff3", "#127a46"),
        "missing": ("#fff1f2", "#be123c"),
        "neutral": ("#eef6ff", "#1d4ed8"),
    }
    bg, fg = colors[kind]
    html = "".join(
        f"<span class='chip' style='background:{bg};color:{fg}'>"
        f"{skill_logo(item) if show_logo else ''}"
        f"<span>{escape(display_skill_name(item))}</span>"
        f"</span>"
        for item in values
    )
    st.markdown(f"<div class='chip-row'>{html}</div>", unsafe_allow_html=True)


def readiness_label(score):
    if score >= 80:
        return "Strong fit", "#15803d"
    if score >= 55:
        return "Moderate fit", "#b45309"
    return "Needs work", "#be123c"


def dashboard_card(label, value, helper="", accent="#2563eb"):
    st.markdown(
        f"""
        <div class="dashboard-card" style="border-top-color:{accent}">
            <div class="card-label">{escape(label)}</div>
            <div class="card-value">{escape(str(value))}</div>
            <div class="card-helper">{escape(helper)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(title, body, accent="#2563eb"):
    st.markdown(
        f"""
        <div class="insight-card" style="border-left-color:{accent}">
            <div class="insight-title">{escape(title)}</div>
            <div class="insight-body">{escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_band(result):
    label, color = readiness_label(result["match_score"])
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        dashboard_card("Match Score", f"{result['match_score']}%", label, color)
    with c2:
        dashboard_card("Matched", len(result["matched_skills"]), "Resume and JD", "#16a34a")
    with c3:
        dashboard_card("Missing", len(result["missing_skills"]), "Skill gaps", "#e11d48")
    with c4:
        dashboard_card("JD Skills", len(result["jd_skills"]), "Required skills", "#0f766e")
    with c5:
        dashboard_card("Resume Skills", len(result["resume_skills"]), "Detected skills", "#7c3aed")


def render_missing_skill_names(result):
    with st.container(border=True):
        st.subheader("Missing Skill Names")
        if result["missing_skills"]:
            st.caption("These skills are required in the job description but were not found in the resume.")
            chip_list(result["missing_skills"], "missing")
        else:
            st.success("No missing JD skills were detected.")


def make_score_chart(result):
    data = pd.DataFrame(
        [
            {"Status": "Matched", "Count": len(result["matched_skills"])},
            {"Status": "Missing", "Count": len(result["missing_skills"])},
            {"Status": "Resume only", "Count": len(result["extra_skills"])},
        ]
    )
    fig = px.bar(
        data,
        x="Status",
        y="Count",
        color="Status",
        color_discrete_map={
            "Matched": "#16a34a",
            "Missing": "#e11d48",
            "Resume only": "#2563eb",
        },
        text="Count",
    )
    fig.update_layout(showlegend=False, height=320, margin=dict(l=10, r=10, t=20, b=10))
    return fig


def make_match_gauge(result):
    score = result["match_score"]
    label, color = readiness_label(score)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%", "font": {"size": 42}},
            title={"text": label, "font": {"size": 16}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 55], "color": "#fee2e2"},
                    {"range": [55, 80], "color": "#fef3c7"},
                    {"range": [80, 100], "color": "#dcfce7"},
                ],
            },
        )
    )
    fig.update_layout(height=270, margin=dict(l=10, r=10, t=25, b=5))
    return fig


def make_gap_donut(result):
    labels = ["Matched", "Missing"]
    values = [len(result["matched_skills"]), len(result["missing_skills"])]
    fig = px.pie(
        names=labels,
        values=values,
        hole=0.58,
        color=labels,
        color_discrete_map={"Matched": "#16a34a", "Missing": "#e11d48"},
    )
    fig.update_traces(textposition="inside", textinfo="label+percent")
    fig.update_layout(showlegend=False, height=270, margin=dict(l=10, r=10, t=25, b=5))
    return fig


def make_cluster_chart(result):
    table = result["cluster_table"]
    if table.empty:
        return None
    counts = table.groupby(["cluster_name", "status"]).size().reset_index(name="count")
    fig = px.bar(
        counts,
        x="cluster_name",
        y="count",
        color="status",
        barmode="stack",
        color_discrete_map={
            "Matched": "#16a34a",
            "Missing": "#e11d48",
            "Resume only": "#2563eb",
        },
        text="count",
    )
    fig.update_layout(
        height=320,
        xaxis_title="Unsupervised Skill Cluster",
        yaxis_title="Skill Count",
        legend_title="Status",
        margin=dict(l=10, r=10, t=25, b=10),
    )
    return fig


def make_cluster_coverage_chart(result):
    summary = result["cluster_summary"]
    if summary.empty:
        return None
    fig = px.bar(
        summary.sort_values("coverage"),
        x="coverage",
        y="cluster_name",
        orientation="h",
        color="priority",
        text="coverage",
        color_discrete_map={"High": "#e11d48", "Medium": "#f59e0b", "Low": "#16a34a"},
        hover_data=["matched", "missing", "resume_only"],
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=310,
        xaxis_title="Coverage %",
        yaxis_title="",
        legend_title="Gap Priority",
        margin=dict(l=10, r=35, t=25, b=10),
        xaxis=dict(range=[0, 110]),
    )
    return fig


def make_profile_radar(result):
    values = radar_values(result)
    labels = list(values.keys())
    points = list(values.values())
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=points + [points[0]],
            theta=labels + [labels[0]],
            fill="toself",
            line_color="#2563eb",
            fillcolor="rgba(37, 99, 235, 0.18)",
            name="Profile",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=290,
        margin=dict(l=20, r=20, t=25, b=20),
    )
    return fig


def make_priority_chart(result):
    gaps = result["gap_priority"]
    if gaps.empty:
        return None
    priority_counts = gaps.groupby(["cluster_name", "priority"]).size().reset_index(name="count")
    fig = px.bar(
        priority_counts,
        x="cluster_name",
        y="count",
        color="priority",
        text="count",
        color_discrete_map={"High": "#e11d48", "Medium": "#f59e0b", "Low": "#2563eb"},
    )
    fig.update_layout(
        height=290,
        xaxis_title="Cluster",
        yaxis_title="Missing Skills",
        legend_title="Priority",
        margin=dict(l=10, r=10, t=25, b=10),
    )
    return fig


def render_cluster_section(result):
    clusters = summarize_clusters(result["cluster_table"])
    if not clusters:
        st.info("Add resume and JD text to generate clusters.")
        return

    cluster_cols = st.columns(2)
    for index, (cluster_name, skills) in enumerate(clusters.items()):
        with cluster_cols[index % 2]:
            st.markdown(f"<div class='panel-title'>{cluster_name}</div>", unsafe_allow_html=True)
            chip_list(skills)

    with st.expander("View cluster table"):
        st.dataframe(result["cluster_table"], use_container_width=True, hide_index=True)


st.markdown(
    """
    <style>
        .stApp {
            background: #f5f7fb;
        }
        .main .block-container {
            padding-top: 1.5rem;
            max-width: 1280px;
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #ffffff;
            border-color: #dbe3ef;
            border-radius: 8px;
        }
        .subtle {
            color: #475569;
            font-size: 0.98rem;
            margin-top: -0.75rem;
        }
        .dashboard-header {
            background:
                linear-gradient(120deg, rgba(37, 99, 235, 0.08), rgba(22, 163, 74, 0.08)),
                #ffffff;
            border: 1px solid #dbe3ef;
            border-radius: 8px;
            padding: 1rem 1.15rem;
            margin-bottom: 1rem;
        }
        .dashboard-title {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 750;
            line-height: 1.1;
        }
        .dashboard-card {
            background: #ffffff;
            border: 1px solid #dbe3ef;
            border-radius: 8px;
            border-top: 4px solid #2563eb;
            min-height: 118px;
            padding: 0.85rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        }
        .dashboard-card:hover,
        .insight-card:hover {
            border-color: #bfdbfe;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
        }
        .card-label {
            color: #64748b;
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        .card-value {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 780;
            line-height: 1.15;
            margin-top: 0.3rem;
        }
        .card-helper {
            color: #64748b;
            font-size: 0.88rem;
            margin-top: 0.2rem;
        }
        .panel-title {
            color: #0f172a;
            font-size: 0.95rem;
            font-weight: 750;
            margin-bottom: 0.3rem;
        }
        .insight-card {
            background: #ffffff;
            border: 1px solid #dbe3ef;
            border-left: 4px solid #2563eb;
            border-radius: 8px;
            min-height: 104px;
            padding: 0.85rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        }
        .insight-title {
            color: #0f172a;
            font-size: 0.95rem;
            font-weight: 750;
        }
        .insight-body {
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.45;
            margin-top: 0.28rem;
        }
        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin: 0.3rem 0 0.9rem;
        }
        .chip {
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            font-size: 0.88rem;
            font-weight: 600;
            min-height: 34px;
            padding: 0.25rem 0.68rem 0.25rem 0.28rem;
            white-space: nowrap;
        }
        .skill-logo {
            align-items: center;
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 7px;
            display: inline-flex;
            font-size: 0.68rem;
            font-weight: 850;
            height: 24px;
            justify-content: center;
            letter-spacing: 0;
            min-width: 24px;
            padding: 0 0.25rem;
            text-transform: none;
        }
        div[data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 0.8rem;
        }
        section[data-testid="stSidebar"] {
            background: #eef3f9;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="dashboard-header">
        <div class="dashboard-title">Resume Skill Gap Dashboard</div>
        <p class="subtle">Aesthetic NLP and unsupervised learning dashboard for resume matching, K-Means skill clustering, gap priority, and improvement planning.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Controls")
    use_sample = st.toggle("Use sample resume and JD", value=True)
    show_multi_jd = st.toggle("Show multiple JD ranking", value=True)
    st.divider()
    st.write("Dashboard sections")
    st.caption("Overview, skill gaps, unsupervised clusters, recommendations, and job ranking.")
    st.divider()
    st.caption("For PDF resumes, text extraction works best with selectable text PDFs.")

input_col, dashboard_col = st.columns([0.88, 1.6], gap="large")

with input_col:
    with st.container(border=True):
        st.subheader("Inputs")
        uploaded_resume = st.file_uploader("Upload resume PDF", type=["pdf"])
        resume_text = ""
        if uploaded_resume is not None:
            try:
                resume_text = read_pdf(uploaded_resume)
            except Exception as exc:
                st.error(f"Could not read PDF: {exc}")
        resume_text = st.text_area(
            "Resume text",
            value=resume_text or (SAMPLE_RESUME if use_sample else ""),
            height=245,
            placeholder="Paste resume text here...",
        )
        jd_text = st.text_area(
            "Job description text",
            value=SAMPLE_JD if use_sample else "",
            height=245,
            placeholder="Paste job description here...",
        )
        analyze = st.button("Analyze Dashboard", type="primary", use_container_width=True)

with dashboard_col:
    should_analyze = analyze or use_sample

if should_analyze:
    if not resume_text.strip() or not jd_text.strip():
        st.warning("Please provide both resume and job description text.")
        st.stop()

    result = compare_resume_to_jd(resume_text, jd_text)

    with dashboard_col:
        metric_band(result)
        render_missing_skill_names(result)
        overview_tab, gaps_tab, clusters_tab, plan_tab = st.tabs(
            ["Overview", "Skill Gaps", "Clusters", "Action Plan"]
        )

        with overview_tab:
            st.subheader("Executive Snapshot")
            top_cluster = (
                result["cluster_summary"].iloc[0].to_dict()
                if not result["cluster_summary"].empty
                else None
            )
            insight_cols = st.columns(3)
            with insight_cols[0]:
                insight_card(
                    "Best Signal",
                    f"{len(result['matched_skills'])} JD skills are already present in the resume.",
                    "#16a34a",
                )
            with insight_cols[1]:
                insight_card(
                    "Main Gap",
                    (
                        f"{top_cluster['cluster_name']} has {top_cluster['missing']} missing skill(s)."
                        if top_cluster
                        else "Add more resume and JD text to discover the main gap."
                    ),
                    "#e11d48",
                )
            with insight_cols[2]:
                insight_card(
                    "Model Used",
                    "TF-IDF vectors plus K-Means clustering with silhouette-based cluster selection.",
                    "#2563eb",
                )

            gauge_col, donut_col, radar_col = st.columns(3)
            with gauge_col:
                with st.container(border=True):
                    st.subheader("Candidate Fit")
                    st.plotly_chart(make_match_gauge(result), use_container_width=True)
            with donut_col:
                with st.container(border=True):
                    st.subheader("JD Coverage")
                    st.plotly_chart(make_gap_donut(result), use_container_width=True)
            with radar_col:
                with st.container(border=True):
                    st.subheader("Profile Shape")
                    st.plotly_chart(make_profile_radar(result), use_container_width=True)

            with st.container(border=True):
                st.subheader("Skill Status Breakdown")
                st.plotly_chart(make_score_chart(result), use_container_width=True)

            if show_multi_jd:
                with st.container(border=True):
                    st.subheader("Resume Ranking Across Multiple JDs")
                    ranking = score_multiple_jobs(resume_text, SAMPLE_MULTI_JDS)
                    fig = px.bar(
                        ranking,
                        x="role",
                        y="match_score",
                        color="match_score",
                        color_continuous_scale=["#ef4444", "#f59e0b", "#16a34a"],
                        text="match_score",
                    )
                    fig.update_layout(
                        height=310,
                        xaxis_title="Role",
                        yaxis_title="Match Score",
                        coloraxis_showscale=False,
                        margin=dict(l=10, r=10, t=20, b=10),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(ranking, use_container_width=True, hide_index=True)

        with gaps_tab:
            gap_left, gap_right = st.columns(2)
            with gap_left:
                with st.container(border=True):
                    st.subheader("Matched Skills")
                    chip_list(result["matched_skills"], "match")
                    st.subheader("Resume Only")
                    chip_list(result["extra_skills"], "neutral")
            with gap_right:
                with st.container(border=True):
                    st.subheader("Missing Skills")
                    chip_list(result["missing_skills"], "missing")
                    if not result["gap_priority"].empty:
                        st.dataframe(result["gap_priority"], use_container_width=True, hide_index=True)
            with st.container(border=True):
                st.subheader("Gap Priority by Cluster")
                priority_fig = make_priority_chart(result)
                if priority_fig:
                    st.plotly_chart(priority_fig, use_container_width=True)
                else:
                    st.success("No missing JD skills were detected.")

        with clusters_tab:
            cluster_chart_col, coverage_col = st.columns(2)
            with cluster_chart_col:
                with st.container(border=True):
                    st.subheader("K-Means Skill Clusters")
                    cluster_fig = make_cluster_chart(result)
                    if cluster_fig:
                        st.plotly_chart(cluster_fig, use_container_width=True)
            with coverage_col:
                with st.container(border=True):
                    st.subheader("Cluster Coverage")
                    coverage_fig = make_cluster_coverage_chart(result)
                    if coverage_fig:
                        st.plotly_chart(coverage_fig, use_container_width=True)
            with st.container(border=True):
                st.subheader("Unsupervised Cluster Summary")
                if not result["cluster_summary"].empty:
                    st.dataframe(result["cluster_summary"], use_container_width=True, hide_index=True)
                render_cluster_section(result)

        with plan_tab:
            plan_left, plan_right = st.columns(2)
            with plan_left:
                with st.container(border=True):
                    st.subheader("Improvement Suggestions")
                    if result["recommendations"]:
                        rec_df = pd.DataFrame(result["recommendations"])
                        st.dataframe(rec_df, use_container_width=True, hide_index=True)
                    else:
                        st.success("Great match. No missing JD skills were detected.")
            with plan_right:
                with st.container(border=True):
                    st.subheader("Extracted Keywords")
                    st.write("Resume keywords")
                    chip_list(result["resume_keywords"], "neutral")
                    st.write("JD keywords")
                    chip_list(result["jd_keywords"], "neutral")
else:
    with dashboard_col:
        st.info("Upload or paste resume and JD text, then click Analyze Dashboard.")
