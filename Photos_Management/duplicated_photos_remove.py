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
import json
import pytest
import inspect

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
if not os.path.exists(gen_dir_path):
    os.makedirs(gen_dir_path)

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
    
    def get_duplicates_filenames(self):
        return [duplicate_item.get_name() for duplicate_item in self.list_of_duplicate_items]
            
class DirectoryStructure:
    """A class used to store and manage files in directory"""
    class FileProperties:
        """A class used to store file properties"""
        def __init_structures(self):
            self.__sources_dict = {}
            self.filename = None

        def __init__(self, path):
            self.__init_structures()
            if path:
                self.add_path(path)
        
        def __get_first_dir_path(self):
            dir_path = str(self.get_dir_paths()[0])
            return dir_path

        def add_path(self, path):
            """Add path to current file properties object"""
            filename = os.path.split(path)[1]
            dir_path = os.path.split(path)[0]
            if self.filename is None:
                self.filename = filename
            assert filename == self.filename, "Filename must be the same for all paths"
            self.__sources_dict[dir_path] = {}

        def extend(self, ext_file_prop):
            """
            Extend current object based on external FileProperties object

            Add new paths of filename

            Parameters
            ----------
            ext_file_prop : FileProperties
                external FileProperties object
            """
            ext_file_path = ext_file_prop.get_first_file_path()
            self.add_path(ext_file_path)
        
        def get_file_extension(self):
            extension = os.path.splitext(self.filename)[1]
            return extension

        def get_filename(self):
            return self.filename

        def get_first_file_path(self):
            """Get full file path of file used to init object"""
            dir_path = self.__get_first_dir_path()
            filename = self.get_filename()
            full_path = os.path.join(dir_path, filename)
            return full_path

        def get_file_paths_list(self):
            """Get list of full file paths"""
            file_paths_list = self.get_dir_paths()
            filename = self.get_filename()
            full_path_list = [os.path.join(dir_path, filename) for dir_path in file_paths_list]
            return full_path_list

        def get_dir_paths(self):
            return list(self.__sources_dict.keys())

        def file_in_multiple_directories(self):
            return len(self.get_dir_paths()) > 1
        
        def file_extensions_is_trusted(self):
            return self.get_file_extension() in TRUSTED_EXTENSIONS
        
        def file_extensions_is_ignored(self):
            return self.get_file_extension() in IGNORED_EXTENSIONS

    def __init__(self):
        self.__files_map_dict = {}

    def get_stored_filenames(self):
        """Get keys of filenames stored in class"""
        return self.__files_map_dict.keys()

    def get_file_property(self, filename_key):
        return self.__files_map_dict.get(filename_key)

    def add_file_path(self, file_path):
        """Add add file path to directory structure(update existing or add new)"""
        file_properties = DirectoryStructure.FileProperties(file_path)
        if file_properties.get_filename() in self.get_stored_filenames():
            self.__files_map_dict.get(file_properties.get_filename()).extend(file_properties)
        else:
            self.__files_map_dict[file_properties.get_filename()] = file_properties

    def iterate_files(self):
        for file_key in self.get_stored_filenames():
            item = self.get_file_property(file_key)
            yield item

class FilesManager:
    def __init__(self, root_directory=None):
        self.root_directory_path = root_directory
        self.nested_files_list = None
        self.directory_structure = DirectoryStructure()
        self.prepare_nested_file_paths_list()

    def prepare_nested_file_paths_list(self):
        self.nested_files_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.root_directory_path) for f in filenames]

    def get_directory_structure(self):
        return self.directory_structure

    def scan_directory(self):
        assert not self.nested_files_list is None
        logger.info('scan_directory {} - Number of files found {}'.format(self.root_directory_path, len(self.nested_files_list)))
        [self.directory_structure.add_file_path(file_path) for file_path in tqdm.tqdm(self.nested_files_list, desc="Scan directory")]

    def print_duplicates(self):
        item: DirectoryStructure.FileProperties = None
        print("\n\n***********************\n****   DUPLICATES  ****\n***********************")
        for item in self.directory_structure.iterate_files():
            if item.file_in_multiple_directories():
                print("Duplicate  - Filename: {}\nPaths".format(item.get_filename()))
                pprint.pprint(item.get_file_paths_list())
                print("")

    def print_ignored(self):
        print("\n\n***********************\n****    IGNORED    ****\n***********************")
        item: DirectoryStructure.FileProperties = None
        for item in self.directory_structure.iterate_files():
            if item.file_extensions_is_ignored():
                log_msg = "IGNORED: File was ignored:\n{}\n".format(item.get_filename())
                print(log_msg)
                json_log = "print_ignored - {}".format(log_msg.replace('\n', ' '))
                logger.info(json_log)

    def print_warnings(self):
        print("\n\n***********************\n****    WARNINGS   ****\n***********************")
        item: DirectoryStructure.FileProperties = None
        for item in self.directory_structure.iterate_files():
            if (not item.file_extensions_is_ignored()) and (not item.file_extensions_is_trusted()):
                log_msg = "Warning: File was not found:\n{}\n".format(item.get_filename())
                print(log_msg)
                json_log = "print_warnings - {}".format(log_msg.replace('\n', ' '))
                logger.info(json_log)

