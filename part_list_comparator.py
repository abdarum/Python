#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv, codecs, cStringIO
import os
import sys
import argparse
import shutil
import codecs

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def get_integer(text_to_display='', min_value=None,
        max_value=None, nothing_as_None=False):
    try:
        val = str(raw_input(text_to_display))
        if (val == '') and nothing_as_None:
            return None
        val = int(val)
        if min_value and val<min_value:
            raise NameError('low')
        if max_value and val>max_value:
            raise NameError('high')
        return val
    except ValueError:
        print('You typped wrong value. Please do it again correctly.')
        return get_integer(text_to_display=text_to_display,
                min_value=min_value, max_value=max_value,
                nothing_as_None=nothing_as_None)
    except NameError:
        if min_value and max_value:
            print('You should type value between '+str(min_value)+' and '+
                    str(max_value)+' Please do it again correctly.')
        elif min_value:
            print('You should type value greater or equal than '+str(min_value)+
                    '. Please do it again correctly.')
        elif max_value:
            print('You should type value less or equal than '+str(max_value)+
                    '. Please do it again correctly.')
        else:
            print('You typped wrong value. Please do it again correctly.')

        return get_integer(text_to_display=text_to_display,
                min_value=min_value, max_value=max_value,
                nothing_as_None=nothing_as_None)


class UserInterface:
    def __init__(self):
        self.cont = Container()
        parser = argparse.ArgumentParser(description='Find diffrences '+
                 'in part list')

        parser.add_argument('-i', '--input-name', action='store', nargs=1,
                help='path to file to check')
        parser.add_argument('-s', '--save-changes', action='store_true',
                help='save changes in input files')
        parser.add_argument('-k', '--ktm-code-log', action='store', nargs=1,
                help='path to file with ktm codes')
        parser.add_argument('-d', '--disp-code-to-check', action='store_true',
                help='display code to check')

        """
        parser.add_argument('-o', '--log-name', action='store', nargs=1,
                help='path to log file')
        """

        args = parser.parse_args()


        if args.input_name:
            self.cont.csv_read(filename=args.input_name[0])

            self.cont.sort_by()
            self.cont.group()

            self.cont.find_diff_group()
            if args.save_changes:
                self.cont.fix_all_differences()
                self.cont.csv_write(filename=args.input_name[0])
            else:
                self.cont.print_diff()

            if args.ktm_code_log:
                self.cont.print_to_check(args.ktm_code_log[0])
            else:
                if args.disp_code_to_check:
                    self.cont.print_to_check()

        """
        if args.log_name:
            pass
            #self.f_mng.send_to_kindle_dir_path(name=args.stk_dir_name[0])
        """
        if len(sys.argv)==1:
            parser.print_help()

class DataIndex:
    def __init__(self, name, f_col=None,
            c_idx=None, descr=None, diffrent=True):
        self.name = name
        self.f_col = f_col #column in file
        if c_idx==None and f_col!=None:
            self.c_idx = f_col #idx in container
        else:
            self.c_idx = c_idx
        self.descr = descr
        self.diffrent = diffrent

    def print_data(self):
        print('Name: ',self.name)
        print('Col in file: ',self.f_col)
        print('Index in container: ',self.c_idx)
        print('Description: ',self.descr)
        print('Can be diffrent in elements: ',self.diffrent)


class DataConfiguration:
    def __init__(self):
        self.conf_list = list()
        self.conf_list.append(DataIndex(name="idx",
            f_col=0, c_idx=0, descr="L,P,"))
        self.conf_list.append(DataIndex(name="page", f_col=1,
            c_idx=1, descr="Str,"))
        self.conf_list.append(DataIndex(name="qnt",
            f_col=2, c_idx=2, descr="Ilość"))
        self.conf_list.append(DataIndex(name="schem_idx",
            f_col=3, c_idx=3, descr="Nr na schemacie"))
        self.conf_list.append(DataIndex(name="manuf_code", f_col=4,
            c_idx=4, descr="Kod producenta", diffrent=False))
        self.conf_list.append(DataIndex(name="ktm_code",
            f_col=5, c_idx=5, descr="Kod KTM", diffrent=False))
        self.conf_list.append(DataIndex(name="type",
            f_col=6, c_idx=6, descr="Typ", diffrent=False))
        self.conf_list.append(DataIndex(name="manuf_name",
            f_col=7, c_idx=7, descr="Firma", diffrent=False))
        self.conf_list.append(DataIndex(name="descript",
            f_col=8, c_idx=8, descr="Opis", diffrent=False))
        self.conf_list.append(DataIndex(name="module_name",
            f_col=9, c_idx=9, descr="Funkcja"))
        self.conf_list.append(DataIndex(name="machine_name", f_col=10,
            c_idx=10))

        self.sort_key_idx = self.c_idx_of('ktm_code')

    def print_data(self):
        for i in self.conf_list:
            i.print_data()

    def c_idx_of(self,name):
        for i in self.conf_list:
            if i.name == name:
                return i.c_idx

    def max_c_idx(self):
        max_idx = 0
        for i in self.conf_list:
            if i.c_idx > max_idx:
                max_idx = i.c_idx
        return max_idx

    def must_be_equal(self,c_idx):
        for i in self.conf_list:
            if i.c_idx == c_idx:
                if i.diffrent == False:
                    return True
        return None

    def name_c_idx(self,c_idx):
         for i in self.conf_list:
            if i.c_idx == c_idx:
                return i.name
         return None

    def descr_c_idx(self,c_idx):
         for i in self.conf_list:
            if i.c_idx == c_idx:
                return i.descr
         return None


