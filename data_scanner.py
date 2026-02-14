import os, json
from datetime import datetime

SCAN_RESULTS_DIR = "users/scan_history"

def save_scan_result(u, result_df, name):
    if not os.path.exists(SCAN_RESULTS_DIR): os.makedirs(SCAN_RESULTS_DIR)
    fn = f"{SCAN_RESULTS_DIR}/{u}_{datetime.now().strftime('%Y%m%d')}_{name}.json"
    result_df.to_json(fn, orient="records", force_ascii=False)

def list_scan_history(u):
    if not os.path.exists(SCAN_RESULTS_DIR): return []
    return sorted([f for f in os.listdir(SCAN_RESULTS_DIR) if f.startswith(u)], reverse=True)