class DuplicatesRemover(FilesManager):
    def __init__(self, root_directory=None, skip_duplicates=True):
        """       
        Parameters
        ----------
        root_directory : str
            path to root directory, where search should be executed
        skip_duplicates : bool
            True - skip delete files with multiple sources(duplicates)
            False - delete all images(also duplicated files)
        """
        super(DuplicatesRemover, self).__init__(root_directory)
        self.delete_from_current_directory = []
        self.delete_duplicates = not bool(skip_duplicates)

    def file_should_be_deleted(self, file_properties: DirectoryStructure.FileProperties, reference):
        """Return bool if file should be deleted"""
        item = file_properties
        # check if item is stored in reference DuplicatesRemover object
        if item.get_filename() in reference.get_directory_structure().get_stored_filenames():
            # check if file has duplicates or delete duplicated
            if not item.file_in_multiple_directories() or self.delete_duplicates:
                if item.file_extensions_is_trusted():
                    return True
        return False

    def prepare_to_delete_existing_files(self, reference):
        assert isinstance(reference, DuplicatesRemover), "reference must be a object of DuplicatesRemover class"
        for item in tqdm.tqdm(self.directory_structure.iterate_files(), desc="Prepare to delete duplicates"):
            if self.file_should_be_deleted(item, reference):
                self.delete_from_current_directory.extend(item.get_file_paths_list())
                logger.info("prepare_to_delete_existing_files - file('s) will be deleted: {}".format(item.get_file_paths_list()))

    def delete_prepared_files(self):
        for f in self.delete_from_current_directory:
            os.remove(f)
            logger.info("delete_prepared_files - file was deleted: {}".format(f))
        print("\n\n*************************\n**** DELETE COMPLETE ****\n*************************")

    def print_prepared_to_delete(self):
        print("\n\n***********************\n****    DELETE     ****\n***********************")
        for f in self.delete_from_current_directory:
            log_msg = "DELETE: File will be deleted:\n{}\n".format(f)
            print(log_msg)
            json_log = "print_prepared_to_delete - {}".format(log_msg.replace('\n', ' '))
            logger.info(json_log)


class CompressExporter(FilesManager):
    def classify_file_for_export(self, full_file_path):
        if not (self.find_duplicates_in_current_directory(full_file_path) \
            and self.delete_duplicates):    
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

    def export_sorted_to_destination(self, destination_path):
        for export_source_path in tqdm.tqdm(self.trusted_files):
            export_relative_path = export_source_path.replace(self.root_directory_path, '')
            export_destination_path = destination_path + export_relative_path
            os.makedirs(os.path.dirname(export_destination_path), exist_ok=True)
            if not os.path.isfile(export_destination_path):
                shutil.copyfile(export_source_path, export_destination_path)
                picture = Image.open(export_destination_path)
                picture.save(export_destination_path,optimize=True,quality=30) 

    def scan_directory_for_export(self, full_file_path=None):
        if full_file_path is None:
            full_file_path = self.root_directory_path
        if self.delete_duplicates:
            pass
        else:
            result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(full_file_path) for f in filenames]
            [self.classify_file_for_export(file_path) for file_path in result]

