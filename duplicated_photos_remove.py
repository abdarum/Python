import os
import pprint
import sys
import argparse

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

# source = DirectoryStructure(source_path, skip_duplicates=skip_duplicates_global)
# source.scan_directory()
# # source.print_warnings()
# # source.print_ignored()
# # source.print_duplicates()

# destination = DirectoryStructure(destination_path, skip_duplicates=skip_duplicates_global)
# destination.scan_directory()
# destination.prepare_to_delete_existing_files(source)
# destination.print_prepared_to_delete()
# print("")
# # destination.delete_prepared_files()

def auto_scan_directories(sources, destinations, delete_files, skip_duplicates, verbose):
    for d in destinations:
        for s in sources:
            source = DirectoryStructure(s, skip_duplicates=skip_duplicates)
            source.scan_directory()
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

            if delete_files:
                destination.prepare_to_delete_existing_files(source)
                if verbose == True:
                    destination.print_prepared_to_delete()
                destination.delete_prepared_files()

def parse_boolean_from_string(old_value, string_to_parse):
    if string_to_parse  != None:
        string_to_parse = string_to_parse.lower()
        string_to_parse = string_to_parse.replace(" ", "")
        if string_to_parse in ['true', 't', 'yes', 'y', '1']:
            return True
        elif string_to_parse in ['false', 'f', 'no', 'n', '0']:    
            return False
        else:
            return None
    else:
        return old_value
    

def parse_and_execute_cli():    
# https://www.datacamp.com/community/tutorials/argument-parsing-in-python?utm_source=adwords_ppc&utm_campaignid=1455363063&utm_adgroupid=65083631748&utm_device=c&utm_keyword=&utm_matchtype=b&utm_network=g&utm_adpostion=&utm_creative=278443377086&utm_targetid=aud-438999696719:dsa-429603003980&utm_loc_interest_ms=&utm_loc_physical_ms=9067607&gclid=CjwKCAjwqML6BRAHEiwAdquMnY-Y7T09n7dDoispZbw9IMz_YumA5TonX1G-lZLVwW1ljzNIdP4HCxoCj88QAvD_BwE
    #CLI global variables
    skip_duplicates_bool = True
    delete_files_bool = False

    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    ap.add_argument("-p", "--preset", required=False, action="store_true",
    help="execute preset in code options and exit")
    ap.add_argument("-s", "--source", required=False,
    help="path of source directory")
    ap.add_argument("-d", "--destination", required=False,
    help="path of destination directory")
    ap.add_argument("-m", "--skip_duplicates", required=False,
    help="skip duplicates(True/False or 1/0 or yes/no), default: "+str(skip_duplicates_bool))
    ap.add_argument("-r", "--delete_files", required=False,
    help="delete files existing in source(True/False or 1/0 or yes/no), default: "+str(delete_files_bool))
    ap.add_argument("-n", "--no_action", required=False, action="store_true",
    help="explain what would be deleted, but there is no action in file system, default: False")
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
        auto_scan_directories(sources = ["C:\\Kornel_Zdjecia\\Camera", "C:\\Kornel_Zdjecia\\___Gallery_Gotowe_finalne"], 
                                destinations = ["C:\\Kornel_Zdjecia\\telefon_tmp"], 
                                delete_files=True, 
                                skip_duplicates=True,
                                verbose=args['verbose'])
        sys.exit(1)

    assert (args['source'] != None) and (args['destination'] != None), "source and destination have to be set"

    if args['source'] != None:
        source_path = args['source']

    if args['destination'] != None:
        destination_path = args['destination']

    skip_duplicates_bool = parse_boolean_from_string(skip_duplicates_bool, args['skip_duplicates'])
    delete_files_bool = parse_boolean_from_string(delete_files_bool, args['delete_files'])

    source = DirectoryStructure(source_path, skip_duplicates=skip_duplicates_bool)
    destination = DirectoryStructure(destination_path, skip_duplicates=skip_duplicates_bool)
    source.scan_directory()
    destination.scan_directory()

    if args['verbose'] == True:
        print("\n\tSource\n")
        source.print_warnings()
        source.print_ignored()
        source.print_duplicates()
        print("\n\tDestination\n")
        destination.print_warnings()
        destination.print_ignored()
        destination.print_duplicates()

    if (args['no_action'] == True): # (args['verbose'] == True) and delete_files_bool and 
        destination.prepare_to_delete_existing_files(source)
        destination.print_prepared_to_delete()
    elif delete_files_bool:
        if args['verbose'] == True:
            destination.prepare_to_delete_existing_files(source)
            destination.print_prepared_to_delete()
        destination.delete_prepared_files()


parse_and_execute_cli()
