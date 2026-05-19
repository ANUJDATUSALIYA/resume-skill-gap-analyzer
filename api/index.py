from html import escape
import re

from flask import Flask, jsonify, request


app = Flask(__name__)


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

SKILL_CATALOG = [
    "python",
    "java",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "html",
    "css",
    "react",
    "angular",
    "node.js",
    "express",
    "django",
    "flask",
    "fastapi",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",
    "excel",
    "power bi",
    "tableau",
    "data analysis",
    "data visualization",
    "statistics",
    "machine learning",
    "deep learning",
    "natural language processing",
    "nlp",
    "computer vision",
    "scikit-learn",
    "pandas",
    "numpy",
    "tensorflow",
    "keras",
    "pytorch",
    "aws",
    "azure",
    "google cloud",
    "docker",
    "kubernetes",
    "git",
    "github",
    "linux",
    "rest api",
    "api",
    "streamlit",
    "matplotlib",
    "seaborn",
    "big data",
    "spark",
    "hadoop",
    "devops",
    "agile",
    "testing",
    "selenium",
    "cybersecurity",
    "networking",
    "android",
    "flutter",
    "firebase",
    "ui ux",
    "figma",
    "project management",
]

ALIASES = {
    "js": "javascript",
    "node": "node.js",
    "nodejs": "node.js",
    "ml": "machine learning",
    "dl": "deep learning",
    "natural language processing": "nlp",
    "postgres": "postgresql",
    "gcp": "google cloud",
    "rest": "rest api",
    "apis": "api",
    "ms excel": "excel",
    "powerbi": "power bi",
    "ui/ux": "ui ux",
}

COURSE_SUGGESTIONS = {
    "machine learning": "Complete a beginner ML course and build a classification project with scikit-learn.",
    "deep learning": "Learn neural networks with TensorFlow or PyTorch and train an image or text model.",
    "aws": "Study cloud basics, IAM, EC2, S3, and deploy one small web application.",
    "docker": "Containerize a Python or Node app and write a simple Dockerfile.",
    "sql": "Practice joins, grouping, subqueries, and window functions on a public dataset.",
    "react": "Build a dashboard UI with components, state, routing, and API calls.",
    "python": "Strengthen Python basics, file handling, OOP, pandas, and project structure.",
    "nlp": "Build a text classification or resume keyword extraction project.",
    "power bi": "Create an interactive business dashboard using filters and charts.",
    "git": "Practice branching, commits, pull requests, and resolving merge conflicts.",
}

SKILL_DOMAINS = {
    "Programming": {"python", "java", "c++", "c#", "javascript", "typescript"},
    "Frontend": {"html", "css", "react", "angular", "ui ux", "figma"},
    "Backend": {"node.js", "express", "django", "flask", "fastapi", "rest api", "api"},
    "Data": {
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "oracle",
        "excel",
        "pandas",
        "numpy",
        "statistics",
        "data analysis",
        "data visualization",
        "power bi",
        "tableau",
    },
    "AI / ML": {
        "machine learning",
        "deep learning",
        "nlp",
        "computer vision",
        "scikit-learn",
        "tensorflow",
        "keras",
        "pytorch",
    },
    "Cloud / DevOps": {
        "aws",
        "azure",
        "google cloud",
        "docker",
        "kubernetes",
        "linux",
        "spark",
        "hadoop",
        "big data",
        "devops",
    },
    "Quality / Delivery": {"git", "github", "agile", "testing", "selenium", "project management"},
    "Mobile": {"android", "flutter", "firebase"},
    "Security": {"cybersecurity", "networking"},
}


def title_skill(skill):
    names = {
        "api": "API",
        "aws": "AWS",
        "css": "CSS",
        "git": "Git",
        "html": "HTML",
        "javascript": "JavaScript",
        "mysql": "MySQL",
        "nlp": "NLP",
        "numpy": "NumPy",
        "pandas": "Pandas",
        "power bi": "Power BI",
        "scikit-learn": "Scikit-learn",
        "sql": "SQL",
    }
    return names.get(skill.lower(), skill.title())


def chip_list(skills, css_class):
    if not skills:
        return "<span class='muted'>None found</span>"
    return "".join(
        f"<span class='chip {css_class}'>{escape(title_skill(skill))}</span>" for skill in skills
    )


def dataframe_records(dataframe):
    return dataframe