class Container:
    def __init__(self):
        #ogolna klasa dzialjaca bez konkretnych nazw
        self.cont_conf = DataConfiguration()
        self.main_list = list()
        self.main_list_to_write = list()
        self.group_list = list()
        self.diff_group = list()
        self.tmp_sort_key = None

        self.dialect_format2 = csv.excel_tab
        self.dialect_format2.quoting = csv.QUOTE_NONE
        self.dialect_format2.escapechar = '\\'

    def csv_read(self, filename, input_data_format='format_2',
            remove=False):
        """Read data from CSV file

        input_data_format:
            format_1 - ansii
            format_2 - utf-8
        """
        if input_data_format is 'format_1':
            #with open(filename, newline='', encoding='utf-8') as csvfile:
            with open(filename, mode='rb') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for row in reader:
                    #print('\t'.join(row))
                    self.main_list.append(row)

        elif input_data_format is 'format_2':
            with open(filename,'rb') as csvfile:
                reader = UnicodeReader(csvfile,dialect=self.dialect_format2)
                for row in reader:
                    #print('\t'.join(row))
                    self.main_list.append(row)
                
        else:
            print('Not recognised type of csv read')

        self.main_list_to_write = list(self.main_list)

        if remove:
            self.files_to_remove.append(filenam)

    def csv_write(self, filename, output_data_format='format_2',
            remove=False):
        """Read data from CSV file

        input_data_format:
            format_1 - ansii
            format_2 - utf-8
        """
        
        if len(self.diff_group)>0:
            shutil.copyfile(filename,filename+'_bac')

        if output_data_format is 'format_1':
            with open(filename, 'wb') as csvfile:
                #with open(filename, newline='', encoding='utf-8') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter='\t',
                                        quoting=csv.QUOTE_NONE)
                for i in self.main_list_to_write:
                    spamwriter.writerow(i)


        elif output_data_format is 'format_2':
            with open(filename, 'wb') as csvfile:
                spamwriter = UnicodeWriter(csvfile, 
                        dialect=self.dialect_format2)

                for i in self.main_list_to_write:
                   spamwriter.writerow(i)

            with open(filename, 'r') as infile, \
                open(filename+'_tmp', 'w') as outfile:
                    data = infile.read()
                    data = data.replace('\\', '')
                    outfile.write(data)
            shutil.move(filename+'_tmp',filename)



    def print_data(self):
        for i in self.main_list:
            print(i)

    def print_by_group(self):
        for i in self.group_list:
            print("\n\n")
            print(i)
            print('')

    def sort_tmp_key(self, elem):
        return elem[self.tmp_sort_key]

    def sort_by_key(self,elem):
        return elem[self.cont_conf.sort_key_idx]

    def sort_by(self):
        self.main_list.sort(key=self.sort_by_key)

    def group(self):
        if len(self.main_list)>1:
            for i in range(1, len(self.main_list)):
                if len(self.group_list):
                    if self.main_list[i-1][self.cont_conf.sort_key_idx] \
                        == self.main_list[i][self.cont_conf.sort_key_idx]:
                         self.group_list[-1].append(self.main_list[i])
                    else:
                        self.group_list.append([])
                        self.group_list[-1].append(self.main_list[i])

                else:
                    self.group_list.append([])
                    self.group_list[-1].append(self.main_list[0])

    def find_diff_group(self):
        for i in self.group_list:
            if len(i)>1:
                for idx in range(0,self.cont_conf.max_c_idx()):
                    if self.cont_conf.must_be_equal(idx):
                        self.tmp_sort_key = idx
                        i.sort(key=self.sort_tmp_key)
                        for grp_elem_idx in range(1,len(i)):
                            if i[grp_elem_idx-1][idx]\
                                    != i[grp_elem_idx][idx]:
                                #modif if you need
                                self.diff_group.append(
                                    [
                                    i[grp_elem_idx-1],
                                    i[grp_elem_idx],
                                    idx,
                                    self.cont_conf.name_c_idx(idx),
                                    self.cont_conf.descr_c_idx(idx)])

    def print_diff(self):
        if len(self.diff_group):
            print("\n\n\n\tDiffrences\n\n\n")
            for i in self.diff_group:
                print('\n\n')
                print(i)
                print('')
                print("KTM code: "+str(i[0][self.cont_conf.\
                    c_idx_of('ktm_code')]))

                print('Page ',i[0][1],' Idx ',i[0][0],'Schem idx',i[0][3],
                        'Part',i[0][9])
                print('Page ',i[1][1],' Idx ',i[1][0],'Schem idx',i[1][3],
                        'Part',i[1][9])


                print('Diffrence:')
                print(i[0][i[2]])
                print(i[1][i[2]])
        else:
            print("\n\tThere is no diffrences\n")

    def fix_all_differences(self):
        for i in range(0,len(self.diff_group)):
            self.choose_one_from_diff(diff_group_idx=i)

    def choose_one_from_diff(self,diff_group_idx,idx=None,diff_type=None,
            choose=None,user_name=None):
        i=self.diff_group[diff_group_idx]
        if idx is None:
            idx=i[2]
        if diff_type is None:
            diff_type=i[4]
        if choose is None:
            print('Choose t name of '+self.cont_conf.name_c_idx(idx)+
                    ' for '+i[0][self.cont_conf.sort_key_idx])
            print('1: '+i[0][idx])
            print('2: '+i[1][idx])
            print('3: Enter different name')
            print('\nMore data:')
            print(i)
            print('')
            print("KTM code: "+str(i[0][self.cont_conf.\
                c_idx_of('ktm_code')]))

            print('Page ',i[0][1],' Idx ',i[0][0],'Schem idx',i[0][3],
                    'Part',i[0][9])
            print('Page ',i[1][1],' Idx ',i[1][0],'Schem idx',i[1][3],
                    'Part',i[1][9])
            print('\n')

            choose = get_integer(text_to_display='Enter number to choose '+
                'option(Enter to skip): ',min_value=0,max_value=3,
                nothing_as_None=True)
        if choose == 1:
            self.make_data_uniform(
                    main_param_name=i[0][self.cont_conf.sort_key_idx],
                    idx=idx,name_to_change=i[0][idx])
            
            print('zmieniono na opcje 1')

        elif choose == 2:
            self.make_data_uniform(
                    main_param_name=i[0][self.cont_conf.sort_key_idx],
                    idx=idx,name_to_change=i[1][idx])
            
            print('zmieniono na opcje 2')

        elif choose == 3:
            
            print('zmieniono na opcje 3')

            if user_name:
                self.make_data_uniform(
                        main_param_name=i[0][self.cont_conf.sort_key_idx],
                        idx=idx,name_to_change=user_name)
            else:
                user_name =  raw_input('Enter your name:\n')
                user_name = user_name.decode(sys.stdin.encoding)
                self.make_data_uniform(
                        main_param_name=i[0][self.cont_conf.sort_key_idx],
                        idx=idx,name_to_change=user_name)
        elif choose == None:
            pass


    def make_data_uniform(self, main_param_name, idx, name_to_change):
        for i in self.main_list_to_write:
            if i[self.cont_conf.sort_key_idx] == main_param_name:
                i[idx] = name_to_change

    def is_on_list(self, elem, list, idx):
        try:
            for i in list:
                if i[idx] == elem:
                    return True
            return False
        except:
            return None

    def print_to_check(self, log_file_check=None, save_change=True):
        list_of_main_parameter = list()
        list_of_not_check = list()
        list_check_file = list()
        for i in self.group_list:
            list_of_main_parameter.append(i[0]\
                [self.cont_conf.sort_key_idx])

        if log_file_check == None:
            list_of_not_check = list_of_main_parameter
            for i in list_of_not_check:
                print(i)
        else:
            if os.path.exists(log_file_check):
                with open(log_file_check, 'rb') as csvfile:
                    reader = csv.reader(csvfile, delimiter='\t')
                    for row in reader:
                        list_check_file.append(row)
                for i in list_of_main_parameter:
                    if self.is_on_list(i,list_check_file,0):
                        pass
                    else:

                        list_check_file.append([i,'0'])
            else:
                for i in list_of_main_parameter:
                    list_check_file.append([i,'0'])
        with open(log_file_check, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\t',
                                    quoting=csv.QUOTE_NONE)
            for i in list_check_file:
                spamwriter.writerow(i)

        for i in list_check_file:
                if len(i)>1:
                    if i[1] == '0':
                        print(i[0])



UserInterface()
