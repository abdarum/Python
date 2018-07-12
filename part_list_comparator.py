#python2.7
#-*- coding: utf-8 -*-

import csv



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
        print(self.f_col)
        print(self.c_idx)
        print(self.descr)
       
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



        

class Container:
    def __init__(self):
        #ogolna klasa dzialjaca bez konkretnych nazw
        cont_conf = DataConfiguration() 
        main_list = list()

    def read_file(self, input_file=None): 
        pass

    def csv_read(self, filename, input_data_format='format_1', 
            remove=False):
        """Read data from CSV file

        input_data_format:
            format_1      
            format_2
        """
        if input_data_format is 'format_1':
            with open(filename, newline='', encoding='utf-16') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for row in reader:
                    if str(row[0]) != 'id':
                        self.bom_element_list.append(BOMData(
                                                id = row[0],
                                                quantity = row[2],
                                                manufacturer_code = row[5],
                                                part_name = row[1],
                                                package = row[3],
                                                circut_index = row[4],
                                                lcsc_index = row[6],
                                                supplier = row[7],
                                                manufacturer = row[8]))

        if input_data_format is 'format_2':
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

        if remove:
            self.files_to_remove.append(filename)


tmp = DataConfiguration()