def normalize_text(text):
    text = text.lower()
    text = text.replace("c++", "cplusplus").replace("c#", "csharp").replace("node.js", "nodejs")
    text = re.sub(r"[^a-z0-9\s.+#/-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace("cplusplus", "c++").replace("csharp", "c#").replace("nodejs", "node.js")


def extract_skills(text):
    normalized = normalize_text(text)
    found = set()
    for raw_skill in SKILL_CATALOG:
        skill = normalize_text(raw_skill)
        pattern = r"(?<![a-z0-9+#.])" + re.escape(skill) + r"(?![a-z0-9+#.])"
        if re.search(pattern, normalized):
            found.add(ALIASES.get(skill, skill))

    tokens = set(re.findall(r"[a-z0-9.+#/-]+", normalized))
    for alias, canonical in ALIASES.items():
        if alias in tokens or alias in normalized:
            found.add(canonical)
    return sorted(found)


def infer_skill_domain(skill):
    for domain, skills in SKILL_DOMAINS.items():
        if skill in skills:
            return domain
    return "Mixed Skills"


def compare_resume_to_jd(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)
    extra = sorted(resume_set - jd_set)
    match_score = 0 if not jd_skills else round((len(matched) / len(jd_skills)) * 100)

    cluster_map = {}
    for skill in sorted(resume_set | jd_set):
        cluster_map.setdefault(infer_skill_domain(skill), {"matched": 0, "missing": 0, "resume_only": 0})
        if skill in matched:
            cluster_map[infer_skill_domain(skill)]["matched"] += 1
        elif skill in missing:
            cluster_map[infer_skill_domain(skill)]["missing"] += 1
        else:
            cluster_map[infer_skill_domain(skill)]["resume_only"] += 1

    cluster_summary = []
    for cluster_name, counts in sorted(cluster_map.items()):
        jd_count = counts["matched"] + counts["missing"]
        coverage = 100 if jd_count == 0 else round((counts["matched"] / jd_count) * 100)
        priority = "High" if counts["missing"] >= 3 else "Medium" if counts["missing"] else "Low"
        cluster_summary.append(
            {
                "cluster_name": cluster_name,
                "matched": counts["matched"],
                "missing": counts["missing"],
                "resume_only": counts["resume_only"],
                "coverage": coverage,
                "priority": priority,
            }
        )

    recommendations = [
        {
            "skill": skill,
            "suggestion": COURSE_SUGGESTIONS.get(
                skill,
                f"Learn {skill} basics, complete a mini project, and add it to your resume.",
            ),
        }
        for skill in missing
    ]
    return {
        "match_score": match_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
        "cluster_summary": sorted(cluster_summary, key=lambda row: row["missing"], reverse=True),
        "gap_priority": [
            {
                "skill": skill,
                "cluster_name": infer_skill_domain(skill),
                "priority": "High",
                "why_it_matters": f"Strengthens the {infer_skill_domain(skill).lower()} cluster required by this role.",
            }
            for skill in missing
        ],
        "recommendations": recommendations,
    }


def score_multiple_jobs(resume_text, job_descriptions):
    rows = []
    for role, jd_text in job_descriptions.items():
        result = compare_resume_to_jd(resume_text, jd_text)
        rows.append(
            {
                "role": role,
                "match_score": result["match_score"],
                "matched_skills": ", ".join(result["matched_skills"]) or "None",
                "missing_skills": ", ".join(result["missing_skills"]) or "None",
            }
        )
    return sorted(rows, key=lambda row: row["match_score"], reverse=True)


def result_payload(resume_text, jd_text):
    result = compare_resume_to_jd(resume_text, jd_text)
    ranking = score_multiple_jobs(resume_text, SAMPLE_MULTI_JDS)
    return {
        "match_score": result["match_score"],
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"],
        "extra_skills": result["extra_skills"],
        "cluster_summary": dataframe_records(result["cluster_summary"]),
        "gap_priority": dataframe_records(result["gap_priority"]),
        "recommendations": result["recommendations"],
        "ranking": dataframe_records(ranking),
    }


def render_page(payload=None, resume_text=SAMPLE_RESUME, jd_text=SAMPLE_JD):
    payload = payload or result_payload(resume_text, jd_text)
    cluster_rows = "".join(
        "<tr>"
        f"<td>{escape(str(row['cluster_name']))}</td>"
        f"<td>{escape(str(row['matched']))}</td>"
        f"<td>{escape(str(row['missing']))}</td>"
        f"<td>{escape(str(row['coverage']))}%</td>"
        f"<td>{escape(str(row['priority']))}</td>"
        "</tr>"
        for row in payload["cluster_summary"]
    )
    recommendation_rows = "".join(
        "<tr>"
        f"<td>{escape(title_skill(row['skill']))}</td>"
        f"<td>{escape(row['suggestion'])}</td>"
        "</tr>"
        for row in payload["recommendations"]
    )
    ranking_rows = "".join(
        "<tr>"
        f"<td>{escape(row['role'])}</td>"
        f"<td>{escape(str(row['match_score']))}%</td>"
        f"<td>{escape(row['missing_skills'])}</td>"
        "</tr>"
        for row in payload["ranking"]
    )

    return f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Resume Skill Gap Analyzer</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                background: #f5f7fb;
                color: #0f172a;
                font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}
            main {{ max-width: 1180px; margin: 0 auto; padding: 28px 18px 44px; }}
            header {{
                background: #ffffff;
                border: 1px solid #dbe3ef;
                border-radius: 8px;
                padding: 18px 20px;
                margin-bottom: 18px;
            }}
            h1 {{ font-size: 2rem; margin: 0 0 8px; }}
            h2 {{ font-size: 1.05rem; margin: 0 0 14px; }}
            p {{ color: #475569; margin: 0; line-height: 1.5; }}
            form, section {{
                background: #ffffff;
                border: 1px solid #dbe3ef;
                border-radius: 8px;
                padding: 16px;
            }}
            .grid {{ display: grid; gap: 16px; grid-template-columns: minmax(0, 0.82fr) minmax(0, 1.18fr); }}
            .cards {{ display: grid; gap: 12px; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-bottom: 16px; }}
            .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; }}
            .label {{ color: #64748b; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; }}
            .value {{ font-size: 1.9rem; font-weight: 800; margin-top: 6px; }}
            label {{ color: #334155; display: block; font-weight: 700; margin-bottom: 8px; }}
            textarea {{
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                font: inherit;
                min-height: 210px;
                padding: 12px;
                resize: vertical;
                width: 100%;
            }}
            .field {{ margin-bottom: 14px; }}
            button {{
                background: #2563eb;
                border: 0;
                border-radius: 8px;
                color: #ffffff;
                cursor: pointer;
                font: inherit;
                font-weight: 800;
                padding: 12px 16px;
                width: 100%;
            }}
            .panel {{ margin-bottom: 16px; }}
            .chip-row {{ display: flex; flex-wrap: wrap; gap: 8px; }}
            .chip {{ border-radius: 8px; display: inline-flex; font-size: 0.88rem; font-weight: 700; padding: 7px 10px; }}
            .match {{ background: #e8fff3; color: #127a46; }}
            .missing {{ background: #fff1f2; color: #be123c; }}
            .extra {{ background: #eef6ff; color: #1d4ed8; }}
            .muted {{ color: #64748b; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border-bottom: 1px solid #e2e8f0; padding: 10px 8px; text-align: left; vertical-align: top; }}
            th {{ color: #475569; font-size: 0.78rem; text-transform: uppercase; }}
            @media (max-width: 860px) {{
                .grid, .cards {{ grid-template-columns: 1fr; }}
                textarea {{ min-height: 170px; }}
            }}
        </style>
    </head>
    <body>
        <main>
            <header>
                <h1>Resume Skill Gap Analyzer</h1>
                <p>Compare a resume with a job description, detect missing skills, and prioritize learning gaps with NLP and K-Means clustering.</p>
            </header>
            <div class="grid">
                <form method="post">
                    <div class="field">
                        <label for="resume_text">Resume text</label>
                        <textarea id="resume_text" name="resume_text">{escape(resume_text)}</textarea>
                    </div>
                    <div class="field">
                        <label for="jd_text">Job description text</label>
                        <textarea id="jd_text" name="jd_text">{escape(jd_text)}</textarea>
                    </div>
                    <button type="submit">Analyze Resume</button>
                </form>
                <div>
                    <div class="cards">
                        <div class="card"><div class="label">Match Score</div><div class="value">{payload['match_score']}%</div></div>
                        <div class="card"><div class="label">Matched</div><div class="value">{len(payload['matched_skills'])}</div></div>
                        <div class="card"><div class="label">Missing</div><div class="value">{len(payload['missing_skills'])}</div></div>
                    </div>
                    <section class="panel">
                        <h2>Matched Skills</h2>
                        <div class="chip-row">{chip_list(payload['matched_skills'], 'match')}</div>
                    </section>
                    <section class="panel">
                        <h2>Missing Skills</h2>
                        <div class="chip-row">{chip_list(payload['missing_skills'], 'missing')}</div>
                    </section>
                    <section class="panel">
                        <h2>Resume Only Skills</h2>
                        <div class="chip-row">{chip_list(payload['extra_skills'], 'extra')}</div>
                    </section>
                    <section class="panel">
                        <h2>Cluster Coverage</h2>
                        <table>
                            <thead><tr><th>Cluster</th><th>Matched</th><th>Missing</th><th>Coverage</th><th>Priority</th></tr></thead>
                            <tbody>{cluster_rows or "<tr><td colspan='5'>No cluster data found.</td></tr>"}</tbody>
                        </table>
                    </section>
                    <section class="panel">
                        <h2>Improvement Suggestions</h2>
                        <table>
                            <thead><tr><th>Skill</th><th>Suggestion</th></tr></thead>
                            <tbody>{recommendation_rows or "<tr><td colspan='2'>No missing JD skills were detected.</td></tr>"}</tbody>
                        </table>
                    </section>
                    <section>
                        <h2>Multiple JD Ranking</h2>
                        <table>
                            <thead><tr><th>Role</th><th>Score</th><th>Missing Skills</th></tr></thead>
                            <tbody>{ranking_rows}</tbody>
                        </table>
                    </section>
                </div>
            </div>
        </main>
    </body>
    </html>
    """


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        resume_text = request.form.get("resume_text", "").strip()
        jd_text = request.form.get("jd_text", "").strip()
        if resume_text and jd_text:
            return render_page(result_payload(resume_text, jd_text), resume_text, jd_text)
    return render_page()


@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    resume_text = data.get("resume_text", "")
    jd_text = data.get("jd_text", "")
    if not resume_text.strip() or not jd_text.strip():
        return jsonify({"error": "resume_text and jd_text are required"}), 400
    return jsonify(result_payload(resume_text, jd_text))
