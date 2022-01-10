import os
import pprint
import sys
import argparse
import shutil 
# image compress
from PIL import Image
import PIL
import glob
import tqdm
# logging
import json_logging, logging, datetime

source_path      = "C:\\Kornel_Zdjecia\\tmp_script_test_source_source"
destination_path = "C:\\Kornel_Zdjecia\\tmp_script_test_source_source_helper"
skip_duplicates_global = True
# skip_duplicates_global = False


EXPORT_EXTENSIONS = ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG' ]
EXPORT_EXCLUDE_DIR = ['Wszystkie', 'All']
TRUSTED_EXTENSIONS = ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG',
                      '.mp4', '.MP4'
                      ]
IGNORED_EXTENSIONS = ['.txt']

file_datestamp_format = '%Y%m%d_%H%M%S'
__init_datestamp = datetime.datetime.now().strftime(file_datestamp_format)
gen_dir_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen", "logs"))

# # logging gear
json_logging.init_non_web(enable_json=True)
logger = logging.getLogger("duplicated_photos_remove-logger")
logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler(sys.stdout))

log_filename = "dup_photo_rem_log_" + __init_datestamp + ".json"
log_file_path = os.path.abspath(os.path.join(gen_dir_path, log_filename))
logger.addHandler(logging.FileHandler(log_file_path))
print("Log stored at: {}".format(log_file_path))

logger.info("Duplicated photos remove init. Logging timestamp: {}".format(__init_datestamp))

class Duplicates:
    class DuplicateItem:
        def __init__(self, list_of_paths, name):
            self.list_of_paths = list_of_paths
            self.name = name

        def get_name(self):
            return self.name

        def set_name(self, name):
            self.name = name

        def get_list_of_paths(self):
            return self.list_of_paths

        def set_list_of_paths(self, list_of_paths):
            # 'list_of_paths' is list of paths containing duplicated files
            self.list_of_paths = list_of_paths

        def add_paths_to_list(self, list_of_paths):
            # 'list_of_paths' is list of paths containing duplicated files
            for path in list_of_paths: 
                self.list_of_paths.append(path)

        def print_duplicate_item(self):
            print("Duplicate  - Filename: {}\nPaths".format(self.name))
            pprint.pprint(self.list_of_paths)
            print("")

    def __init__(self):
        self.list_of_duplicate_items = []

    def create_duplicate(self, paths):
        # 'paths' is list of paths containing duplicated files
        name = os.path.split(paths[0])[1]
        list_of_paths = []
        for path in paths:
            list_of_paths.append(os.path.split(path)[0])
        
        self.list_of_duplicate_items.append(self.DuplicateItem(list_of_paths, name))

    def add_to_existing_duplicate(self, paths):
        # 'paths' is list of paths containing duplicated files
        #todo
        for path in paths:
            for i in self.list_of_duplicate_items:
                if i.name == os.path.split(path)[1]:
                    i.add_paths_to_list([os.path.split(path)[0]])

    def duplicate_exist_in_base(self, paths):
        # 'paths' is list of paths containing duplicated files
        for path in paths:
            for i in self.list_of_duplicate_items:
                if i.name == os.path.split(path)[1]:
                    return True
        return False

    def print_duplicates(self):
        print("\n\n***********************\n****   DUPLICATES  ****\n***********************")
        for duplicate_item in self.list_of_duplicate_items:
            duplicate_item.print_duplicate_item()
            
            
