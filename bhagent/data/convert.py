import pandas as pd
import json

csv_path = "qa_dataset.csv"
jsonl_path = "qa_dataset_ft.jsonl"

df = pd.read_csv(csv_path, encoding="utf-8")

with open(jsonl_path, "w", encoding="utf-8") as f:
    for _, row in df.iterrows():
        prompt = str(row["question"]).strip() + "\n\n###\n\n"
        completion = " " + str(row["answer"]).strip() + " END"  
        json_record = {"prompt": prompt, "completion": completion}
        f.write(json.dumps(json_record, ensure_ascii=False) + "\n")

print(f"✅ JSONL dataset saved to {jsonl_path} with {len(df)} records")