class TestDuplicatesRemover:
    DATASET_FOR_TESTS_PATH = 'PythonPrivate\\Photos_Management\\test_duplicates_dataset.json'

    # run from command line
    # python -m pytest Photos_Management\duplicated_photos_remove.py::TestDuplicatesRemover
    # 
    # run from python script
    # retcode = pytest.main(["<X:\\abs_repo_path>\\Photos_Management\\duplicated_photos_remove.py::TestDuplicatesRemover"])
    #     with console output add -s parameter
    #     retcode = pytest.main(["<X:\\abs_repo_path>\\Photos_Management\\duplicated_photos_remove.py::TestDuplicatesRemover", "-s"])

    ######################
    ###  Tools
    ######################
    @staticmethod
    def print_variable_to_file(variable, file_path=None):
        str_to_print = None
        str_to_print = str(variable)
        if str_to_print:
            if file_path is None:
                file_path = "gen/log_variable.txt"
            file_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
            with open(file_path, 'w') as f:
                print(str_to_print, file=f)
    
    @staticmethod
    def save_dict_to_json(variable, file_path=None):
        str_to_print = None
        str_to_print = json.dumps(variable, indent=4, ensure_ascii=False)
        if str_to_print:
            if file_path is None:
                file_path = "gen/log_variable.json"
            file_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
            with open(file_path, 'w') as f:
                print(str_to_print, file=f)
    
    def load_dataset(self):
        data = None
        file_path = os.path.abspath(os.path.join(os.getcwd(), self.DATASET_FOR_TESTS_PATH))
        with open(file_path) as f:
            data = json.load(f)
        f.close()
        return data

    def load_dataset_section(self, method_name):
        data = self.load_dataset()
        section_data = data.get(method_name)
        section_data['method_name'] = method_name
        return section_data

    def convert_paths_list_to_filenames_list(self, data_list):
        return [os.path.split(path)[1] for path in data_list]
        
    def find_duplicates_at_paths_list(self, data_list):
        filenames_list = self.convert_paths_list_to_filenames_list(data_list)
        duplicates = list({x for x in filenames_list if filenames_list.count(x) > 1})
        duplicates = [item for item in duplicates if True in [item.endswith(extension) for extension in TRUSTED_EXTENSIONS]]
        return duplicates

    def print_saved_preset_data(self, data):
        print('\n\n*****   Preset data summary   *****')

        method_name = data.get('method_name')
        print('\tpreset: {}'.format(method_name))

        d_scanned_files_list = data.get('destination.nested_files_list')
        d_scanned_files_list_len = len(d_scanned_files_list)
        d_scanned_files_list_dup = self.find_duplicates_at_paths_list(d_scanned_files_list)
        print('Destination files: {}. Destination duplicates({}) {}.'.format(d_scanned_files_list_len, len(d_scanned_files_list_dup), d_scanned_files_list_dup))

        s_scanned_files_list = data.get('source.nested_files_list')
        s_scanned_files_list_len = len(s_scanned_files_list)
        s_scanned_files_list_dup = self.find_duplicates_at_paths_list(s_scanned_files_list)
        print('Source files: {}. Source duplicates({}) {}.'.format(s_scanned_files_list_len, len(s_scanned_files_list_dup), s_scanned_files_list_dup))

        print('') #separator

        d_delete_from_current_directory = data.get('destination.delete_from_current_directory')
        d_delete_from_current_directory_len = len(d_delete_from_current_directory)
        print('{} \t files will be deleted from destination dir'.format(d_delete_from_current_directory_len))

        print('') #separator

        d_duplicated_files = data.get('destination.duplicated_files.get_duplicates_filenames()')
        print('Processed duplicates at destination: {}'.format(d_duplicated_files))

        skip_duplicates = data.get('skip_duplicates')
        print('Skip duplicates: {}'.format(skip_duplicates))
        print('*****   Preset data summary   *****\n\n')


    def compare_execution_data_with_saved_preset(self, data):
        # destination.delete_from_current_directory list will be compared with saved list from attached data
        #   Files won't be deleted from pc
        #   data = {'s': '\\\\online_pc\\IMGS', 'd': 'C:\\local_pc\\IMGS', 'delete_files': true, 'skip_duplicates': false, 'verbose': true, 'no_action': true, 'source.nested_files_list': [], 'destination.delete_from_current_directory': [], 'destination.nested_files_list': []}
        self.print_saved_preset_data(data)
        skip_duplicates = data.get('skip_duplicates')
        s = data.get('s')
        d = data.get('d')

        # source
        source = DuplicatesRemover(s, skip_duplicates=skip_duplicates)
        source.nested_files_list = data['source.nested_files_list']
        source.scan_directory()

        # destination
        destination = DuplicatesRemover(d, skip_duplicates=skip_duplicates)
        destination.nested_files_list = data['destination.nested_files_list']
        destination.scan_directory()

        destination.prepare_to_delete_existing_files(source)

        set_data = set(data['destination.delete_from_current_directory'])
        set_test = set(destination.delete_from_current_directory)
        assert set_data == set_test


    ######################
    ###  Test cases
    #######################
    def test_real_case_scenario_1(self):
        # In directory there is no duplicates. Delete 31 repeating files
        # Old implementation passed in 154.49s (0:02:34)
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)

    def test_real_case_scenario_2(self):
        # In directory there is no duplicates. No files to delete
        # Old implementation passed in 1.32s
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)

    def test_real_case_scenario_3(self):
        # In directory there is no duplicates. No files to delete. Source files: 20883. Destination files: 835.
        # Old implementation passed in 85.71s (0:01:25)
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)

    def test_real_case_scenario_4(self):
        # In directory there is 9 duplicates. No files to delete. Source files: 168. Destination files: 1178.
        # Old implementation passed in 2.08s
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)

    def test_real_case_scenario_5(self):
        # In directory there is 1 duplicates. No files to delete. skip_duplicates=True
        # Old implementation passed in 1.72s
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)

    def test_real_case_scenario_6(self):
        # In directory there is 1 duplicates. No files to delete
        # Old implementation passed in 0.50s
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)

    def test_real_case_scenario_7(self):
        # In directory there is 6 duplicates. 754 files to delete
        # Old implementation passed in 93.27s (0:01:33)
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)

    def test_real_case_scenario_8(self):
        # In directory there is 6 duplicates. No files to delete
        # Old implementation passed in 2.23s
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)

    def test_real_case_scenario_9(self):
        # In directory there is 9 duplicates. 751 files to delete. skip_duplicates=True
        # Old implementation passed in 923.46s (0:15:23)
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)

    def test_real_case_scenario_10(self):
        # In directory there is 9 duplicates. No files to delete. skip_duplicates=True
        # Old implementation passed in 3.47s
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)

    def test_real_case_scenario_11(self):
        # In directory there is 9 duplicates. 757 files to delete
        # Old implementation passed in 83.20s (0:01:23)
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)

    def test_real_case_scenario_12(self):
        # In directory there is 9 duplicates. No files to delete
        # Old implementation passed in 3.21s
        method_name = inspect.stack()[0][3]
        loaded_dataset = self.load_dataset_section(method_name)
        self.compare_execution_data_with_saved_preset(loaded_dataset)


