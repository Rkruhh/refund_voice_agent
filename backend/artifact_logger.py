import json
import os
from datetime import datetime

ARTIFACT_DIR = "artifacts"

def ensure_dirs():
    if not os.path.exists(ARTIFACT_DIR):
        os.makedirs(ARTIFACT_DIR)

def save_decision_log(data):
    ensure_dirs()
    file = f"{ARTIFACT_DIR}/decision_{datetime.now().timestamp()}.json"
    with open(file, "w") as f:
        json.dump(data, f, indent=2)
    return file

def save_receipt(result):
    ensure_dirs()
    file = f"{ARTIFACT_DIR}/receipt_{datetime.now().timestamp()}.json"
    with open(file, "w") as f:
        json.dump(result, f, indent=2)
    return file

def save_transcript(lines):
    ensure_dirs()
    file = f"{ARTIFACT_DIR}/transcript_{datetime.now().timestamp()}.txt"
    with open(file, "w") as f:
        f.write("\n".join(lines))
    return file
