import hashlib, json, os

DB = "users/user_registry.json"
def hash_pw(pw): return hashlib.sha256(str.encode(pw)).hexdigest()
def check_login(u, p):
    if not os.path.exists("users"): os.makedirs("users")
    if not os.path.exists(DB):
        with open(DB, "w") as f: json.dump({"admin":{"password":hash_pw("1234"),"role":"admin"}}, f)
    with open(DB, "r") as f: db = json.load(f)
    if u in db and db[u]["password"] == hash_pw(p): return True, db[u]["role"]
    return False, None
def add_user(u, p, r="user"):
    with open(DB,"r") as f: db = json.load(f)
    if u in db: return False, "已存在"
    db[u] = {"password":hash_pw(p), "role":r}
    with open(DB,"w") as f: json.dump(db, f)
    return True, "成功"
def list_users():
    with open(DB,"r") as f: return json.load(f)
def delete_user(u):
    if u == "admin": return False
    with open(DB,"r") as f: db = json.load(f); del db[u]
    with open(DB,"w") as f: json.dump(db, f)
    return True
