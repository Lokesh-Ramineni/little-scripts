import os
import sys
from pathlib import Path
from PIL import Image
from PIL.ExifTags import IFD
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS

def default(exif:Image.Exif ) -> None:
    for tag_id, value in exif.items():
        tag_name = TAGS.get(tag_id, tag_id)

        print(f"{tag_name}: {value}")

def info(exif:Image.Exif) -> None:
    try:
        exif_sub_dir = exif.get_ifd(IFD.Exif)
        for tag_id, value in exif_sub_dir.items():
            tag_name = TAGS.get(tag_id, tag_id)
            if tag_name == 'UserComment':
                clean_bytes = value.replace(b'\x00', b'')

                if not clean_bytes:
                    print("UserComment: [Empty]")
            else:

                print(f"{tag_name}: {value}")
    except KeyError:
        print("No hidden camera settings directory found.")

def gps_coor(exif:Image.Exif) -> None:
    try:
        gps_sub_dir = exif.get_ifd(IFD.GPSInfo)
        for tag_id, value in gps_sub_dir.items():
            tag_name = GPSTAGS.get(tag_id, tag_id)
            print(f"{tag_name}: {value}\n")
    except KeyError:
        print("No GPS directory found.\n")

def get_exif():
    choice=None
    original_stdout = None
    supported_formats = [".jpg", ".jpeg", ".png"]
    while True:
        print("How do you want to display the output:")
        print("1.File")
        print("2.CLI")
        try:
            choice = int(input("Enter your choice: "))
            if choice in (1, 2):
                break
        except ValueError:
            pass
        print("Invalid choice")

    image_dir = Path("exif_test_images").resolve()
    if not image_dir.exists():
        print(f"Directory not found: {image_dir}")
        return

    image_files = [f for f in image_dir.iterdir() if f.is_file()]
    if not image_files:
        print("Directory is empty")
        return

    if choice == 1:
        original_stdout = sys.stdout
        sys.stdout= open("exif_data.txt", "w", encoding="utf-8")
    else:
        pass

    try:
        for file in image_files:
            if file.suffix in supported_formats:
                print(f'--------------------Selected Image:{file}----------------------\n')
                try:
                    with Image.open(file) as img:
                        exif = img.getexif()
                        if not exif:
                            print("No EXIF data found.")
                            continue

                        default(exif)
                        info(exif)
                        gps_coor(exif)

                except Exception as e:
                    print(f"Error processing {file.name}: {e}")
            else:
                print(f"No supported file extension for {file.name}")
    except BrokenPipeError:
        pass
    sys.stdout.close()
    sys.stdout = original_stdout
    if choice==1:
        print("Saved to exif_data.txt")


if __name__ == "__main__":
    get_exif()




