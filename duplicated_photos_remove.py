import os
import pprint
import sys

# source_path      = "C:\\Kornel_Zdjecia\\___Gallery_Gotowe_finalne"
# destination_path = "C:\\Kornel_Zdjecia\\Camera"


# source_path      = "C:\\Kornel_Zdjecia\\tmp_script_test_source_Camera2"
# destination_path = "C:\\Kornel_Zdjecia\\tmp_script_test_source_Gallery_backup"


source_path      = "C:\\Kornel_Zdjecia\\tmp_script_test_source_source"
destination_path = "C:\\Kornel_Zdjecia\\tmp_script_test_source_source_helper"
skip_duplicates_global = True
# skip_duplicates_global = False


TRUSTED_EXTENSIONS = ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG']
IGNORED_EXTENSIONS = ['.txt']

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
            print("Name: {}\nPaths".format(self.name))
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
        if not (self.find_duplicates_in_current_directory(full_file_path) \
            and self.skip_duplicates):    
            extension = os.path.splitext(full_file_path)[1]
            if extension in TRUSTED_EXTENSIONS:
                self.trusted_files.append(full_file_path)
            elif extension in IGNORED_EXTENSIONS:
                self.ignored_files.append(full_file_path)
            else:
                self.found_not_processed_files.append(full_file_path)
        else:
            duplicates = [f for f in self.trusted_files if (os.path.split(f)[1] == os.path.split(full_file_path)[1])]
            for d in duplicates:
                self.trusted_files.remove(d)

    def scan_directory(self, full_file_path=None):
        if full_file_path is None:
            full_file_path = self.root_directory
        result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(full_file_path) for f in filenames]
        [self.classify_file(file_path) for file_path in result]

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
        for trusted in self.trusted_files:
            if os.path.split(trusted)[1] in [os.path.split(f)[1] for f in reference.trusted_files]:
                self.delete_from_current_directory.append(trusted)

    def delete_prepared_files(self):
        for f in self.delete_from_current_directory:
            os.remove(f)
        print("\n\n*************************\n**** DELETE COMPLETE ****\n*************************")


    def print_warnings(self):
        print("\n\n***********************\n****    WARNINGS   ****\n***********************")
        for f in self.found_not_processed_files:
            print("Warning: File was not foud:\n{}\n".format(f))

    def print_ignored(self):
        print("\n\n***********************\n****    IGNORED    ****\n***********************")
        for f in self.ignored_files:
            print("IGNORED: File was ignored:\n{}\n".format(f))

    def print_duplicates(self):
        self.duplicated_files.print_duplicates()

    def print_prepared_to_delete(self):
        print("\n\n***********************\n****    DELETE     ****\n***********************")
        for f in self.delete_from_current_directory:
            print("DELETE: File will be deleted:\n{}\n".format(f))

source = DirectoryStructure(source_path, skip_duplicates=skip_duplicates_global)
source.scan_directory()
# source.print_warnings()
# source.print_ignored()
# source.print_duplicates()

destination = DirectoryStructure(destination_path, skip_duplicates=skip_duplicates_global)
destination.scan_directory()
destination.prepare_to_delete_existing_files(source)
destination.print_prepared_to_delete()
print("")
# destination.delete_prepared_files()