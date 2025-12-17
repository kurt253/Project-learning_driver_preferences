from pathlib import Path
import json
import re
import sys
import pandas as pd

# -----------------------
# Paths (project-relative)
# -----------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

REQUESTS_ROOT = PROJECT_ROOT / "data" / "input" / "requests"
INTERMEDIATE_FOLDER = PROJECT_ROOT / "data" / "intermediate"
INTERMEDIATE_FOLDER.mkdir(parents=True, exist_ok=True)

# -----------------------
# Subfolder selection
# -----------------------
# Gebruik:
#   python ParseRequests.py
#   python ParseRequests.py 0521_301-20220610
#   python ParseRequests.py "0521_301-20220610/something"
subfolder_arg = sys.argv[1] if len(sys.argv) > 1 else None

if subfolder_arg:
    selected_folder = (REQUESTS_ROOT / subfolder_arg).resolve()
    if not selected_folder.exists():
        raise FileNotFoundError(f"❌ Subfolder bestaat niet: {selected_folder}")
    if REQUESTS_ROOT not in selected_folder.parents and selected_folder != REQUESTS_ROOT:
        raise ValueError(f"❌ Subfolder moet onder {REQUESTS_ROOT} zitten.")
else:
    selected_folder = REQUESTS_ROOT

# -----------------------
# Find JSON files
# -----------------------
json_files = list(selected_folder.rglob("*.json"))
print(f"JSON files gevonden: {len(json_files)}")

if not json_files:
    raise RuntimeError("❌ Geen .json files gevonden in de gekozen folder.")

# -----------------------
# Parse JSON -> rows
# -----------------------
rows = []

for file in json_files:
    try:
        with file.open(encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"⚠️ Skip file (kan niet gelezen worden): {file} ({e})")
        continue

    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        continue

    for task in tasks:
        address = task.get("address", {})
        rows.append({
            "task_id": task.get("id"),
            "longitude": address.get("longitude"),
            "latitude": address.get("latitude"),
        })

df = pd.DataFrame(rows)
print(f"Ingelezen rows (voor cleaning): {len(df)}")

if df.empty:
    raise RuntimeError("❌ Rows=0. Files gevonden, maar geen bruikbare 'tasks' in de JSONs.")

# -----------------------
# Clean + dedupe
# -----------------------
df_clean = (
    df.dropna(subset=["task_id", "longitude", "latitude"])
      .drop_duplicates(subset=["task_id", "longitude", "latitude"])
      .reset_index(drop=True)
)

print(f"Na deduplicatie: {len(df_clean)} (dubbels verwijderd: {len(df) - len(df_clean)})")

# Sort: numerieke task_id eerst, daarna alfanumeriek
df_clean["task_id_num"] = pd.to_numeric(df_clean["task_id"], errors="coerce")
df_clean["task_id_is_num"] = df_clean["task_id_num"].notna()

df_sorted = (
    df_clean
    .sort_values(
        by=["task_id_is_num", "task_id_num", "task_id"],
        ascending=[False, True, True]
    )
    [["task_id", "longitude", "latitude"]]
)

# -----------------------
# Output filename (append subfolder if used)
# -----------------------
def slug(s: str) -> str:
    s = s.strip().replace("\\", "/")
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    return s.strip("_") or "all"

suffix = slug(subfolder_arg) if subfolder_arg else "all"
output_path = INTERMEDIATE_FOLDER / f"tasks_clean_sorted__{suffix}.json"

df_sorted.to_json(output_path, orient="records", indent=2)

print(f"✅ Output geschreven: {output_path}")
print(f"📦 Records: {len(df_sorted)}")
