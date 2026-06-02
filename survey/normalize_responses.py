import json
import os
import shutil

# Paths
BASE_DIR = r"d:\7.DAP 391m AB test\survey"
JSONL_PATH = os.path.join(BASE_DIR, "responses.jsonl")
BACKUP_PATH = os.path.join(BASE_DIR, "responses_backup.jsonl")

# Raw data copied from Google Sheets
RAW_SHEET_DATA = """
01/06/2026 22:22:24	Linh	18-24	Monthly	{"UI-01":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327069340},"UI-03":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327081131},"UI-06":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327094107},"UI-07":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327113759},"UI-09":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327131399},"UI-10":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327156478},"UI-11":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327175205},"UI-12":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327183213},"COPY-04":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327190269},"COPY-05":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327198805},"COPY-06":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327208039},"COPY-08":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327223930},"COPY-09":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327233934},"COPY-10":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327244980},"COPY-11":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327262387},"REC-01":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327269892},"REC-02":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327280691},"REC-03":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327288243},"REC-04":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327300042},"REC-06":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327318682},"REC-07":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327325632},"REC-08":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327332212},"REC-11":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327340747}}	307011
01/06/2026 22:23:26	rater_3vw50g	18-24	Rarely	{"UI-01":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327305163},"UI-03":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327322395},"UI-06":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327326243},"UI-07":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327332907},"UI-09":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327338243},"UI-10":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327341419},"UI-11":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327346347},"UI-12":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327348475},"COPY-04":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327352468},"COPY-05":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327360915},"COPY-06":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327363747},"COPY-08":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327366323},"COPY-09":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327368916},"COPY-10":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327372468},"COPY-11":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327376436},"REC-01":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327380268},"REC-02":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327382669},"REC-03":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327385924},"REC-04":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327388916},"REC-06":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327391164},"REC-07":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327394237},"REC-08":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327396036},"REC-11":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327402060}}	110297
01/06/2026 22:25:13	Trần Nhật Ánh	18-24	Monthly	{"UI-01":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327178432},"UI-03":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327215819},"UI-06":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327237998},"UI-07":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327256690},"UI-09":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327280509},"UI-10":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327295754},"UI-11":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327307544},"UI-12":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327320671},"COPY-04":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327322955},"COPY-05":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327364670},"COPY-06":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327373156},"COPY-08":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327380211},"COPY-09":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327391792},"COPY-10":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327404591},"COPY-11":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327417197},"REC-01":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327428899},"REC-02":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327436552},"REC-03":{"chosen_opt":"opt2","chosen_sem":"B","ts":1780327449782},"REC-04":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327456430},"REC-06":{"chosen_opt":"opt1","chosen_sem":"B","ts":1780327468190},"REC-07":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327474238},"REC-08":{"chosen_opt":"opt2","chosen_sem":"A","ts":1780327497169},"REC-11":{"chosen_opt":"opt1","chosen_sem":"A","ts":1780327511137}}	355340
"""

def clean_and_normalize():
    # 1. Back up the original file
    if os.path.exists(JSONL_PATH):
        shutil.copyfile(JSONL_PATH, BACKUP_PATH)
        print(f"Backed up original file to {BACKUP_PATH}")
    else:
        print("Error: responses.jsonl not found!")
        return

    # 2. Read existing responses and strip "_age"
    existing_records = []
    with open(JSONL_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                record = json.loads(line.strip())
                # Remove _age if exists
                if "_age" in record:
                    del record["_age"]
                existing_records.append(record)

    print(f"Read {len(existing_records)} existing records.")

    # 3. Parse new raw data
    new_records = []
    seen_pids = set()
    
    # Track the next ID number
    next_id_num = len(existing_records) + 1

    lines = RAW_SHEET_DATA.strip().split("\n")
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 6:
            # Let's try splitting by multiple spaces/tabs
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) < 6:
                print(f"Skipping malformed line: {line[:50]}...")
                continue
        
        # Columns: Time, PID, Age, Frequency, Responses (JSON), Duration
        # Let's map indexes based on tab split
        timestamp_str = parts[0].strip()
        pid = parts[1].strip()
        age = parts[2].strip()
        freq = parts[3].strip()
        responses_json = parts[4].strip()
        duration_str = parts[5].strip()
        
        # Avoid duplicate PIDs in new data
        if pid in seen_pids:
            print(f"Skipping duplicate PID in raw data: {pid}")
            continue
        seen_pids.add(pid)

        try:
            responses_dict = json.loads(responses_json)
            duration = int(duration_str)
        except Exception as e:
            print(f"Error parsing JSON or duration for PID {pid}: {e}")
            continue

        # Find first response timestamp to reconstruct start/finish times
        try:
            first_ts = min(resp_val["ts"] for resp_val in responses_dict.values())
            _started = first_ts - 25000  # Estimate start time 25s before first response
            _finished = _started + duration
        except Exception as e:
            # Fallback
            _started = 0
            _finished = duration

        # Assign anonymized ID
        anon_id = f"ID{next_id_num}"
        next_id_num += 1

        # Build clean record (NO _age field!)
        new_rec = {
            "_pid": anon_id,
            "_freq": freq,
            "_started": int(_started),
            "responses": responses_dict,
            "_finished": int(_finished)
        }
        new_records.append(new_rec)
        print(f"Anonymized new participant -> {anon_id} (Frequency: {freq})")

    # 4. Merge lists
    all_records = existing_records + new_records

    # 5. Write back to responses.jsonl
    with open(JSONL_PATH, 'w', encoding='utf-8') as f:
        for rec in all_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Successfully wrote {len(all_records)} total records to {JSONL_PATH} (all anonymized and '_age' removed).")

if __name__ == "__main__":
    clean_and_normalize()
