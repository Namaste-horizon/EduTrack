import os
import json

subjectsFile = "subjects.json"
rollnumbersFile = "rollnumbers.json"

def loadJson(filename, default):
    if not os.path.exists(filename):
        return default
    with open(filename, "r") as f:
        return json.load(f)

def saveJson(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def addSubject():
    data = loadJson(subjectsFile, {"subjects": []})
    subjects = data.get("subjects", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
    name = input("Enter subject name: ").strip()
    code = input("Enter subject code [eg- TMA101]: ").strip().upper()
    if any(s.get("code") == code for s in subjects):
        print("Subject code already exists.")
        return
    subjects.append({"name": name, "code": code})
    toSave = {"subjects": subjects}
    saveJson(subjectsFile, toSave)
    print("Subject added.")

def listSubjects():
    data = loadJson(subjectsFile, {"subjects": []})
    subjects = data.get("subjects", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
    if not subjects:
        print("No subjects available.")
        return []
    print("\nSubjects:")
    for i, s in enumerate(subjects, 1):
        print(f" {i}. {s.get('name','')} ({s.get('code','')})")
    return subjects

def getRollNumber(name, role="student"):
    db = loadJson(rollnumbersFile, {})
    if not isinstance(db, dict) or "map" not in db or "counters" not in db:
        legacy = db if isinstance(db, dict) else {}
        db = {"map": {"student": {}, "teacher": {}, "admin": {}}, "counters": {"student": 0, "teacher": 0, "admin": 0}}
        for k, v in legacy.items():
            r = "student"
            if isinstance(v, str):
                if v.startswith("T"):
                    r = "teacher"
                    try: db["counters"][r] = max(db["counters"][r], int(v[1:]))
                    except: pass
                elif v.startswith("A"):
                    r = "admin"
                    try: db["counters"][r] = max(db["counters"][r], int(v[1:]))
                    except: pass
                elif v.startswith("2025"):
                    r = "student"
                    try: db["counters"][r] = max(db["counters"][r], int(v[4:]))
                    except: pass
            db["map"][r][k] = v
        saveJson(rollnumbersFile, db)
    if name in db["map"].get(role, {}):
        return db["map"][role][name]
    db["counters"][role] = db["counters"].get(role, 0) + 1
    n = db["counters"][role]
    if role == "teacher":
        roll = f"T{str(n).zfill(4)}"
    elif role == "admin":
        roll = f"A{str(n).zfill(4)}"
    else:
        roll = f"2025{str(n).zfill(4)}"
    if role not in db["map"]:
        db["map"][role] = {}
    db["map"][role][name] = roll
    saveJson(rollnumbersFile, db)
    return roll