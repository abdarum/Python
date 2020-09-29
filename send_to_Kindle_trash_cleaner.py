#/usr/bin/python3

#import built-in modules
import os
import shutil
import sys
import argparse


__author__  = 'Kornel Stefańczyk'
__license__ = 'CC BY-SA'
__version__ = 1.0
__maintainer__ = 'Kornel Stefańczyk'
__email__ = 'kornelstefanczyk@wp.pl'


def debug(msg, active_debugging=True, end_=None):
    """Print msg to terminal"""
    if active_debugging:
        if end_:
            print(msg, end=end_)
        else:
            print(msg)


def get_bool(text_to_display='', nothing_as_None=False):
    true_list = ['True', 'TRUE', 'true', 'T', 't', 'Yes', 'YES', 'yes', 'Y',
            'y', '1']
    false_list = ['False', 'FALSE', 'false', 'F', 'f', 'No', 'NO', 'no',
            'N', 'n', '0']
    try:
        val = str(input(text_to_display))
        if (val == '') and nothing_as_None:
            return None

        for i in true_list:
            if val == i:
                return True
        for i in false_list:
            if val == i:
                return False
        raise NameError('Not mach option')
    except NameError:
        print('You typped wrong value. Please do it again correctly.')
        return get_bool(text_to_display=text_to_display,
                nothing_as_None=nothing_as_None)


class UserInterface:
    def __init__(self):
        self.f_mng = FileManager()


        parser = argparse.ArgumentParser(description='Cleaning trash '
                +'created by sending docs to Kindle via Internet '+
                'and removing books from Kindle device\n\n'+
                'Script features:'+
                '\n\t* list files in main dir downloaded from the internet'+
                ' and allows to move it to separate directory'+
                '\n\t* list trash after removing books from the Kindle device'+
                ' and allows to remove trash files',
                formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument('-m', '--main-path', action='store', nargs=1, 
                required=True,
                help='path to main dir on Kindle device e.g. \'G:\\documents\' ')
        parser.add_argument('-s', '--stk-dir-name', action='store', nargs=1,
                help='name of send to Kindle folder(should be subdirectory '+
                    '--main-path),'+
                    '\ndefault: \'MAIN_PATH\\send_to_kindle\''+
                    ', if not exist it is created')

        #group = parser.add_mutually_exclusive_group()
        group = parser

        only_display__mode = group.add_argument_group('only display')
        only_display__mode.add_argument('-P', '--only-display', action='store_true',
                help='only display info, move and delete is not processed')

        normal_mode = group.add_argument_group('normal')
        normal_mode.add_argument('-f', '--force', action='store_true',
                help='force - agree for all move and remove operation')
        normal_mode.add_argument('-p', '--print', action='store_true',
                help='display info')
        normal_mode.add_argument('-r', '--recursive', action='store_true',
                help='scan in subfolders')


        args = parser.parse_args()

        if args.main_path:
            debug('main_path: '+args.main_path[0],active_debugging=False)
            self.f_mng.main_path = args.main_path[0]
            self.f_mng.send_to_kindle_dir_path(
                    name=self.f_mng.send_to_kindle_default_name)
        if args.stk_dir_name:
            debug('stk_dir_name: '+args.stk_dir_name[0],active_debugging=False)
            self.f_mng.send_to_kindle_dir_path(name=args.stk_dir_name[0])

        if args.recursive:
            debug('recursive',active_debugging=False)
            self.f_mng.find_recursive()
        else:
            debug('not recursive',active_debugging=False)
            self.f_mng.find_data_files()
        if args.only_display:
            debug('only display',active_debugging=False)
            self.f_mng.print_data()
        else:

            if args.force:
                debug('force',active_debugging=False)
                self.f_mng.move(force=True)
                self.f_mng.remove(force=True)
            else:
                debug('not force',active_debugging=False)
                self.f_mng.move(force=False)
                self.f_mng.remove(force=False)
            if args.print:
                debug('display info',active_debugging=False)
                self.f_mng.print_data()




class FileManager:
    def __init__(self):
        self.data_container = list()
        self.dir_to_check = list()
        self.files_to_move = list()
        self.send_to_kindle_default_name = 'send_to_kindle'
        self.main_path = os.getcwd()
        self.send_to_kindle_dir_path(name=self.send_to_kindle_default_name)


    def find_data_files(self, path=None):
        if path is None:
            path = self.main_path
        path_list = list()
        for tmp in  os.scandir(path):
            path_list.append(tmp.path)
        for tmp in os.scandir(path):
            if not tmp.name.startswith('.') and tmp.is_dir():

                if tmp.name.endswith('.sdr'):
                    common_path_part = tmp.path.replace('.sdr','')
                    common_path_files_list = list()
                    for i in path_list:
                        if i.startswith(common_path_part):
                            common_path_files_list.append(i)
                    if not len(common_path_files_list)>1:
                        self.data_container.append(tmp)
                    else:
                        if path.endswith('documents')  or \
                                path.endswith('documents'+os.sep) and \
                                not tmp.name.startswith("My Clippings"):
                            self.files_to_move.append(common_path_files_list)
                else:
                    self.dir_to_check.append(tmp)

    def find_recursive(self, path=None):
        if path is None:
            path = self.main_path
        self.find_data_files(path)
        while len(self.dir_to_check):
            tmp_list = list(self.dir_to_check)
            self.dir_to_check = list()
            for i in tmp_list:
                self.find_data_files(path=i.path)

    def remove(self, force=False):
        debug('\n\tRemove elements')
        for i in self.data_container:
            if not force:
                remove = get_bool(text_to_display='Do you want to remove: '
                        +str(i.path)+'\n')
            else:
                remove = True
            if remove:
                shutil.rmtree(i.path)

    def move(self, force=False):
        debug('\n\tMove elements')
        try:
            os.mkdir(path=self.send_to_kindle_path)
            debug('Created dir: '+self.send_to_kindle_path)
        except FileExistsError:
            pass

        for tmp in self.files_to_move:
            if not force:
                name = tmp[0]
                for i in tmp:
                    if i.endswith('.sdr'):
                        name = i[:-4]
                move = get_bool(text_to_display='Do you want to move: '
                        +name+' to '+self.send_to_kindle_path+'\n')
            else:
                move = True
            if move:
                for i in tmp:
                    shutil.move(src=i,dst=self.send_to_kindle_path)

    def send_to_kindle_dir_path(self, name):
        if self.main_path.endswith(os.sep):
            self.send_to_kindle_path = self.main_path + str(name)
        else:
            self.send_to_kindle_path = self.main_path + os.sep + str(name)


    def print_data(self):
        print('\nMain directiory path:', self.main_path)
        print('Send to Kindle directory path:', self.send_to_kindle_path)
        print('\n\tFound possible trash in current dir:')
        for i in self.data_container:
            print(i.name,'path',i.path)
        print('\n\tFound possible trash in sub dirs:')
        for i in self.dir_to_check:
            print(i.name,'path',i.path)
        print('\n\tFiles to move:')
        print(self.files_to_move)



UserInterface()
