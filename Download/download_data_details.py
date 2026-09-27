import re
import json
from bs4 import BeautifulSoup
from email.utils import formatdate

from payloads import make_payload_4
from endpoints import course_details

with open("config/erpIds.json","r") as f:
    details=json.load(f)

def safe_path_name(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

download_details={}
def download_data_call(session,csrf_token,sem_sub_id,authorized_id,cert_path):
    for detail in details:
        course=detail["course"]
        if course is None or course == "None":
            continue
        class_id=detail["classId"]
        erpid=detail["ErpId"]
        payload_4=make_payload_4(csrf=csrf_token,sem_sub_id=sem_sub_id,erp_id=erpid,class_id=class_id,authorized_id=authorized_id,timestamp=formatdate(timeval=None, localtime=False, usegmt=True))
        course_details_response=session.post(course_details,data=payload_4,verify=str(cert_path),timeout=20)
        print(course)
        course_details_response.raise_for_status()
        print(f'Course Details: {course_details_response.status_code}')

        with open("data/course_details.html","w",encoding="utf-8") as f:
            f.write(course_details_response.text)

        soup=BeautifulSoup(course_details_response.text,"html.parser")

        tables=soup.find_all("table")
        print(len(tables))

        # if tables is None:
        #     break
        
        if len(tables) < 3:
            print(f"Skipping {course}: only {len(tables)} tables found")
            continue

        table2_tr=tables[1].find_all("tr")
        a=table2_tr[0].find("a", href=True)
        download_details[course]=[]
        if a is not None:
            href=a["href"]

            url = re.search(r"vtopDownload\('([^']+)'\)", href).group(1)
            
            download_details[course].append({
                "topic":table2_tr[0].find("td").get_text(strip=True),
                "Download":f"{url}"
            })

        table3_tr=tables[2].find_all("tr")
        for tr in table3_tr[1:]:
            tds=tr.find_all("td")

            a=tds[4].find_all("a",href=True)
            if not a :
                continue
            lecture_topic = tds[3].get_text(strip=True) or None
            for index,value in enumerate(a):
                href=value["href"]
                if not href.startswith("javascript:vtopDownload("):
                    continue

                url = re.search(r"vtopDownload\('([^']+)'\)", href)

                if not url:
                    continue    

                url=url.group(1)
                topic=lecture_topic
                if topic is not None and len(a) >= 2:
                    topic = f"{topic}{index + 1}"
                if topic is not None:
                    topic=safe_path_name(topic)
                download_details[course].append({
                    "topic":topic,
                    "Download":url
                })

        with open("config/download_data.json","w",encoding="utf-8") as file:
            json.dump(download_details,file,indent=4,ensure_ascii=False)
