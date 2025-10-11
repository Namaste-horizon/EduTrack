import json
from datetime import datetime
import os

SUBJECTSFILE = "subjects.json"
EXAMFILE = "exam_date.json"
ALLOCATIONFILE = "subject_allocation.json"

def loadSubjects():
    try:
        with open(SUBJECTSFILE, "r") as f:
            data = json.load(f)
    except:
        return []
    if isinstance(data, dict) and isinstance(data.get("subjects"), list):
        return data["subjects"]
    if isinstance(data, list):
        return data
    return []

def loadExamMap():
    try:
        with open(EXAMFILE, "r") as f:
            raw = json.load(f)
    except:
        raw = {}
    if isinstance(raw, dict) and isinstance(raw.get("exam_schedule"), list):
        items = raw["exam_schedule"]
    elif isinstance(raw, list):
        items = raw
    else:
        items = []
    examMap = {}
    for it in items:
        code = (it.get("subject_code") or it.get("code") or "").upper()
        if not code:
            continue
        examMap[code] = {
            "subjectName": it.get("subject_name") or it.get("name") or "",
            "examDate": it.get("exam_date") or ""
        }
    return examMap

def saveExamMap(examMap):
    payload = {"exam_schedule": []}
    for code in sorted(examMap.keys()):
        entry = examMap[code]
        payload["exam_schedule"].append({
            "subject_code": code,
            "subject_name": entry.get("subjectName", ""),
            "exam_date": entry.get("examDate", "")
        })
    with open(EXAMFILE, "w") as f:
        json.dump(payload, f, indent=2)

def setExamDatesAdmin():
    subjects = loadSubjects()
    if not subjects:
        print("No subjects available.")
        return
    print("\nAvailable subjects:")
    for i, s in enumerate(subjects, 1):
        print(f"{i}. {s.get('name','')} ({s.get('code','')})")
    sel = input("Enter subject numbers to set exam date (comma separated): ").strip()
    if not sel:
        return
    try:
        indexes = [int(x)-1 for x in sel.split(",") if x.strip().isdigit()]
    except:
        print("Invalid input.")
        return
    examMap = loadExamMap()
    for idx in indexes:
        if 0 <= idx < len(subjects):
            s = subjects[idx]
            code = (s.get("code") or "").upper()
            name = s.get("name") or ""
            dateStr = input(f"Enter exam date for {name} ({code}) [DD/MM/YYYY]: ").strip()
            try:
                datetime.strptime(dateStr, "%d/%m/%Y")
            except:
                print(f"Skipped {code}: invalid date format.")
                continue
            examMap[code] = {"subjectName": name, "examDate": dateStr}
    saveExamMap(examMap)
    print("Exam dates saved.")

def getExamDate(subjectCode):
    if not subjectCode:
        return "Not set"
    examMap = loadExamMap()
    return examMap.get(subjectCode.upper(), {}).get("examDate", "Not set")

def loadSectionSubjects(sectionName):
    sectionName = (sectionName or "").strip().upper()
    subjects = loadSubjects()
    if not os.path.exists(ALLOCATIONFILE):
        return subjects, False
    try:
        with open(ALLOCATIONFILE, "r") as f:
            alloc = json.load(f)
    except:
        alloc = {}
    raw = alloc.get(sectionName, [])
    codes = []
    result = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                code = (item.get("code") or item.get("subject_code") or "").upper()
                name = item.get("name") or item.get("subject_name") or ""
                if code:
                    codes.append(code)
                    result.append({"name": name, "code": code})
            elif isinstance(item, str):
                code = item.upper()
                if code:
                    codes.append(code)
    if result:
        return result, True
    if codes:
        for s in subjects:
            if (s.get("code") or "").upper() in codes:
                result.append({"name": s.get("name",""), "code": (s.get("code") or "").upper()})
        return result, True
    return subjects, False

def viewAllExamDates():
    subjects = loadSubjects()
    if not subjects:
        print("No subjects available.")
        return
    examMap = loadExamMap()
    print("\nExam Dates (All Subjects):")
    for s in subjects:
        code = (s.get("code") or "").upper()
        name = s.get("name") or ""
        dateStr = examMap.get(code, {}).get("examDate", "Not set")
        print(f" {name} ({code}) - Exam: {dateStr}")

def viewSectionExamDates(sectionName):
    subs, isAllocated = loadSectionSubjects(sectionName)
    if not subs:
        print("No subjects available for this section.")
        return
    examMap = loadExamMap()
    title = f"Section {sectionName} Exam Dates" if sectionName else "Exam Dates"
    print(f"\n{title}:")
    if not isAllocated:
        print("(No section-specific allocation found; showing all subjects.)")
    for s in subs:
        code = (s.get("code") or "").upper()
        name = s.get("name") or ""
        dateStr = examMap.get(code, {}).get("examDate", "Not set")
        print(f" {name} ({code}) - Exam: {dateStr}")

def viewStudentExamSchedule(username):
    import subject
    import section
    roll = subject.getRollNumber(username, "student")
    sec = section.getSectionForRoll(roll)
    if sec == "Not assigned":
        print("Section not assigned.")
        return
    viewSectionExamDates(sec)