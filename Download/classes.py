import json
from pathlib import Path

from bs4 import BeautifulSoup


def get_course_type(ltpjc):
    parts = ltpjc.split()

    if len(parts) < 5:
        return "Unknown"

    try:
        l, t, p, j, c = map(int, parts[:5])
    except ValueError:
        return "Unknown"

    if l > 0 and t > 0 and p == 0 and j == 0:
        return "Embedded Theory"

    if l > 0 and t == 0 and p == 0 and j == 0:
        return "Theory Only"

    if p > 0 or j > 0:
        return "Embedded Lab"

    return "Unknown"


def scrape_faculty_slots(html_file):
    try:
        soup = BeautifulSoup(html_file, "html.parser")

        results = []
        table = None

        for candidate in soup.find_all("table"):
            headers = [
                th.get_text(" ", strip=True)
                for th in candidate.find_all("th")
            ]

            if "Class Nbr" in headers and "Faculty Details" in headers:
                table = candidate
                break

        if table is None:
            raise RuntimeError("Course table not found")

        for row in table.find_all("tr"):
            cells = row.find_all("td")

            if len(cells) < 9:
                continue

            course_text = cells[2].get_text(" ", strip=True)
            ltpjc = cells[3].get_text(" ", strip=True)
            class_nbr = cells[6].get_text(" ", strip=True)

            slot_parts = [
                p.get_text(" ", strip=True)
                for p in cells[7].find_all("p")
            ]

            faculty_parts = [
                p.get_text(" ", strip=True)
                for p in cells[8].find_all("p")
            ]

            if not course_text or not class_nbr or not slot_parts:
                continue

            if " - " in course_text:
                course_id, course = course_text.split(" - ", 1)
            else:
                course_id = course_text
                course = ""

            slot = slot_parts[0].split(" - ", 1)[0].strip()

            faculty_name = ""

            if faculty_parts:
                faculty_name = faculty_parts[0].split(" - ", 1)[0].strip()

            course_type = get_course_type(ltpjc)

            results.append({
                "course_id": course_id.strip(),
                "course": course.strip(),
                "course_type": course_type,
                "classnbr": class_nbr,
                "slot": slot,
                "facultyname": faculty_name
            })

        output_file = "config/faculty_slots.json"

        Path("config").mkdir(exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                results,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(f"Saved {len(results)} courses to {output_file}")

    except Exception as e:
        print(f"Error: {e}")