def auto_scan_directories(sources, destinations, delete_files, skip_duplicates, verbose, no_action):
    SAVE_PROCESSING_DATA = False
    save_dict = {}
    for d in destinations:
        for s in sources:
            curr_scan_dict = {}
            # Source
            if verbose == True:
                print("Directory path: {}".format(s))
            source = DuplicatesRemover(s, skip_duplicates=skip_duplicates)
            source.scan_directory()
            # Destination
            if verbose == True:
                print("Directory path: {}".format(d))
            destination = DuplicatesRemover(d, skip_duplicates=skip_duplicates)
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

            if SAVE_PROCESSING_DATA:
                curr_scan_dict.update({'s':s, 'd':d, 'delete_files':delete_files, 'skip_duplicates':skip_duplicates, 'verbose':verbose, 'no_action':no_action })
                curr_scan_dict['source.nested_files_list'] = source.nested_files_list
                curr_scan_dict['source.duplicated_files.get_duplicates_filenames()'] = source.duplicated_files.get_duplicates_filenames()
                curr_scan_dict['destination.delete_from_current_directory'] = destination.delete_from_current_directory
                curr_scan_dict['destination.nested_files_list'] = destination.nested_files_list
                curr_scan_dict['destination.duplicated_files.get_duplicates_filenames()'] = destination.duplicated_files.get_duplicates_filenames()
                save_dict['{}{}'.format(s,d)] = curr_scan_dict
    if SAVE_PROCESSING_DATA:
        TestDuplicatesRemover.save_dict_to_json(save_dict)


def parse_and_execute_cli():    
# https://www.datacamp.com/community/tutorials/argument-parsing-in-python?utm_source=adwords_ppc&utm_campaignid=1455363063&utm_adgroupid=65083631748&utm_device=c&utm_keyword=&utm_matchtype=b&utm_network=g&utm_adpostion=&utm_creative=278443377086&utm_targetid=aud-438999696719:dsa-429603003980&utm_loc_interest_ms=&utm_loc_physical_ms=9067607&gclid=CjwKCAjwqML6BRAHEiwAdquMnY-Y7T09n7dDoispZbw9IMz_YumA5TonX1G-lZLVwW1ljzNIdP4HCxoCj88QAvD_BwE
    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    ap.add_argument("-p", "--preset", required=False, action="store_true",
    help="execute preset in code options and exit")
    ap.add_argument("-P", "--preset_path", required=False, 
    help="path of preset config file - execute preset and exit")
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

    if args['preset_path'] != None:
        # python C:\GitHub\Python\duplicated_photos_remove.py -P C:\\GitHub\\Python\\Photos_Management\\config_file.json 
        preset_config_path = args['preset_path'].strip()
        with open(preset_config_path, 'r') as f:
            data = json.load(f)
            tmp_var2 = ''
            auto_scan_directories(**data)
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
            source = CompressExporter(source_path)
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
        source = DuplicatesRemover(source_path, skip_duplicates=args['accept_duplicates'])
        source.scan_directory()
        if args['verbose'] == True:
            print("\n\tSource\n")
            source.print_warnings()
            source.print_ignored()
            source.print_duplicates()

    if args['destination'] != None:
        destination_path = args['destination']
        destination = DuplicatesRemover(destination_path, skip_duplicates=args['accept_duplicates'])
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


if __name__=='__main__':
    parse_and_execute_cli()
