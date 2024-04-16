# Add IMG timestamp for all images
# e.g. from IMG_0033.jpg -> IMG_20240416_184014_IMG_0033.jpg

# Requiremets:
# pip install pillow

import pathlib
from PIL import Image
from datetime import datetime


RENAME_FILES_DIR_PATH = r"C:\Users\kornel\Downloads\jj\conv"  # Podmień na ścieżkę do folderu ze zdjęciami
RENAME_IMAGES_WITH_EXTENSIONS = [".jpg", ".png",]

def add_timestamp_prefix_to_images_in_dir(dir_path):
    dir_path = pathlib.Path(dir_path)
    for file_path in dir_path.iterdir():
        if not file_path.is_file():
            continue # skip this loop - it can not be applied to directory
        
        taken_datetime = None
        
        # Handle images
        if file_path.suffix.lower() in RENAME_IMAGES_WITH_EXTENSIONS:
            img = Image.open(file_path)
            info = img._getexif()
            
            # Get timestamp of creation
            if 36867 in info:
                taken_datetime = info[36867]
                taken_datetime = datetime.strptime(taken_datetime, '%Y:%m:%d %H:%M:%S')
                img.close()

        # Rename file here
        if not taken_datetime is None:
            new_filename_with_suffix = "IMG_" + taken_datetime.strftime('%Y%m%d_%H%M%S') + "_" + file_path.name
            renamed_file_path = pathlib.Path(file_path.parent, new_filename_with_suffix)
            file_path.rename(renamed_file_path)
if __name__ == '__main__':
    add_timestamp_prefix_to_images_in_dir(RENAME_FILES_DIR_PATH)


