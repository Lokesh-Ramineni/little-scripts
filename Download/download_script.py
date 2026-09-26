import re
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from email.utils import formatdate
from certi import cert_path

from classes import scrape_faculty_slots
from payloads import make_payload_1,make_payload_2,make_payload_3
from endpoints import content,get_course,slotId_forCourse,timetable

#Utlis
sem_sub_id="XXXX"
authorized_id="XXXX"

#Paths
Path("data").mkdir(exist_ok=True)
Path("config").mkdir(exist_ok=True)

#Cookie
with open("session.json") as f:
    cookie=json.load(f)

session = requests.Session()
session.cookies.set('JSESSIONID', cookie["JSESSIONID"])

#Content Page
content_page=session.get(content,verify=str(cert_path))
content_page.raise_for_status()

with open("data/content.html","w", encoding="utf-8") as f:
    f.write(content_page.text)
print("content: ",content_page.status_code)

#Csrf Token
csrf_match = re.search(r'name="_csrf"\s+value="([^"]+)"', content_page.text)
if not csrf_match:
    raise RuntimeError("CSRF token not found")
csrf_token = csrf_match.group(1)
print(f'CSRF TOKEN: {csrf_token}')

#Course Page
payload_1=make_payload_1(csrf_token,sem_sub_id=sem_sub_id,authorized_id=authorized_id,timestamp=formatdate(timeval=None, localtime=False, usegmt=True))

course_page=session.post(get_course,data=payload_1,verify=str(cert_path))
course_page.raise_for_status()
print("course: ",course_page.status_code)

soup=BeautifulSoup(course_page.text,"html.parser")

options = soup.select("select#courseCode option")
courses=[]
for option in options[1:]:
    option_dict={
        "text": option.text.strip(),
        "value": option.get("value")
    }
    courses.append(option_dict)

with open("config/class_Id.json", "w", encoding="utf-8") as file:
    json.dump(courses, file, indent=4, ensure_ascii=False)

with open("data/Course.html","w", encoding="utf-8") as f:
    f.write(course_page.text)

if not courses:
    raise RuntimeError("No courses found")

payload_2=make_payload_2(csrf=csrf_token,class_id=courses[0]["value"],sem_sub_id=sem_sub_id,authorized_id=authorized_id,timestamp=formatdate(timeval=None, localtime=False, usegmt=True))

slotid=session.post(slotId_forCourse,data=payload_2,verify=str(cert_path))
slotid.raise_for_status()

print(f'Slot ID: {slotid.status_code}')
with open("data/Slot_Id.html","w", encoding="utf-8") as f:
    f.write(slotid.text)

payload_3=make_payload_3(csrf=csrf_token,sem_sub_id=sem_sub_id,authorized_id=authorized_id,timestamp=formatdate(timeval=None, localtime=False, usegmt=True))
timetable_response=session.post(timetable,data=payload_3,verify=str(cert_path))
timetable_response.raise_for_status()
print(f'TimeTable :{timetable_response.status_code}')

with open("data/timetable.html","w", encoding="utf-8") as f:
    f.write(timetable_response.text)

scrape_faculty_slots(timetable_response.text)

with open("config/faculty_slots.json") as f:
    classes=json.load(f)

erpIds=[]

for cls in classes:
    class_id=cls["classnbr"]

    payload_2=make_payload_2(csrf=csrf_token,class_id=class_id,sem_sub_id=sem_sub_id,authorized_id=authorized_id,timestamp=formatdate(timeval=None, localtime=False, usegmt=True))
    slotid=session.post(slotId_forCourse,data=payload_2,verify=str(cert_path),timeout=20)
    slotid.raise_for_status()

    soup1=BeautifulSoup(slotid.text,"html.parser")
    table=soup1.find("table")

    if table is None:
        print(f'Table not found for {class_id}')
        continue

    rows=table.find_all("tr")
    found=False

    for row in rows:
        tds=row.find_all("td")
        if len(tds) <= 7:
            continue
        row_class_id = tds[5].get_text(strip=True)

        if row_class_id != class_id:
            continue
        
        erp_text = tds[7].get_text(" ", strip=True)
        erp_id = erp_text.split()[0] if erp_text else None
        erpIds.append({
            "classId":class_id,
            "ErpId":erp_id
        })
        if erp_id:
            print(f"Id found for class Id: {class_id}, ID: {erp_id}")
        else:
            print(f"ERP ID is empty for class Id: {class_id}, Faculty: {cls['facultyname']}")
        found=True
        break

    if not found:
        erpIds.append({
            "classId":class_id,
            "ErpId":None
        })
        print(f'Faculty not found with class Id: {class_id} {cls["facultyname"]}')

with open("config/erpIds.json","w",encoding="utf-8") as file:
    json.dump(erpIds,file,indent=4,ensure_ascii=False)
