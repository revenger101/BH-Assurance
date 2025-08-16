import pandas as pd
import os
import re
from PyPDF2 import PdfReader
from pathlib import Path


def find_column(df, keywords):
    """
    Find the first column whose name contains any of the keywords.
    Case-insensitive and ignores spaces/accents.
    """
    normalized_cols = {c: c.lower().strip() for c in df.columns}
    for col, norm in normalized_cols.items():
        for kw in keywords:
            if kw in norm:
                return col
    return None


def rows_from_excel(path):
    df = pd.read_excel(path)

    # Keywords for Q and A detection
    q_keywords = ["question", "quest", "demande"]
    a_keywords = ["answer", "réponse", "response", "reponse"]

    qcol = find_column(df, q_keywords)
    acol = find_column(df, a_keywords)

    if not qcol or not acol:
        raise RuntimeError(
            f"❌ Could not find matching Q/A columns in {path}. "
            f"Found columns: {list(df.columns)}"
        )

    for _, row in df.iterrows():
        if pd.isna(row[qcol]) or pd.isna(row[acol]):
            continue
        yield {
            "question": str(row[qcol]).strip(),
            "answer": str(row[acol]).strip()
        }


def rows_from_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"

    qa_pairs = re.findall(
        r"Q[:\-]?\s*(.*?)\s*A[:\-]?\s*(.*?)(?=Q[:\-]|\Z)",
        text,
        re.DOTALL | re.IGNORECASE
    )

    for q, a in qa_pairs:
        yield {
            "question": q.strip(),
            "answer": a.strip()
        }


def main():
    dataset = []
    data_dir = os.path.join("data", "raw")

    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"❌ Data folder not found: {data_dir}")

    for file in os.listdir(data_dir):
        path = os.path.join(data_dir, file)
        if file.lower().endswith(".xlsx"):
            dataset.extend(rows_from_excel(path))
        elif file.lower().endswith(".pdf"):
            dataset.extend(rows_from_pdf(path))

    out_path = os.path.join("data", "qa_dataset.csv")
    pd.DataFrame(dataset).to_csv(out_path, index=False, encoding="utf-8")
    print(f"✅ Dataset saved to {out_path} with {len(dataset)} rows.")


if __name__ == "__main__":
    main()

def excel_to_qa(file_path, output_path):
    df = pd.read_excel(file_path)

    qa_rows = []

    for _, row in df.iterrows():
        name = f"{row['Nom']} {row['Prénom']}"
        
        qa_rows.append({
            "question": f"What is the profession of {name}?",
            "answer": row["Profession"]
        })
        qa_rows.append({
            "question": f"What is the birthdate of {name}?",
            "answer": str(row["DateNaissance"])
        })
        qa_rows.append({
            "question": f"What is the monthly income of {name}?",
            "answer": str(row["RevenusMensuels"])
        })
        qa_rows.append({
            "question": f"What is the marital status of {name}?",
            "answer": row["SituationFamiliale"]
        })
        # Add more Q/A pairs if needed

    qa_df = pd.DataFrame(qa_rows)
    qa_df.to_csv(output_path, index=False)
    print(f"✅ Q&A dataset saved to {output_path} with {len(qa_rows)} rows.")

if __name__ == "__main__":
    input_file = Path("data/raw/Données_Assurance_S1.xlsx")
    output_file = Path("data/qa_dataset_clients.csv")
    excel_to_qa(input_file, output_file)