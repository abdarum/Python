#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import os
import sys
import argparse


class UserInterface:
    def __init__(self):
        self.cont = Container()
        parser = argparse.ArgumentParser(description='Find diffrences '+
                 'in part list')

        parser.add_argument('-i', '--input-name', action='store', nargs=1,
                help='path to file to check')
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
        self.group_list = list()
        self.diff_group = list()
        self.tmp_sort_key = None

    def csv_read(self, filename, input_data_format='format_1',
            remove=False):
        """Read data from CSV file

        input_data_format:
            format_1
            format_2
        """
        if input_data_format is 'format_1':
            #with open(filename, newline='', encoding='utf-8') as csvfile:
            with open(filename, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for row in reader:
                    #print('\t'.join(row))
                    self.main_list.append(row)


        elif input_data_format is 'format_2':
            pass
        else:
            print('Not recognised type of csv read')

        if remove:
            self.files_to_remove.append(filename)

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
        for i in self.diff_group:
            print('\n\n')
            print(i)
            print('')
            print("KTM code: "+str(i[0][self.cont_conf.\
                c_idx_of('ktm_code')]))

            print('Page ',i[0][1],' Idx ',i[0][0],'Schem idx',i[0][3],'Part',i[0][9])
            print('Page ',i[1][1],' Idx ',i[1][0],'Schem idx',i[1][3],'Part',i[1][9])


            print('Diffrence:')
            print(i[0][i[2]])
            print(i[1][i[2]])

    def print_to_check(self, log_file_check=None):
        list_of_main_parameter = list()
        list_of_not_check = list()
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
                        if len(row)>1:
                            if row[1] == '0':
                                list_of_not_check.append(row[0])
                for i in list_of_not_check:
                    print(i)
            else:
                for i in list_of_main_parameter:
                    print(i)
                with open(log_file_check, 'wb') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter='\t',
                                            quoting=csv.QUOTE_NONE)
                    for i in list_of_main_parameter:
                        spamwriter.writerow([i,0])




UserInterface()
