import re
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from email.utils import formatdate
from certi import cert_path

from payloads import make_payload_1,make_payload_2
from endpoints import content,get_course,slotId_forCourse

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
print("course",course_page.status_code)

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