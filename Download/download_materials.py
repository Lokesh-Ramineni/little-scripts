import re
import json
import zipfile
from io import BytesIO
from pathlib import Path
from email.utils import formatdate

from payloads import make_payload_5
from endpoints import base_url

with open("config/download_data.json","r") as f:
    download_materials=json.load(f)

def download_pdf(session,url_text,payload, output_path,cert_path):

    response = session.get(
        f"{base_url}/{url_text}",
        params=payload,
        verify=str(cert_path),
        timeout=30,
    )
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    return response

def safe_path_name(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def get_extension(response):

    data = response.content

    if data.startswith(b"%PDF-"):
        return ".pdf"

    if data.startswith(b"PK"):
        try:
            with zipfile.ZipFile(BytesIO(data)) as z:

                names = z.namelist()

                if any(name.startswith("ppt/") for name in names):
                    return ".pptx"

                if any(name.startswith("word/") for name in names):
                    return ".docx"

                if any(name.startswith("xl/") for name in names):
                    return ".xlsx"

                print("ZIP but unknown Office type")
                return ".zip"

        except zipfile.BadZipFile:
            print("PK header found, but ZIP is invalid")

    print("DETECTED: UNKNOWN")
    return ".bin"
def download_material(session,csrf_token,authorized_id,cert_path):
    folder=Path("Materials")
    folder.mkdir(parents=True, exist_ok=True)
    payload_5=make_payload_5(csrf=csrf_token,authorized_id=authorized_id ,timestamp=formatdate(timeval=None, localtime=False, usegmt=True))
    for coursename,materials in download_materials.items():

        course_folder=folder/safe_path_name(coursename)
        course_folder.mkdir(parents=True, exist_ok=True)
        print(coursename)

        for material in materials[:1]:
            topic=material["topic"]
            url=material["Download"]
            download_pdf(session=session,url_text=url,payload=payload_5,output_path=f'{course_folder}/{topic}.docx',cert_path=cert_path)

        for material in materials[1:]:
            topic=material["topic"]
            url=material["Download"]
            if topic is None:
                topic=url.split("/")[-1]

            response = download_pdf(
                session=session,
                url_text=url,
                payload=payload_5,
                output_path=f'{course_folder}/{topic}.tmp',
                cert_path=cert_path
            )

            extension = get_extension(response)

            Path(f'{course_folder}/{topic}.tmp').rename(
                f'{course_folder}/{topic}{extension}'
            )