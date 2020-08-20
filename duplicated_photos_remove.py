import os
import sys
import pprint

# source_path = "C:\\Kornel_Zdjecia\\tmp_script_test_source_Camera2"
# destination_path = "C:\\Kornel_Zdjecia\\tmp_script_test_source_Gallery_backup"


source_path = "C:\\Kornel_Zdjecia\\tmp_script_test_source_source"
destination_path = "C:\\Kornel_Zdjecia\\tmp_script_test_source_source_helper"

TRUSTED_EXTENSIONS = ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG']
IGNORED_EXTENSIONS = ['.txt']

class Duplicates:
    class DuplicateItem:
        def __init__(self, list_of_paths, name):
            self.list_of_paths = list_of_paths
            self.name = name
            pass


    def __init__(self):
        self.list_of_duplicate_items = []

    def create_duplicate(self, paths):
        # 'paths' is list of paths containing duplicated files
        #todo
        print('create duplicates')
        pprint.pprint(paths)
        print("")
        pass

    def add_to_existing_duplicate(self, paths):
        # 'paths' is list of paths containing duplicated files
        #todo
        print('update duplicates')
        pprint.pprint(paths)
        print("")
        pass

    def duplicate_exist_in_base(self, paths):
        # 'paths' is list of paths containing duplicated files
        #todo
        return True
        # return False

class DirectoryStructure:
    def __init__(self, root_directory=None):
        self.found_not_processed_files = []
        self.trusted_files = []
        self.ignored_files = []
        self.duplicated_files = Duplicates()
        self.root_directory = root_directory

    def classify_file(self, full_file_path):
        extension = os.path.splitext(full_file_path)[1]
        if extension in TRUSTED_EXTENSIONS:
            self.trusted_files.append(full_file_path)
        elif extension in IGNORED_EXTENSIONS:
            self.ignored_files.append(full_file_path)
        else:
            self.found_not_processed_files.append(full_file_path)
        
        self.find_duplicates(full_file_path)

    def scan_directory(self, full_file_path=None):
        if full_file_path is None:
            full_file_path = self.root_directory
        result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(full_file_path) for f in filenames]
        [self.classify_file(file_path) for file_path in result]

    def find_duplicates(self, full_file_path):
        if os.path.split(full_file_path)[1] in [os.path.split(f)[1] for f in self.trusted_files]:
            if self.duplicated_files.duplicate_exist_in_base([full_file_path]):
                self.duplicated_files.add_to_existing_duplicate([full_file_path])
            else:
                duplicates = [f for f in self.trusted_files \
                        if (os.path.split(f)[1] == os.path.split(full_file_path)[1])]
                self.duplicated_files.create_duplicate(duplicates)

    def print_warnings(self):
        print("\n\n***********************\n****    WARNINGS   ****\n***********************")
        for f in self.found_not_processed_files:
            print("Warning: File was not foud:\n{}\n".format(f))

    def print_ignored(self):
        print("\n\n***********************\n****    IGNORED    ****\n***********************")
        for f in self.ignored_files:
            print("IGNORED: File was ignored:\n{}\n".format(f))

source = DirectoryStructure(source_path)
source.scan_directory()
source.print_warnings()
source.print_ignored()
