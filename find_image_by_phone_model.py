import exif
import os
import shutil 

basic_path = "C:\\Kornel_Zdjecia\\telefon_tmp\\Telefon"
sylwia_move_path = "C:\\Kornel_Zdjecia\\telefon_tmp\\Telefon\\Sylwia"
kornel_move_path = "C:\\Kornel_Zdjecia\\telefon_tmp\\Telefon\\Kornel"
other_move_path = "C:\\Kornel_Zdjecia\\telefon_tmp\\Telefon\\Other"

files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(basic_path) for f in filenames]

for cur_file in files:
    try:
        cur_file_model = None
        with open(cur_file, 'rb') as image_file:
            my_image = exif.Image(image_file)
            if my_image.has_exif:
                if hasattr(my_image, 'model'):
                    cur_file_model = my_image.model

        if cur_file_model == 'Mi 9 Lite':
            shutil.copy(cur_file, kornel_move_path)
            os.remove(cur_file)
        elif cur_file_model == 'Redmi Note 8 Pro':
            shutil.copy(cur_file, sylwia_move_path)
            os.remove(cur_file)
        else:
            shutil.copy(cur_file, other_move_path)
            os.remove(cur_file)
    except:
        print('can not open file: '+cur_file)