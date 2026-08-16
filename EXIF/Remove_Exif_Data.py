import os
import sys
from pathlib import Path
from PIL import Image

def strip_exif():
    cwd = os.getcwd()
    output_dir = os.path.join(cwd, "clean_images")

    image_dir = Path("exif_test_images").resolve()
    if not image_dir.exists():
        print(f"Directory not found: {image_dir}")
        return

    image_files = [f for f in image_dir.iterdir() if f.is_file()]
    if not image_files:
        print("Directory is empty")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory for safe keeping: {output_dir}")

    supported_formats = [".jpg", ".jpeg", ".png"]

    for image_file in image_files:
        if image_file.suffix in supported_formats:
            try:
                with Image.open(image_file) as f:
                    pixels = list(f.getdata())
                    new_img=Image.new(f.mode, f.size)
                    new_img.putdata(pixels)

                    new_img.save(f"{output_dir}/{image_file.name}")
                    print(f"Success: Stripped metadata from '{image_file}' -> saved as 'clean_{image_file.name}'")
            except Exception as e:
                print(f"Failed to strip metadata for '{image_file.name}, Error: {e}'")


if __name__ == "__main__":
    strip_exif()