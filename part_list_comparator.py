#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import sys
import argparse



class UserInterface:
    def __init__(self):
        self.cont = Container()
        parser = argparse.ArgumentParser(description='Find diffrences in '+
                'part list')

        parser.add_argument('-i', '--input-name', action='store', nargs=1,
                help='path to file to check')
        parser.add_argument('-o', '--log-name', action='store', nargs=1,
                help='path to log file')


        args = parser.parse_args()

        if args.input_name:
            print(args.input_name[0])
            self.cont.csv_read(filename=args.input_name[0])
            #read this csv

        if args.log_name:
            pass
            #self.f_mng.send_to_kindle_dir_path(name=args.stk_dir_name[0])

        self.cont.print_data()

        print('\n\n\n\n')
        self.cont.sort_by()
        self.cont.print_data()





class DataIndex:
    def __init__(self, name, f_col=None,
            c_idx=None, descr=None):
        self.name = name
        self.f_col = f_col #column in file
        if c_idx==None and f_col!=None:
            self.c_idx = f_col #idx in container
        else:
            self.c_idx = c_idx
        self.descr = descr

    def print_data(self):
        print('Name: ',self.name)
        print('Col in file: ',self.f_col)
        print('Index in container: ',self.c_idx)
        print('Description: ',self.descr)



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
            c_idx=4, descr="Kod producenta"))
        self.conf_list.append(DataIndex(name="ktm_code",
            f_col=5, c_idx=5, descr="Kod KTM"))
        self.conf_list.append(DataIndex(name="type",
            f_col=6, c_idx=6, descr="Typ"))
        self.conf_list.append(DataIndex(name="manuf_name",
            f_col=7, c_idx=7, descr="Firma"))
        self.conf_list.append(DataIndex(name="descript",
            f_col=8, c_idx=8, descr="Opis"))
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





class Container:
    def __init__(self):
        #ogolna klasa dzialjaca bez konkretnych nazw
        self.cont_conf = DataConfiguration()
        self.main_list = list()

    def read_file(self, input_file=None):
        pass

    def csv_read(self, filename, input_data_format='format_1',
            remove=False):
        """Read data from CSV file

        input_data_format:
            format_1
            format_2
        """

        print(filename)


        if input_data_format is 'format_1':
            #with open(filename, newline='', encoding='utf-8') as csvfile:
            with open(filename, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for row in reader:
                    #print('\t'.join(row))
                    self.main_list.append(row)




        elif input_data_format is 'format_2':
            with open(filename, newline='', encoding='utf-16') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for row in reader:
                    if str(row[0]) != 'id':
                        self.bom_element_list.append(BOMData(
                                                id = row[0],
                                                quantity = row[4],
                                                manufacturer_code = row[5],
                                                part_name = row[1],
                                                package = row[3],
                                                circut_index = row[2],
                                                lcsc_index = row[8],
                                                supplier = row[7],
                                                manufacturer = row[6]))
        else:
            print('Not recognised type of csv read')

        if remove:
            self.files_to_remove.append(filename)

    def print_data(self):
        for i in self.main_list:
            print(i)

    def sort_by_key(self,elem):
        return elem[self.cont_conf.sort_key_idx]

    def sort_by(self):
        self.main_list.sort(key=self.sort_by_key)


UserInterface()
