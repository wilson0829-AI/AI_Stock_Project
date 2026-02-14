import json, os

USERS_DIR = "users"

def get_user_file_path(u, file_type="portfolio"):
    if not os.path.exists(USERS_DIR): os.makedirs(USERS_DIR)
    return f"{USERS_DIR}/{u}_{file_type}.json"

def load_portfolio(u):
    p = get_user_file_path(u, "portfolio")
    return json.load(open(p, "r", encoding="utf-8")) if os.path.exists(p) else {}

def save_portfolio(u, data):
    json.dump(data, open(get_user_file_path(u, "portfolio"), "w", encoding="utf-8"), indent=4, ensure_ascii=False)

def load_history(u):
    p = get_user_file_path(u, "history")
    return json.load(open(p, "r", encoding="utf-8")) if os.path.exists(p) else []

def save_history(u, data):
    json.dump(data, open(get_user_file_path(u, "history"), "w", encoding="utf-8"), indent=4, ensure_ascii=False)
    