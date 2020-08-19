import os
import sys
import pprint

source_path = "C:\\Kornel_Zdjecia\\tmp_script_test_source_Camera2"
destination_path = "C:\\Kornel_Zdjecia\\tmp_script_test_source_Gallery_backup"


TRUSTED_EXTENSIONS = ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG']
IGNORED_EXTENSIONS = ['.txt']


source_files = []
destination_files = []
class DirectoryStructure:
    def __init__(self, root_directory=None):
        self.found_not_processed_files = []
        self.trusted_files = []
        self.ignored_files = []
        self.root_directory = root_directory

    def classify_file(self, full_file_path):
        extension = os.path.splitext(full_file_path)[1]
        if extension in TRUSTED_EXTENSIONS:
            self.trusted_files.append(full_file_path)
        elif extension in IGNORED_EXTENSIONS:
            self.ignored_files.append(full_file_path)
        else:
            self.found_not_processed_files.append(full_file_path)

    def scan_directory(self, full_file_path=None):
        if full_file_path is None:
            full_file_path = self.root_directory
        result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(full_file_path) for f in filenames]
        [self.classify_file(file_path) for file_path in result]

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
