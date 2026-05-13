# Resume Skill Gap Analyzer

This project uses unsupervised learning and NLP to compare a candidate's resume with job descriptions, cluster required skills, and identify missing skills with improvement suggestions.

## Features

- Upload a resume PDF or paste resume text.
- Paste a job description.
- Extract resume and JD skills with NLP preprocessing.
- Vectorize skills using TF-IDF.
- Cluster skills using K-Means with silhouette-based cluster selection.
- Label clusters by skill domain and show cluster coverage.
- Prioritize missing skills by unsupervised cluster gaps.
- Calculate a skill match score.
- Detect missing, matched, and resume-only skills.
- Recommend courses, practice areas, and mini projects.
- Show dashboard cards, gauges, radar view, skill clusters, keyword extraction, and multiple JD ranking.

## Tech Stack

- Python
- Streamlit
- Pandas and NumPy
- Scikit-learn
- pypdf
- Plotly

## Project Workflow

1. Input resume and job description.
2. Preprocess text using tokenization, stopword removal, and light lemmatization.
3. Extract skills from a predefined skill catalog and aliases.
4. Convert skills into TF-IDF vectors.
5. Apply K-Means clustering to group similar skills.
6. Use silhouette score to choose a suitable cluster count.
7. Compare resume skills with JD skills.
8. Display match score, missing skills, cluster coverage, gap priority, and recommendations.

## How To Run

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

On Windows PowerShell, you can also run:

```powershell
.\run_app.ps1
```

## Viva Explanation

This project compares a resume against a job description using NLP and unsupervised learning. First, it cleans and tokenizes the text, removes stopwords, and applies simple lemmatization. Then it extracts important technical skills from both documents. The extracted skills are converted into TF-IDF vectors. K-Means clustering groups related skills, and silhouette scoring helps choose the best cluster count for the current input. The dashboard labels clusters by domain, measures cluster coverage, and highlights which missing skills should be learned first. Finally, the system calculates the match score and recommends learning paths and mini projects.

## Example

Resume skills:

```text
Python, SQL, HTML, CSS
```

Job description skills:

```text
Python, SQL, Machine Learning, AWS
```

Output:

```text
Matched: Python, SQL
Missing: Machine Learning, AWS
Match Score: 50%
```

## Dataset Ideas

- Kaggle Resume Dataset
- Kaggle Job Description Dataset
- Custom job descriptions from company career pages

## Future Enhancements

- Add Sentence-BERT embeddings for deeper semantic matching.
- Add spaCy named entity recognition.
- Add resume section detection.
- Add GPT-based personalized suggestions.
- Store analyzed resumes in a database.