class DirectoryStructure:
    def __init__(self, root_directory=None, skip_duplicates=True):
        self.found_not_processed_files = []
        self.trusted_files = []
        self.ignored_files = []
        self.duplicated_files = Duplicates()
        self.delete_from_current_directory = []
        self.root_directory = root_directory
        self.skip_duplicates = skip_duplicates

    def classify_file(self, full_file_path):
        if not (self.skip_duplicates and \
                self.find_duplicates_in_current_directory(full_file_path) ):    
            extension = os.path.splitext(full_file_path)[1]
            if extension in TRUSTED_EXTENSIONS:
                self.trusted_files.append(full_file_path)
                logger.info('classify_file - File in TRUSTED_EXTENSIONS - processing file: {}'.format(full_file_path))
            elif extension in IGNORED_EXTENSIONS:
                self.ignored_files.append(full_file_path)
                logger.info('classify_file - File in IGNORED_EXTENSIONS - processing file: {}'.format(full_file_path))
            else:
                self.found_not_processed_files.append(full_file_path)
                logger.info('classify_file - Extension not recognized - processing file: {}'.format(full_file_path))
        else:
            duplicates = [f for f in self.trusted_files if (os.path.split(f)[1] == os.path.split(full_file_path)[1])]
            for d in duplicates:
                self.trusted_files.remove(d)
                logger.info('classify_file - File found as duplicate, file removed from self.trusted_files - processing file: {}'.format(full_file_path))

    def scan_directory(self, full_file_path=None):
        if full_file_path is None:
            full_file_path = self.root_directory
        result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(full_file_path) for f in filenames]
        logger.info('scan_directory {} - Number of files found {}'.format(full_file_path, len(result)))
        [self.classify_file(file_path) for file_path in tqdm.tqdm(result, desc="Scan directory")]

    def classify_file_for_export(self, full_file_path):
        if not (self.find_duplicates_in_current_directory(full_file_path) \
            and self.skip_duplicates):    
            extension = os.path.splitext(full_file_path)[1]
            excluded_dir = []

            [excluded_dir.append(excl) 
            for excl in EXPORT_EXCLUDE_DIR 
            if os.path.sep+excl+os.path.sep in os.path.splitext(full_file_path)[0]]
            if len(excluded_dir) == 0 and extension in EXPORT_EXTENSIONS:
                self.trusted_files.append(full_file_path)
        else:
            duplicates = [f for f in self.trusted_files if (os.path.split(f)[1] == os.path.split(full_file_path)[1])]
            for d in duplicates:
                self.trusted_files.remove(d)

    def scan_directory_for_export(self, full_file_path=None):
        if full_file_path is None:
            full_file_path = self.root_directory
        if self.skip_duplicates:
            pass
        else:
            result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(full_file_path) for f in filenames]
            [self.classify_file_for_export(file_path) for file_path in result]

    def export_sorted_to_destination(self, destination_path):
        for export_source_path in tqdm.tqdm(self.trusted_files):
            export_relative_path = export_source_path.replace(self.root_directory, '')
            export_destination_path = destination_path + export_relative_path
            os.makedirs(os.path.dirname(export_destination_path), exist_ok=True)
            if not os.path.isfile(export_destination_path):
                shutil.copyfile(export_source_path, export_destination_path)
                picture = Image.open(export_destination_path)
                picture.save(export_destination_path,optimize=True,quality=30) 

    def find_duplicates_in_current_directory(self, full_file_path):
        if os.path.split(full_file_path)[1] in [os.path.split(f)[1] for f in self.trusted_files]:
            if self.duplicated_files.duplicate_exist_in_base([full_file_path]):
                self.duplicated_files.add_to_existing_duplicate([full_file_path])
            else:
                duplicates = [f for f in self.trusted_files if (os.path.split(f)[1] == os.path.split(full_file_path)[1])]
                duplicates.append(full_file_path)
                self.duplicated_files.create_duplicate(duplicates)
            return True
        return False

    def prepare_to_delete_existing_files(self, reference):
        assert isinstance(reference, DirectoryStructure), "reference must be a object of DirectoryStructure class"
        for trusted in tqdm.tqdm(self.trusted_files, desc="Prepare to delete duplicates"):
            if os.path.split(trusted)[1] in [os.path.split(f)[1] for f in reference.trusted_files]:
                self.delete_from_current_directory.append(trusted)
                logger.info("prepare_to_delete_existing_files - file will be deleted: {}".format(trusted))

    def delete_prepared_files(self):
        for f in self.delete_from_current_directory:
            os.remove(f)
            logger.info("delete_prepared_files - file was deleted: {}".format(f))
        print("\n\n*************************\n**** DELETE COMPLETE ****\n*************************")


    def print_warnings(self):
        print("\n\n***********************\n****    WARNINGS   ****\n***********************")
        for f in self.found_not_processed_files:
            log_msg = "Warning: File was not found:\n{}\n".format(f)
            print(log_msg)
            json_log = "print_warnings - {}".format(log_msg.replace('\n', ' '))
            logger.info(json_log)

    def print_ignored(self):
        print("\n\n***********************\n****    IGNORED    ****\n***********************")
        for f in self.ignored_files:
            log_msg = "IGNORED: File was ignored:\n{}\n".format(f)
            print(log_msg)
            json_log = "print_ignored - {}".format(log_msg.replace('\n', ' '))
            logger.info(json_log)

    def print_duplicates(self):
        self.duplicated_files.print_duplicates()

    def print_prepared_to_delete(self):
        print("\n\n***********************\n****    DELETE     ****\n***********************")
        for f in self.delete_from_current_directory:
            log_msg = "DELETE: File will be deleted:\n{}\n".format(f)
            print(log_msg)
            json_log = "print_prepared_to_delete - {}".format(log_msg.replace('\n', ' '))
            logger.info(json_log)


