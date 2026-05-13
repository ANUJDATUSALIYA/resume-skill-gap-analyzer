import re
from collections import Counter, defaultdict

from dependency_guard import disable_optional_pyarrow

disable_optional_pyarrow()

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics import silhouette_score


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


def normalize_text(text):
    text = text.lower()
    text = text.replace("c++", "cplusplus").replace("c#", "csharp").replace("node.js", "nodejs")
    text = re.sub(r"[^a-z0-9\s.+#/-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("cplusplus", "c++").replace("csharp", "c#").replace("nodejs", "node.js")
    return text


def preprocess_text(text):
    normalized = normalize_text(text)
    tokens = re.findall(r"[a-z0-9.+#/-]+", normalized)
    cleaned = []
    for token in tokens:
        if token in ENGLISH_STOP_WORDS or len(token) <= 1:
            continue
        cleaned.append(lemmatize_light(token))
    return cleaned


def lemmatize_light(token):
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ing") and len(token) > 5:
        return token[:-3]
    if token.endswith("ed") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and len(token) > 3 and token not in {"aws", "css"}:
        return token[:-1]
    return token


def extract_skills(text, skill_catalog=None):
    skill_catalog = skill_catalog or SKILL_CATALOG
    normalized = normalize_text(text)
    found = set()

    for raw_skill in skill_catalog:
        skill = normalize_text(raw_skill)
        pattern = r"(?<![a-z0-9+#.])" + re.escape(skill) + r"(?![a-z0-9+#.])"
        if re.search(pattern, normalized):
            found.add(ALIASES.get(skill, skill))

    tokens = set(preprocess_text(text))
    for alias, canonical in ALIASES.items():
        alias_tokens = alias.split()
        if len(alias_tokens) == 1 and alias in tokens:
            found.add(canonical)
        elif alias in normalized:
            found.add(canonical)

    return sorted(found)


def extract_keywords(text, limit=15):
    tokens = preprocess_text(text)
    counts = Counter(tokens)
    blocked = set(SKILL_CATALOG) | set(ENGLISH_STOP_WORDS)
    keywords = [
        word
        for word, _ in counts.most_common()
        if len(word) > 2 and word not in blocked and not word.isdigit()
    ]
    return keywords[:limit]


def cluster_skills(skills, max_clusters=4):
    if not skills:
        return pd.DataFrame(columns=["skill", "cluster", "cluster_id", "cluster_name", "confidence"])

    if len(skills) == 1:
        return pd.DataFrame(
            [
                {
                    "skill": skills[0],
                    "cluster": "Cluster 1",
                    "cluster_id": 0,
                    "cluster_name": infer_skill_domain([skills[0]]),
                    "confidence": 1.0,
                }
            ]
        )

    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
    matrix = vectorizer.fit_transform(skills)
    cluster_count = choose_cluster_count(matrix, len(skills), max_clusters)

    model = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
    labels = model.fit_predict(matrix)
    distances = model.transform(matrix)
    confidence = []
    for row, label in zip(distances, labels):
        nearest = row[label]
        second_nearest = np.partition(row, 1)[1] if len(row) > 1 else nearest
        if second_nearest == 0:
            confidence.append(1.0)
        else:
            confidence.append(round(float(max(0, 1 - nearest / second_nearest)), 2))

    rows = pd.DataFrame(
        {
            "skill": skills,
            "cluster_id": labels,
            "confidence": confidence,
        }
    )
    cluster_names = {
        cluster_id: infer_skill_domain(rows.loc[rows["cluster_id"] == cluster_id, "skill"].tolist())
        for cluster_id in sorted(rows["cluster_id"].unique())
    }
    rows["cluster"] = rows["cluster_id"].map(lambda label: f"Cluster {label + 1}")
    rows["cluster_name"] = rows["cluster_id"].map(cluster_names)
    return rows[["skill", "cluster", "cluster_id", "cluster_name", "confidence"]].sort_values(
        ["cluster", "skill"]
    )


def choose_cluster_count(matrix, skill_count, max_clusters):
    if skill_count <= 3:
        return skill_count

    upper = min(max_clusters, skill_count - 1)
    best_score = -1
    best_count = min(3, upper)
    dense_matrix = matrix.toarray()

    for count in range(2, upper + 1):
        model = KMeans(n_clusters=count, random_state=42, n_init=10)
        labels = model.fit_predict(matrix)
        if len(set(labels)) < 2:
            continue
        score = silhouette_score(dense_matrix, labels)
        if score > best_score:
            best_score = score
            best_count = count

    return best_count


def infer_skill_domain(skills):
    votes = Counter()
    skill_set = set(skills)
    for domain, domain_skills in SKILL_DOMAINS.items():
        votes[domain] = len(skill_set & domain_skills)
    if not votes or votes.most_common(1)[0][1] == 0:
        return "Mixed Skills"
    top_votes = votes.most_common(2)
    if len(top_votes) > 1 and top_votes[0][1] == top_votes[1][1]:
        return "Mixed Skills"
    return top_votes[0][0]


def calculate_match_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    return round((len(resume_set & jd_set) / len(jd_set)) * 100)


def build_recommendations(missing_skills):
    recommendations = []
    for skill in missing_skills:
        suggestions = COURSE_SUGGESTIONS.get(
            skill,
            f"Learn {skill} basics, complete a mini project, and add it to your resume.",
        )
        recommendations.append({"skill": skill, "suggestion": suggestions})
    return recommendations


def build_cluster_summary(cluster_table):
    if cluster_table.empty:
        return pd.DataFrame(
            columns=[
                "cluster",
                "cluster_name",
                "total_skills",
                "matched",
                "missing",
                "resume_only",
                "coverage",
                "priority",
            ]
        )

    summary = (
        cluster_table.groupby(["cluster", "cluster_name"])
        .agg(
            total_skills=("skill", "count"),
            matched=("status", lambda values: int((values == "Matched").sum())),
            missing=("status", lambda values: int((values == "Missing").sum())),
            resume_only=("status", lambda values: int((values == "Resume only").sum())),
        )
        .reset_index()
    )
    summary["jd_cluster_skills"] = summary["matched"] + summary["missing"]
    summary["coverage"] = summary.apply(
        lambda row: 100
        if row["jd_cluster_skills"] == 0
        else round((row["matched"] / row["jd_cluster_skills"]) * 100),
        axis=1,
    )
    summary["priority_score"] = summary.apply(
        lambda row: 0 if row["missing"] == 0 else row["missing"] * 2 + (100 - row["coverage"]) / 25,
        axis=1,
    )
    summary["priority"] = summary["priority_score"].apply(priority_label)
    return summary.sort_values(["priority_score", "missing"], ascending=False).drop(
        columns=["priority_score", "jd_cluster_skills"]
    )


def priority_label(score):
    if score >= 6:
        return "High"
    if score >= 3:
        return "Medium"
    return "Low"


def build_gap_priority_table(cluster_table):
    if cluster_table.empty:
        return pd.DataFrame(columns=["skill", "cluster_name", "priority", "why_it_matters"])

    missing = cluster_table[cluster_table["status"] == "Missing"].copy()
    if missing.empty:
        return pd.DataFrame(columns=["skill", "cluster_name", "priority", "why_it_matters"])

    cluster_missing_counts = missing.groupby("cluster")["skill"].transform("count")
    missing["priority_rank"] = cluster_missing_counts.rank(method="dense", ascending=False).astype(int)
    missing["priority"] = missing["priority_rank"].map({1: "High", 2: "Medium"}).fillna("Low")
    missing["why_it_matters"] = missing["cluster_name"].apply(
        lambda name: f"Strengthens the {name.lower()} cluster required by this role."
    )
    missing = missing.sort_values(["priority_rank", "cluster_name", "skill"])
    return missing[["skill", "cluster_name", "priority", "why_it_matters"]]


def compare_resume_to_jd(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)
    extra = sorted(resume_set - jd_set)
    all_skills = sorted(resume_set | jd_set)

    cluster_table = cluster_skills(all_skills)
    if not cluster_table.empty:
        status_by_skill = {}
        for skill in matched:
            status_by_skill[skill] = "Matched"
        for skill in missing:
            status_by_skill[skill] = "Missing"
        for skill in extra:
            status_by_skill[skill] = "Resume only"
        cluster_table["status"] = cluster_table["skill"].map(status_by_skill)
    cluster_summary = build_cluster_summary(cluster_table)
    gap_priority = build_gap_priority_table(cluster_table)

    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
        "match_score": calculate_match_score(resume_skills, jd_skills),
        "cluster_table": cluster_table,
        "cluster_summary": cluster_summary,
        "gap_priority": gap_priority,
        "recommendations": build_recommendations(missing),
        "resume_keywords": extract_keywords(resume_text),
        "jd_keywords": extract_keywords(jd_text),
    }


def summarize_clusters(cluster_table):
    if cluster_table.empty:
        return {}
    grouped = defaultdict(list)
    for _, row in cluster_table.iterrows():
        grouped[f"{row['cluster']} - {row['cluster_name']}"].append(row["skill"])
    return dict(grouped)


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
    return pd.DataFrame(rows).sort_values("match_score", ascending=False)


def radar_values(result):
    jd_count = max(len(result["jd_skills"]), 1)
    resume_count = max(len(result["resume_skills"]), 1)
    return {
        "JD coverage": result["match_score"],
        "Resume focus": round((len(result["matched_skills"]) / resume_count) * 100),
        "Gap size": round((len(result["missing_skills"]) / jd_count) * 100),
    }
