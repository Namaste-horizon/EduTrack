import os
import json

sectionListFile = "sectionlist.json"
sectionsFile = "sections.json"
teacherSectionsFile = "teachersections.json"

def loadJson(filename, default):
    if not os.path.exists(filename):
        return default
    with open(filename, "r") as f:
        return json.load(f)

def saveJson(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def createSection():
    lst = loadJson(sectionListFile, [])
    lst = sorted({str(s).strip().upper() for s in lst if str(s).strip()})
    s = input("Enter new section (e.g., A): ").strip().upper()
    if not s:
        print("Invalid section.")
        return
    if s in lst:
        print("Section already exists.")
        return
    lst.append(s)
    saveJson(sectionListFile, sorted(lst))
    print(f"Section {s} created.")

def listSections(returnList=False):
    lst = loadJson(sectionListFile, [])
    lst = sorted({str(s).strip().upper() for s in lst if str(s).strip()})
    if not lst:
        print("No sections available. Create one first.")
        return [] if returnList else None
    print("\nSections:")
    for i, s in enumerate(lst, 1):
        print(f" {i}. {s}")
    return lst if returnList else None

def assignSectionFromList():
    lst = listSections(returnList=True)
    if not lst:
        return
    num = input("Choose section number to assign: ").strip()
    if not num.isdigit():
        print("Invalid choice.")
        return
    idx = int(num) - 1
    if not (0 <= idx < len(lst)):
        print("Invalid section number.")
        return
    roll = input("Enter student roll no: ").strip()
    if not roll:
        print("Invalid roll no.")
        return
    mapping = loadJson(sectionsFile, {})
    mapping[roll] = lst[idx]
    saveJson(sectionsFile, mapping)
    print(f"Assigned section {lst[idx]} to {roll}.")

def assignSectionToTeacher():
    lst = listSections(returnList=True)
    if not lst:
        return
    teacher = input("Enter teacher username: ").strip()
    if not teacher:
        print("Invalid teacher username.")
        return
    print("\nSelect section numbers to assign to this teacher (comma separated):")
    nums = input("Enter numbers: ").strip()
    indexes = [int(x) - 1 for x in nums.split(",") if x.strip().isdigit()]
    chosen = [lst[i] for i in indexes if 0 <= i < len(lst)]
    if not chosen:
        print("No valid sections selected.")
        return
    tmap = loadJson(teacherSectionsFile, {})
    tmap[teacher] = sorted(set(chosen))
    saveJson(teacherSectionsFile, tmap)
    print(f"Assigned sections {', '.join(tmap[teacher])} to {teacher}.")

def viewMySections(teachername):
    tmap = loadJson(teacherSectionsFile, {})
    secs = tmap.get(teachername, [])
    if not secs:
        print("No sections assigned to this teacher.")
        return
    print(f"\nSections assigned to {teachername}:")
    for s in secs:
        print(f" {s}")

def viewSectionAssignments():
    mapping = loadJson(sectionsFile, {})
    if not mapping:
        print("No students assigned yet.")
        return
    bysec = {}
    for roll, sec in mapping.items():
        sec = str(sec).strip().upper()
        bysec.setdefault(sec, []).append(roll)
    print("\nCurrent section assignments:")
    for sec in sorted(bysec.keys()):
        print(f" Section {sec}: {', '.join(sorted(bysec[sec]))}")

def getSectionForRoll(roll):
    mapping = loadJson(sectionsFile, {})
    return mapping.get(str(roll), "Not assigned")

def listTeacherSections(teachername):
    tmap = loadJson(teacherSectionsFile, {})
    return tmap.get(teachername, [])