def auto_scan_directories(sources, destinations, delete_files, skip_duplicates, verbose, no_action):
    for d in destinations:
        for s in sources:
            # Source
            if verbose == True:
                print("Directory path: {}".format(s))
            source = DirectoryStructure(s, skip_duplicates=skip_duplicates)
            source.scan_directory()
            # Destination
            if verbose == True:
                print("Directory path: {}".format(d))
            destination = DirectoryStructure(d, skip_duplicates=skip_duplicates)
            destination.scan_directory()

            if verbose == True:
                print("\n\tSource\n")
                source.print_warnings()
                source.print_ignored()
                source.print_duplicates()
                print("\n\tDestination\n")
                destination.print_warnings()
                destination.print_ignored()
                destination.print_duplicates()

            if no_action:
                destination.prepare_to_delete_existing_files(source)
                destination.print_prepared_to_delete()
            elif delete_files:
                destination.prepare_to_delete_existing_files(source)
                if verbose == True:
                    destination.print_prepared_to_delete()
                destination.delete_prepared_files()


def parse_and_execute_cli():    
# https://www.datacamp.com/community/tutorials/argument-parsing-in-python?utm_source=adwords_ppc&utm_campaignid=1455363063&utm_adgroupid=65083631748&utm_device=c&utm_keyword=&utm_matchtype=b&utm_network=g&utm_adpostion=&utm_creative=278443377086&utm_targetid=aud-438999696719:dsa-429603003980&utm_loc_interest_ms=&utm_loc_physical_ms=9067607&gclid=CjwKCAjwqML6BRAHEiwAdquMnY-Y7T09n7dDoispZbw9IMz_YumA5TonX1G-lZLVwW1ljzNIdP4HCxoCj88QAvD_BwE
    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    ap.add_argument("-p", "--preset", required=False, action="store_true",
    help="execute preset in code options and exit")
    ap.add_argument("-s", "--source", required=False,
    help="path of source directory")
    ap.add_argument("-d", "--destination", required=False,
    help="path of destination directory")
    ap.add_argument("-a", "--accept_duplicates", required=False, action="store_false",
    help="NO skip duplicates, by default duplicated files are skipped")
    ap.add_argument("-r", "--delete_files", required=False, action="store_true",
    help="delete files existing in source from destination dir, default: False")
    ap.add_argument("-n", "--no_action", required=False, action="store_true",
    help="explain what would be deleted, but there is no action in file system, default: False")
    ap.add_argument("-e", "--export_sorted_newest", required=False, action="store_true",
    help="export sorted files from source to destination directory.\nNote: the source and the destination paths have to be set")
    ap.add_argument("-v", "--verbose", required=False, action="store_true",
    help="explain what is being done")
    ###############################
    ###     Possible options    ###
    ###############################
    # -i                    prompt before every removal
    args = vars(ap.parse_args())

    if len(sys.argv)==1:
        ap.print_help()
        sys.exit(1)

    if args['preset'] == True:
        # python C:\GitHub\Python\duplicated_photos_remove.py -v -p -r 
        auto_scan_directories(
                                sources = ["\\\\networkpc\\image\\Camera", "C:\\image\\Camera"], 
                                destinations = ["D:\\images"], 
                                delete_files=args['delete_files'], 
                                skip_duplicates=args['accept_duplicates'],
                                verbose=args['verbose'],
                                no_action=args['no_action'])
        sys.exit(1)

    if args['export_sorted_newest'] != None:
        # python.exe C:\GitHub\Python\duplicated_photos_remove.py -e -s C:\Kornel_Zdjecia\___Gallery_Gotowe_finalne\2020 -d C:\Kornel_Zdjecia\zz__inne_tmp\tmp_script
        if (args['source'] != None) and (args['destination'] != None):
            source_path = args['source']
            source = DirectoryStructure(source_path, skip_duplicates=False)
            source.scan_directory_for_export()
            
            destination_path = args['destination']

            source.export_sorted_to_destination(destination_path)

            sys.exit(1)
        else:
            print("source and destination have to be set")
            sys.exit(1)



    if (args['source'] == None) and (args['destination'] == None):
            print("source or destination have to be set")
            sys.exit(1)

    if args['source'] != None:
        source_path = args['source']
        source = DirectoryStructure(source_path, skip_duplicates=args['accept_duplicates'])
        source.scan_directory()
        if args['verbose'] == True:
            print("\n\tSource\n")
            source.print_warnings()
            source.print_ignored()
            source.print_duplicates()

    if args['destination'] != None:
        destination_path = args['destination']
        destination = DirectoryStructure(destination_path, skip_duplicates=args['accept_duplicates'])
        destination.scan_directory()
        if args['verbose'] == True:
            print("\n\tDestination\n")
            destination.print_warnings()
            destination.print_ignored()
            destination.print_duplicates()


    if ((args['source'] != None) and (args['destination'] != None)):
        if (args['no_action'] == True):
            destination.prepare_to_delete_existing_files(source)
            destination.print_prepared_to_delete()
        elif args['delete_files']:
            if args['verbose'] == True:
                destination.prepare_to_delete_existing_files(source)
                destination.print_prepared_to_delete()
            destination.delete_prepared_files()
    elif ((args['delete_files'] == True) or (args['no_action'] == True)):
        print("To activate \"no_action\" or \"verbose\" source and destination should be set")


parse_and_execute_cli()
