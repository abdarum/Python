#python2.7
#-*- coding: utf-8 -*-

class DataIndex:
    def __init__(self, f_col=None, c_idx=None,
            descr=None):
        self.f_col = f_col #column in file
        if c_idx==None and f_col!=None:
            self.c_idx = f_col
        else:
            self.c_idx = c_idx
        self.descr = descr

    def print_data(self):
        print(self.f_col)
        print(self.c_idx)
        print(self.descr)
       
class DataConfiguration:
    def __init__(self):
        self.idx = DataIndex(f_col=0,
            c_idx=0, descr="L,P,")
        self.page = DataIndex(f_col=1,
            c_idx=1, descr="Str,")
        self.qnt = DataIndex(f_col=2,
            c_idx=2, descr="Ilość")
        self.schem_idx = DataIndex(f_col=3,
            c_idx=3, descr="Nr na schemacie")
        self.manuf_numb = DataIndex(f_col=4,
            c_idx=4, descr="Kod producenta")
        self.ktm_numb = DataIndex(f_col=5,
            c_idx=5, descr="Kod KTM")
        self.type = DataIndex(f_col=6,
            c_idx=6, descr="Typ")
        self.manuf_name = DataIndex(f_col=7,
            c_idx=7, descr="Firma")
        self.descript = DataIndex(f_col=8,
            c_idx=8, descr="Opis")
        self.module_name = DataIndex(f_col=9,
            c_idx=9, descr="Funkcja")
        self.machine_name = DataIndex(f_col=10,
            c_idx=10)

        self.idx.print_data()
        self.page.print_data()
        self.qnt.print_data()
 
        #okreslenie ktora kolumna za co odpowiada


class Container:
    def __init__(self):
        #ogolna klasa dzialjaca bez konkretnych nazw
        pass


tmp = DataConfiguration()
