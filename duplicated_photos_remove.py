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


TRUSTED_EXTENSIONS = ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG',
                      '.mp4', '.MP4'
                      ]
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

    def scan_directory_for_export(self, full_file_path=None):
        if full_file_path is None:
            full_file_path = self.root_directory
        if self.skip_duplicates:
            pass
        else:
            # python.exe .\duplicated_photos_remove.py -e 5 -s C:\Kornel_Zdjecia\___Gallery_Gotowe_finalne\2020 -d C:\Kornel_Zdjecia\zz__inne_tmp\tmp_script
            print("\n\n\n")
            print(full_file_path)
            print("\n\n\n")
            result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(full_file_path) for f in filenames]
            [print(file_path) for file_path in result]

            # sss
            pass

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


def auto_scan_directories(sources, destinations, delete_files, skip_duplicates, verbose, no_action):
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
    help="delete files existing in source, default: False")
    ap.add_argument("-n", "--no_action", required=False, action="store_true",
    help="explain what would be deleted, but there is no action in file system, default: False")
    ap.add_argument("-e", "--export_sorted_newest", required=False, type=int,
    help="export sorted files newer than number of days from source to destination directory\nNote source and destination has to be set")
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
        auto_scan_directories(sources = ["C:\\Kornel_Zdjecia\\Camera", "C:\\Kornel_Zdjecia\\___Gallery_Gotowe_finalne", "C:\\Kornel_Zdjecia\\___Movie_Gallery_Gotowe_finalne"], 
                                destinations = ["C:\\Kornel_Zdjecia\\telefon_tmp"], 
                                delete_files=args['delete_files'], 
                                skip_duplicates=args['accept_duplicates'],
                                verbose=args['verbose'],
                                no_action=args['no_action'])
        sys.exit(1)

    if args['export_sorted_newest'] != None:
        if (args['source'] != None) and (args['destination'] != None):
            source_path = args['source']
            source = DirectoryStructure(source_path, skip_duplicates=False)
            source.scan_directory_for_export()
            
            destination_path = args['destination']

            #todo
            #scan with dates
            # move only from main dir in source to dest
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
