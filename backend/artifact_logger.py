import json
import os
from datetime import datetime

ARTIFACT_DIR = "artifacts"
LOG_DIR = "logs"


def _ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_decision_log(data):
    _ensure_dir(ARTIFACT_DIR)
    file = f"{ARTIFACT_DIR}/decision_{datetime.now().timestamp()}.json"
    with open(file, "w") as f:
        json.dump(data, f, indent=2)
    return file


def save_receipt(result):
    _ensure_dir(ARTIFACT_DIR)
    file = f"{ARTIFACT_DIR}/receipt_{datetime.now().timestamp()}.json"
    with open(file, "w") as f:
        json.dump(result, f, indent=2)
    return file


def save_transcript(lines):
    _ensure_dir(ARTIFACT_DIR)
    file = f"{ARTIFACT_DIR}/transcript_{datetime.now().timestamp()}.txt"
    with open(file, "w") as f:
        f.write("\n".join(lines))
    return file


def save_metrics(metrics: dict):
    """
    Save operational metrics for the call:
    - start_time, end_time
    - seconds_total
    - seconds_to_auth
    - seconds_to_decision
    - cost breakdown (if provided)
    """
    _ensure_dir(ARTIFACT_DIR)
    file = f"{ARTIFACT_DIR}/metrics_{datetime.now().timestamp()}.json"
    with open(file, "w") as f:
        json.dump(metrics, f, indent=2)
    return file


def save_trial_summary(trial_label: str, summary: dict):
    """
    Save a high-level trial summary for the spike docs.
    Example trial_label: 'trial_A_eligible', 'trial_B_ineligible'
    """
    _ensure_dir(LOG_DIR)
    file = f"{LOG_DIR}/{trial_label}_{datetime.now().timestamp()}.json"
    with open(file, "w") as f:
        json.dump(summary, f, indent=2)
    return file
