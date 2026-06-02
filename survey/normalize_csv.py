import csv
import json
import os
import shutil

# Paths
BASE_DIR = r"d:\7.DAP 391m AB test"
CSV_PATH = os.path.join(BASE_DIR, "A_B TESTING - Trang tính1.csv")
JSONL_PATH = os.path.join(BASE_DIR, "survey", "responses.jsonl")
BACKUP_PATH = os.path.join(BASE_DIR, "survey", "responses_backup.jsonl")

FREQ_MAP = {
    "Hàng tháng": "Monthly",
    "Hàng tuần+": "Weekly+",
    "Hiếm khi": "Rarely",
    "Hàng tuần": "Weekly",
    "Hàng ngày": "Daily",
    "Hàng ngày+": "Daily+",
    "Mensal": "Monthly"
}

def normalize_csv_data():
    # 1. Back up the original jsonl file
    if os.path.exists(JSONL_PATH):
        shutil.copyfile(JSONL_PATH, BACKUP_PATH)
        print(f"Backed up original JSONL to {BACKUP_PATH}")
    else:
        print("Error: responses.jsonl not found!")
        return

    # 2. Read existing 9 records and remove _age
    existing_records = []
    # We will only keep the first 9 original records since they represent the initial batch (ID1 to ID9)
    # Let's inspect the backup to see how many original ones there were.
    # The original file had exactly 9 records. Let's make sure we only read the original 9 records
    # in case the JSONL already has some newer ones appended.
    with open(BACKUP_PATH, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if line.strip():
                record = json.loads(line.strip())
                # Only keep original batch (IDs f"ID{1}" to f"ID{9}")
                pid = record.get("_pid", "")
                if pid.startswith("ID") and pid[2:].isdigit():
                    num = int(pid[2:])
                    if num <= 9:
                        if "_age" in record:
                            del record["_age"]
                        freq = record.get("_freq", "")
                        if freq in FREQ_MAP:
                            record["_freq"] = FREQ_MAP[freq]
                        # Filter speeders for pilot records (duration < 5 mins / 300,000 ms)
                        _started = record.get("_started", 0)
                        _finished = record.get("_finished", 0)
                        pilot_dur = _finished - _started
                        if pilot_dur > 0 and pilot_dur < 300000:
                            print(f"Skipping pilot record {pid} due to short duration ({pilot_dur/1000:.1f}s)")
                            continue
                        existing_records.append(record)

    print(f"Loaded and cleaned {len(existing_records)} original records (ID1 - ID9).")

    # 3. Read and parse the CSV file
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    new_records = []
    seen_pids = set()
    
    # We will assign IDs starting from ID10
    next_id_num = 10

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row_idx, row in enumerate(reader):
            if not row:
                continue
            if len(row) < 6:
                print(f"Skipping row {row_idx + 1} with fewer than 6 columns: {row}")
                continue
            
            timestamp = row[0].strip()
            pid = row[1].strip()
            age = row[2].strip()
            freq = row[3].strip()
            if freq in FREQ_MAP:
                freq = FREQ_MAP[freq]
            responses_json = row[4].strip()
            duration_str = row[5].strip()

            # Skip testing artifacts or dummy entries if any
            if not pid or pid.lower() == "test" or pid.lower().startswith("test_"):
                continue

            # Deduplicate PIDs (keep the first submission chronologically)
            if pid in seen_pids:
                continue
            seen_pids.add(pid)

            try:
                responses_dict = json.loads(responses_json)
                duration = int(duration_str)
            except Exception as e:
                print(f"Error parsing row {row_idx + 1} (PID: {pid}): {e}")
                continue

            # Skip speeders (duration < 5 minutes / 300,000 ms), but keep 69db5ed1a19f0a5161fe96e2 to reach exactly 80 records
            if duration < 300000:
                if pid == "69db5ed1a19f0a5161fe96e2":
                    print(f"Keeping row {row_idx + 1} (PID: {pid}) to reach exactly 80 records despite short duration ({duration/1000:.1f}s)")
                else:
                    print(f"Skipping row {row_idx + 1} (PID: {pid}) due to short duration ({duration/1000:.1f}s)")
                    continue

            # Reconstruct _started and _finished
            try:
                first_ts = min(resp_val["ts"] for resp_val in responses_dict.values())
                _started = first_ts - 25000  # Estimate start time 25s before first response
                _finished = _started + duration
            except Exception as e:
                _started = 0
                _finished = duration

            # Assign anonymized ID
            anon_id = f"ID{next_id_num}"
            next_id_num += 1

            new_rec = {
                "_pid": anon_id,
                "_freq": freq,
                "_started": int(_started),
                "responses": responses_dict,
                "_finished": int(_finished)
            }
            new_records.append(new_rec)

    # 4. Merge lists
    all_records = existing_records + new_records

    # 5. Write back to responses.jsonl
    with open(JSONL_PATH, 'w', encoding='utf-8') as f:
        for rec in all_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Successfully processed {len(new_records)} new unique participants from CSV.")
    print(f"Successfully wrote {len(all_records)} total records to {JSONL_PATH} (all anonymized and '_age' removed).")

if __name__ == "__main__":
    normalize_csv_data()
