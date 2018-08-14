#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv, codecs, cStringIO
import os
import sys
import argparse
import shutil
import Tkinter
import tkFileDialog
import ttk
import tkMessageBox
import copy

__author__ = 'Kornel Stefańczyk'
__version__ = '1.0.5'
__email__ = 'kornelstefanczyk@wp.pl'

#constant
TITLE = "Part list comparator"


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
    def __init__(self,check_only_name=None):
        self.cont = Container(check_only_name=check_only_name)
        self.default_dir = '~/Desktop'
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
            if self.cont.csv_read(filename=args.input_name[0]):

                self.cont.sort_by()
                self.cont.group()

                self.cont.find_diff_group()
                if args.save_changes:
                    self.cont.fix_all_differences()
                    self.cont.csv_write(filename=args.input_name[0],
                            fix_quotes=True)
                else:
                    self.cont.print_diff()

                if args.ktm_code_log:
                    self.cont.print_to_check(args.ktm_code_log[0])
                else:
                    if args.disp_code_to_check:
                        self.cont.print_to_check()
            else:
                print("Your file is empty or in wrong fomat")

        """
        if args.log_name:
            pass
            #self.f_mng.send_to_kindle_dir_path(name=args.stk_dir_name[0])
        """
        if len(sys.argv)==1:
            parser.print_help()
            root = Tkinter.Tk()
            my_gui = self.GUI(root)
            root.mainloop()


    def GUI(self, master):
        self.idx_of_data = 0
        self.choose = None
        self.box_insert = False
        self.stop_program_var= False
        self.master = master
        self.main_filename = tkFileDialog.askopenfilename(
                initialdir = self.default_dir,
                title = "Select file to check",
                filetypes = (("csv files","*.csv"),("all files","*.*")))
        if self.main_filename == '':
            self.remove_quotes_from_csv()
        if self.cont.csv_read(filename=self.main_filename):
            self.cont.sort_by()
            self.cont.group()

            self.cont.find_diff_group()

            self.master.title(TITLE+'\t\t\tfile:\t'+self.main_filename)
            print(self.main_filename)
            self.master.geometry('1250x500')

            self.set_window()
            self.show_differences()
        else:
            tkMessageBox.showerror('Wrong file',
"""
You file is empty or in wrong fomat

Next window will show you
correct csv file format
""")
            self.show_format_file()
            quit()

    def remove_quotes_from_csv(self):
            tkMessageBox.showerror('Wrong file',
"""
Not choose file to compare

In next window you will be
able to remove unnecessary
quotes char from selected file
""")
            remove_quotes_filename = tkFileDialog.askopenfilename(
                    initialdir = self.default_dir,
                    title = "Select file to remove quotes",
                    filetypes = (("csv files","*.csv"),("all files","*.*")))

            self.cont.csv_read(filename=remove_quotes_filename,
                    input_data_format='format_rewrite')

            self.cont.csv_write(filename=remove_quotes_filename,
                    output_data_format='format_rewrite_without_quotes')
            tkMessageBox.showerror('Removed quotes',
"""
Removed quotes from file
""")




    def set_window(self, ktm_code=None,type_of_diff=None):
        head_color = 'lavender'
        self.master.bind("<KeyRelease>", self.on_return_release)
        number_cols = 10
        number_rows = 3
        self.master.grid_columnconfigure((number_cols-1)-3,weight=1)
        self.master.config(background=head_color)

        # Define the different GUI widgets
        self.ktm_code_label = Tkinter.Label(self.master, text = "Ktm code:",
                background=head_color)
        self.ktm_code_label.grid(row = (number_rows-1)-2,
                column = (number_cols-1)-2, sticky = Tkinter.E)
        self.ktm_code_data = Tkinter.Label(self.master, text = ktm_code,
                background=head_color)
        self.ktm_code_data.grid(row = (number_rows-1)-2,
                column = (number_cols-1)-1, sticky = Tkinter.W)

        self.type_of_diff_label = Tkinter.Label(self.master,
            text = "Type of diff:",background=head_color)
        self.type_of_diff_label.grid(row = (number_rows-1),
                column = (number_cols-1)-2, sticky = Tkinter.E)
        self.type_of_diff_data = Tkinter.Label(self.master,
            text = type_of_diff,background=head_color)
        self.type_of_diff_data.grid(row = (number_rows-1),
                column = (number_cols-1)-1, sticky = Tkinter.W)


        self.modified_label = Tkinter.Label(self.master, text = "Your choose:",
                background=head_color)
        self.modified_entry = Tkinter.Entry(self.master, width=10)
        self.modified_label.grid(row = (number_rows-1)-1,
                column = (number_cols-1)-2, sticky = Tkinter.E)
        self.modified_entry.grid(row = (number_rows-1)-1,
                column = (number_cols-1)-1)
        self.submit_button = Tkinter.Button(self.master, text = "Go",
            command = self.insert_data)
        self.submit_button.grid(row = (number_rows-1)-1,
                column = (number_cols-1), sticky = Tkinter.W+Tkinter.E)
        self.skip_button = Tkinter.Button(self.master, text = "Skip",
            command = self.skip_data)
        self.skip_button.grid(row = (number_rows-1), column = (number_cols-1),
                sticky = Tkinter.W+Tkinter.E)
        self.back_button = Tkinter.Button(self.master, text = "Back",
            command = self.back_data)
        self.back_button.grid(row = (number_rows-1)-2, column = (number_cols-1),
                sticky = Tkinter.W)
        self.help_button = Tkinter.Button(self.master, text = "Help",
            command = self.show_help)
        self.help_button.grid(row = 0, column = 3, sticky = Tkinter.W)
        self.save_and_exit_button = Tkinter.Button(self.master,
                text = "Save and Exit", command = self.stop_program)
        self.save_and_exit_button.grid(row = 0, column = 0, sticky = Tkinter.W)
        self.save_button = Tkinter.Button(self.master,
                text = "Save", command = self.save_without_exit)
        self.save_button.grid(row = 1, column = 0, sticky = Tkinter.W+Tkinter.E)
        self.quote_replace_button = Tkinter.Button(self.master,
                text = "Remove unnecessary quotes", command = self.remove_quotes)
        self.quote_replace_button.grid(row = 0, column = 1, sticky = Tkinter.W)
        self.xpertis_csv_button = Tkinter.Button(self.master,
                text = "Xpertis csv",
                command = self.do_you_want_to_save_xpertis_file)
        self.xpertis_csv_button.grid(row = 0, column = 2,
                sticky = Tkinter.W+Tkinter.E)
        self.xpertis_csv_test_button = Tkinter.Button(self.master,
                text = "Xpertis TEST csv",
                command = self.do_you_want_to_save_xpertis_test_file)
        self.xpertis_csv_test_button.grid(row = 1, column = 2,
                sticky = Tkinter.W+Tkinter.E)
        self.csv_test_button = Tkinter.Button(self.master,
                text = "TEST csv",
                command = self.do_you_want_to_save_main_file_format_test)
        self.csv_test_button.grid(row = 2, column = 2,
                sticky = Tkinter.W+Tkinter.E)

        self.test_mode_var = Tkinter.StringVar(None, 'one')
        #self.test_mode_frame = Tkinter.Frame(self.master, width=100,height=100,
        #        background="Blue")
        #self.test_mode_frame.grid(row = 1, column=3)
        #self.test_mode_frame.pack()
        self.test_mode_radoibutton = Tkinter.Radiobutton(self.master,
                text='Only one code', variable=self.test_mode_var,
                value='one', background=head_color)
        self.test_mode_radoibutton.grid(row = 1, column = 3,
                sticky = Tkinter.W)
        self.test_mode_radoibutton = Tkinter.Radiobutton(self.master,
                text='All variants', variable=self.test_mode_var,
                value='all', background=head_color)
        self.test_mode_radoibutton.grid(row = 2, column = 3,
                sticky = Tkinter.W)
        #self.test_mode_radiobutton.set('one')





        # Set the treeview
        self.tree = ttk.Treeview(self.master, columns=('','','','','',''),
                height=40)
        self.tree.heading('#0', text='Choose idx')
        self.tree.heading('#1', text='Diffrence')
        self.tree.heading('#2', text=self.cont.cont_conf.conf_list[
            self.cont.cont_conf.c_idx_of("schem_idx")].descr)
        self.tree.heading('#3', text=self.cont.cont_conf.conf_list[
            self.cont.cont_conf.c_idx_of("idx")].descr)
        self.tree.heading('#4', text=self.cont.cont_conf.conf_list[
            self.cont.cont_conf.c_idx_of("page")].descr)
        self.tree.heading('#5', text=self.cont.cont_conf.conf_list[
            self.cont.cont_conf.c_idx_of("module_name")].descr)
        self.tree.heading('#6', text=self.cont.cont_conf.conf_list[
            self.cont.cont_conf.c_idx_of("machine_name")].descr)

        self.tree.column('#0', width=85, stretch=Tkinter.YES)
        self.tree.column('#1', width=500, stretch=Tkinter.YES)
        self.tree.column('#2', width=130, stretch=Tkinter.YES)
        self.tree.column('#3', width=55, stretch=Tkinter.YES)
        self.tree.column('#4', width=55, stretch=Tkinter.YES)
        self.tree.column('#5', width=200, stretch=Tkinter.YES)
        self.tree.column('#6', width=200, stretch=Tkinter.YES)
        self.tree.grid(row=7, columnspan=number_cols, sticky='nsew')
        self.treeview = self.tree

    def get_test_mode(self):
        self.cont.test_mode_var = self.test_mode_var.get()

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            self.ktm_code_data.config(text='')
            self.type_of_diff_data.config(text='')

    def stop_program(self):
        self.stop_program_var = True
        self.do_you_want_to_save_index_to_check()
        self.do_you_want_to_save_main_file()

    def save_without_exit(self):
        self.do_you_want_to_save_main_file(quit_after_save=False)

    def remove_quotes(self):
        self.cont.remove_unnecessary_quot_marks()
        self.cont.find_diff_group()
        self.insert_data()

    def show_differences(self):
        if len(self.cont.diff_group) > self.idx_of_data:
            diff_item = self.cont.diff_group[self.idx_of_data]
            self.cont.print_diff_one_code(self.idx_of_data)
            """
            print('\n\n')
            print(diff_item)
            print('\n\n')
            print(self.cont.cont_conf.c_idx_of("ktm_code")
            print('\n\n')
            print(diff_item[0][1])
            print('\n\n')
            """
            self.ktm_code_data.config(text=
                    diff_item[0][0][self.cont.cont_conf.c_idx_of("ktm_code")])
            self.type_of_diff_data.config(text=diff_item[3])
            for i in range(0,len(diff_item[0])):
                self.treeview.insert('', 'end', text=str(i+1), values=(
                   diff_item[0][i][diff_item[1]],
                    diff_item[0][i][self.cont.cont_conf.c_idx_of("schem_idx")],
                    diff_item[0][i][self.cont.cont_conf.c_idx_of("idx")],
                    diff_item[0][i][self.cont.cont_conf.c_idx_of("page")],
                    diff_item[0][i]\
                            [self.cont.cont_conf.c_idx_of("module_name")],
                    diff_item[0][i]\
                            [self.cont.cont_conf.c_idx_of("machine_name")]))

    def on_return_release(self, event):
        #print(event.keysym)
        if not self.stop_program_var:
            if event.keysym=='Return' or event.keysym=='KP_Enter':
                if self.box_insert:
                    self.box_insert_data()
                else:
                    self.insert_data()

            elif  event.keysym=='Escape':
                if self.box_insert:
                    self.box_insert_window.destroy()
                    self.box_insert = False
                else:
                    self.skip_data()


    def skip_data(self):
        self.idx_of_data += 1
        self.insert_data()

    def back_data(self):
        if self.idx_of_data > 0:
            self.idx_of_data -= 1
        self.insert_data()


    def insert_data(self):
        self.clear_tree()

        #self.cont.print_diff()

        if self.idx_of_data < len(self.cont.diff_group):
            print(self.idx_of_data)

            self.choose = self.modified_entry.get()
            self.modified_entry.delete(0, 'end')
            try:
                self.choose = int(self.choose)
            except:
                self.choose = -1

            if self.choose>0:
                self.cont.print_diff_one_code(self.idx_of_data)

                self.cont.choose_one_from_diff(diff_group_idx=self.idx_of_data,
                        choose=self.choose,update_diff=True)

            elif self.choose == 0:
                self.box_insert_data_window()

            self.show_differences()

        else:
            print('fixed whole file')
            self.stop_program()


    def box_insert_data_window(self):
        self.box_insert = True
        self.box_insert_window = Tkinter.Tk()
        self.box_insert_window.bind("<KeyRelease>", self.on_return_release)
        self.box_insert_window.title('Choose name for code')
        self.modified_insert_entry = Tkinter.Entry(self.box_insert_window,
                width=60)
        self.modified_insert_label = Tkinter.Label(self.box_insert_window,
                text = "Your choose:")
        self.modified_insert_label.grid(row = 0, column = 0, sticky = Tkinter.E)
        self.modified_insert_entry.grid(row = 1, column = 0)
        self.submit_insert_button = Tkinter.Button(self.box_insert_window,
                text = "Insert", command = self.box_insert_data)
        self.submit_insert_button.grid(row = 1, column = 1, sticky = Tkinter.W)

    def box_insert_data(self):
        self.choose = -1
        user_data = self.modified_insert_entry.get()
        user_data = user_data.encode(sys.stdin.encoding)

        self.cont.choose_one_from_diff(diff_group_idx=self.idx_of_data,
                choose=0,user_name=user_data,update_diff=True)
        self.modified_insert_entry.delete(0, 'end')

        self.show_differences()
        self.box_insert_window.destroy()
        self.choose = 0
        self.insert_data()
        self.box_insert = False


    def do_you_want_to_save_main_file(self, quit_after_save=True):
        if tkMessageBox.askyesno('Main CSV file',
"""
Do you want to save your changes
in oryginal csv file?
"""):
            if tkMessageBox.askyesno('Save changes?', "Are you sure?"):
                self.cont.csv_write(filename=self.main_filename)
                if quit_after_save:
                    quit()

        else:
            if tkMessageBox.askyesno('Do not save changes?', "Are you sure?"):
                self.cont.print_by_group()
                if quit_after_save:
                    quit()
            else:
                pass

    def do_you_want_to_save_main_file_format_test(self):
        try:
            if tkMessageBox.askyesno('Main CSV TEST file',
"""
Do you want to save TEST file
in oryginal file format?
"""):
                filename = tkFileDialog.asksaveasfilename(
                        initialdir = "~/Desktop",
                        title = "Select file to save TEST csv file",
                        filetypes = (("csv files","*.csv"),
                            ("all files","*.*")))
                print(filename)
                self.get_test_mode()
                self.cont.csv_write(filename=filename,
                        output_data_format='format_2_test')
            else:
                pass
        except:
            pass


    def do_you_want_to_save_index_to_check(self):
        try:
            if tkMessageBox.askyesno('Index CSV file',
"""
Do you want to save file
with codes to check?
"""):
                filename = tkFileDialog.asksaveasfilename(
                        initialdir = "~/Desktop",
                        title = "Select file to save index to check",
                        filetypes = (("csv files","*.csv"),
                            ("all files","*.*")))
                print(filename)
                self.cont.print_to_check(filename)
            else:
                pass
        except:
            pass

    def do_you_want_to_save_xpertis_file(self):
        try:
            if tkMessageBox.askyesno('Xpertis file',
"""
Do you want to save your data
in Xpertis csv format file?
"""):
                filename = tkFileDialog.asksaveasfilename(
                        initialdir = "~/Desktop",
                        title = "Select file to save Xpertis csv file",
                        filetypes = (("csv files","*.csv"),
                            ("all files","*.*")))
                print(filename)
                self.cont.csv_write(filename=filename,
                        output_data_format='xpertis_csv')
            else:
                pass
        except:
            pass


    def do_you_want_to_save_xpertis_test_file(self):
        try:
            if tkMessageBox.askyesno('Xpertis TEST file',
"""
Do you want to save your data
in Xpertis csv format file?
File is only for testing compatibility
of this data and Xpertis database.
"""):
                filename = tkFileDialog.asksaveasfilename(
                        initialdir = "~/Desktop",
                        title = "Select file to save Xpertis TEST csv file",
                        filetypes = (("csv files","*.csv"),
                            ("all files","*.*")))
                print(filename)
                self.get_test_mode()
                self.cont.csv_write(filename=filename,
                        output_data_format='xpertis_csv_test')
            else:
                pass
        except:
            pass



    def show_help(self):
        text_info ="""
Program was writed by
""" + __author__ + """ in 1.08.2018
email: """ + __email__+"""

Do you want to see .
csv file format?"""
        if tkMessageBox.askyesno('Help, ver. '+__version__, text_info,
                parent=self.master):
            self.show_format_file()
        else:
            pass

    def show_format_file(self):
        text_format = """
Your  delimiter should be  ; and
your rows should consist

"""
        name_list = list()
        char_list = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N',
                'O','P','Q','R','S','T','U','V','W','X','Y','Z']
        for i in self.cont.cont_conf.conf_list:
            name_list.append(i.descr)
        text_format = text_format + ";".join(name_list) +\
            '\nYour last column should be \'' + char_list[len(name_list)-1] +'\''
        tkMessageBox.showinfo('File format', text_format,parent=self.master)


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
    def __init__(self, check_only_name=None):
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
            c_idx=10, descr="Maszyna"))
        self.conf_list.append(DataIndex(name="module_code", f_col=11,
            c_idx=11, descr="Numer modułu"))
        self.conf_list.append(DataIndex(name="module_idx", f_col=12,
            c_idx=12, descr="Kod modułu"))
        self.conf_list.append(DataIndex(name="el_mech", f_col=13,
            c_idx=13, descr="El/Mech"))




        if check_only_name:
            self.check_only(check_only_name)

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

    def min_required_c_idx(self):
        idx = 0
        for i in self.conf_list:
            if i.c_idx > idx and i.diffrent == False:
                idx = i.c_idx
        return idx

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

    def check_only(self, name):
        for i in self.conf_list:
            if i.name == name:
                i.diffrent = False
            else:
                i.diffrent = True


class Container:
    def __init__(self,check_only_name=None):
        self.cont_conf = DataConfiguration(check_only_name=check_only_name)
        self.main_list = list()
        self.main_list_to_write = list()
        self.group_list = list()
        self.diff_group = list()
        self.tmp_sort_key = None

    def set_format(self, remove_quotes_mode=False):
        self.dialect_format = copy.deepcopy(csv.excel_tab)
        if remove_quotes_mode:
            self.dialect_format.quoting = csv.QUOTE_NONE
            self.dialect_format.escapechar = '\\'
            self.dialect_format.delimiter = ';'

        else:
            self.dialect_format.quoting = csv.QUOTE_MINIMAL
            self.dialect_format.delimiter = ';'


    def remove_backslash_from_file(self, filename):
        with open(filename, 'r') as infile, \
            open(filename+'_tmp', 'w') as outfile:
                data = infile.read()
                data = data.replace('\\', '')
                outfile.write(data)
        shutil.move(filename+'_tmp',filename)


    def csv_read(self, filename, input_data_format='format_2',
            remove_quotes=False):
        """Read data from CSV file

        input_data_format:
            format_1 - ansii
            format_2 - utf-8
        """
        if input_data_format == 'format_1':
            with open(filename, mode='rb') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for row in reader:
                    self.main_list.append(row)

        elif input_data_format == 'format_2':
            self.set_format()
            with open(filename,'rb') as csvfile:
                reader = UnicodeReader(csvfile,dialect=self.dialect_format)
                for row in reader:
                    self.main_list.append(row)
        elif input_data_format == 'format_rewrite':
            self.set_format()
            with open(filename,'rb') as csvfile:
                self.rewrite_list = list()
                reader = UnicodeReader(csvfile,dialect=self.dialect_format)
                for row in reader:
                    self.rewrite_list.append(row)


        else:
            print('Not recognised type of csv read')

        self.main_list_to_write = list(self.main_list)

        if len(self.main_list):
            if len(self.main_list[0]) > self.cont_conf.max_c_idx():
                return True
        return False

    def csv_write(self, filename, output_data_format='format_2',
            list_to_write=None, test_mode=None):
        """Read data from CSV file

        input_data_format:
            format_1 - ansii
            format_2 - utf-8
            xpertis_csv
            xpertis_csv_test
        """
        if len(self.diff_group)>0:
            if os.path.isfile(filename):
                shutil.copyfile(filename,filename+'_bac')


        if output_data_format == 'format_1':
            with open(filename, 'wb') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter='\t',
                                        quoting=csv.QUOTE_NONE)
                for i in self.main_list_to_write:
                    spamwriter.writerow(i)
            print 'csv wrote'


        elif output_data_format == 'format_2':
            self.set_format()
            with open(filename, 'wb') as csvfile:
                spamwriter = UnicodeWriter(csvfile,
                        dialect=self.dialect_format)

                for i in self.main_list_to_write:
                   spamwriter.writerow(i)
            print 'csv wrote'

        elif output_data_format == 'format_2_test':
            self.set_format()
            if test_mode is None:
                test_mode = self.test_mode_var
            if test_mode == 'one':
                with open(filename, 'wb') as csvfile:
                    spamwriter = UnicodeWriter(csvfile,
                            dialect=self.dialect_format)
                    for i in self.group_list:
                        i = i[0]
                        spamwriter.writerow(i)
            elif test_mode == 'all':
                with open(filename, 'wb') as csvfile:
                    spamwriter = UnicodeWriter(csvfile,
                            dialect=self.dialect_format)
                    for i in self.group_list:
                        i = i[0]
                        if self.is_code_uniform(i[\
                                self.cont_conf.c_idx_of('ktm_code')]):
                            spamwriter.writerow(i)
                        else:
                            for j in self.return_list_of_diff(i[\
                                self.cont_conf.c_idx_of('ktm_code')]):
                                spamwriter.writerow(j)
            print 'csv wrote'


        elif output_data_format == 'format_rewrite_without_quotes':
            self.remove_unnecessary_quot_marks(plain_text=True)
            self.set_format(remove_quotes_mode=True)
            with open(filename, 'wb') as csvfile:
                spamwriter = UnicodeWriter(csvfile,
                        dialect=self.dialect_format)

                for i in self.rewrite_list:
                    spamwriter.writerow(i)
            self.remove_backslash_from_file(filename)
            print 'csv wrote'

        elif output_data_format == 'xpertis_csv':
            self.remove_unnecessary_quot_marks(plain_text=True)
            self.set_format(remove_quotes_mode=True)
            with open(filename, 'wb') as csvfile:
                spamwriter = UnicodeWriter(csvfile,
                        dialect=self.dialect_format)
                spamwriter.writerow([
                    'Modul','Zespol', 'Zespol2', 'Zespol3', 'Zespol4',
                    'Nr','Nr czesci','Sztuk','Nazwa','Kod znormalizowany',
                    'Opis','El/Mech','Do napraw','Do eksploat'
                    ])
                for i in self.main_list_to_write:
                    spamwriter.writerow([
                       i[self.cont_conf.c_idx_of('module_idx')],
                       i[self.cont_conf.c_idx_of('module_code')],
                       '','','',
                       i[self.cont_conf.c_idx_of('schem_idx')],
                       i[self.cont_conf.c_idx_of('ktm_code')],
                       i[self.cont_conf.c_idx_of('qnt')],
                       i[self.cont_conf.c_idx_of('descript')],
                       i[self.cont_conf.c_idx_of('manuf_code')],
                       '',
                       i[self.cont_conf.c_idx_of('el_mech')],
                       '','','','',
                       i[self.cont_conf.c_idx_of('page')],
                       i[self.cont_conf.c_idx_of('idx')],
                       i[self.cont_conf.c_idx_of('module_name')],
                       i[self.cont_conf.c_idx_of('machine_name')]
                       ])

            self.remove_backslash_from_file(filename)
            print 'csv wrote'

        elif output_data_format == 'xpertis_csv_test':
            if test_mode is None:
                test_mode = self.test_mode_var
            if test_mode == 'one':
                self.remove_unnecessary_quot_marks(plain_text=True)
                self.set_format(remove_quotes_mode=True)
                with open(filename, 'wb') as csvfile:
                    spamwriter = UnicodeWriter(csvfile,
                            dialect=self.dialect_format)
                    spamwriter.writerow([
                        'Modul','Zespol', 'Zespol2', 'Zespol3', 'Zespol4',
                        'Nr','Nr czesci','Sztuk','Nazwa','Kod znormalizowany',
                        'Opis','El/Mech','Do napraw','Do eksploat'
                        ])
                    for i in self.group_list:
                        i = i[0]
                        spamwriter.writerow([
                        '','','','','',
                        i[self.cont_conf.c_idx_of('schem_idx')],
                        i[self.cont_conf.c_idx_of('ktm_code')],
                        i[self.cont_conf.c_idx_of('qnt')],
                        i[self.cont_conf.c_idx_of('descript')],
                        i[self.cont_conf.c_idx_of('manuf_code')],
                        '','','','','','',
                        i[self.cont_conf.c_idx_of('page')],
                        i[self.cont_conf.c_idx_of('idx')],
                        i[self.cont_conf.c_idx_of('module_name')],
                        i[self.cont_conf.c_idx_of('machine_name')]
                        ])

                self.remove_backslash_from_file(filename)
            elif test_mode == 'all':
                with open(filename, 'wb') as csvfile:
                    spamwriter = UnicodeWriter(csvfile,
                            dialect=self.dialect_format)
                    for i in self.group_list:
                        i = i[0]
                        if self.is_code_uniform(i[\
                                self.cont_conf.c_idx_of('ktm_code')]):
                            spamwriter.writerow(i)
                        else:
                            for j in self.return_list_of_diff(i[\
                                self.cont_conf.c_idx_of('ktm_code')]):
                                spamwriter.writerow(j)
                pass
                self.remove_unnecessary_quot_marks(plain_text=True)
                self.set_format(remove_quotes_mode=True)
                with open(filename, 'wb') as csvfile:
                    spamwriter = UnicodeWriter(csvfile,
                            dialect=self.dialect_format)
                    spamwriter.writerow([
                        'Modul','Zespol', 'Zespol2', 'Zespol3', 'Zespol4',
                        'Nr','Nr czesci','Sztuk','Nazwa','Kod znormalizowany',
                        'Opis','El/Mech','Do napraw','Do eksploat'
                        ])
                    for i in self.group_list:
                        i = i[0]
                        if self.is_code_uniform(i[\
                                self.cont_conf.c_idx_of('ktm_code')]):
                            spamwriter.writerow([
                            '','','','','',
                            i[self.cont_conf.c_idx_of('schem_idx')],
                            i[self.cont_conf.c_idx_of('ktm_code')],
                            i[self.cont_conf.c_idx_of('qnt')],
                            i[self.cont_conf.c_idx_of('descript')],
                            i[self.cont_conf.c_idx_of('manuf_code')],
                            '','','','','','',
                            i[self.cont_conf.c_idx_of('page')],
                            i[self.cont_conf.c_idx_of('idx')],
                            i[self.cont_conf.c_idx_of('module_name')],
                            i[self.cont_conf.c_idx_of('machine_name')]
                            ])
                        else:
                            for j in self.return_list_of_diff(i[\
                                self.cont_conf.c_idx_of('ktm_code')]):

                                spamwriter.writerow([
                                '','','','','',
                                j[self.cont_conf.c_idx_of('schem_idx')],
                                j[self.cont_conf.c_idx_of('ktm_code')],
                                j[self.cont_conf.c_idx_of('qnt')],
                                j[self.cont_conf.c_idx_of('descript')],
                                j[self.cont_conf.c_idx_of('manuf_code')],
                                '','','','','','',
                                j[self.cont_conf.c_idx_of('page')],
                                j[self.cont_conf.c_idx_of('idx')],
                                j[self.cont_conf.c_idx_of('module_name')],
                                j[self.cont_conf.c_idx_of('machine_name')]
                                ])

                self.remove_backslash_from_file(filename)
            print 'csv wrote'

        else:
            print('Not recognised type of csv file')


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
        self.group_list = list()
        if len(self.main_list)>1:
            self.group_list.append([])
            self.group_list[-1].append(self.main_list[0])
            for i in range(1, len(self.main_list)):
                if self.main_list[i-1][self.cont_conf.sort_key_idx] \
                    == self.main_list[i][self.cont_conf.sort_key_idx]:
                        self.group_list[-1].append(self.main_list[i])
                else:
                    self.group_list.append([])
                    self.group_list[-1].append(self.main_list[i])



    def find_diff_group(self):
        self.diff_group = list()
        self.group()
        for i in self.group_list:
            if len(i)>1:
                for idx in range(0,self.cont_conf.max_c_idx()):
                    if self.cont_conf.must_be_equal(idx):
                        tmp_diff_list = [ [],
                            idx,
                            self.cont_conf.name_c_idx(idx),
                            self.cont_conf.descr_c_idx(idx)]
                        self.tmp_sort_key = idx
                        i.sort(key=self.sort_tmp_key)
                        for grp_elem_idx in range(0,len(i)):
                            if self.is_on_list(i[grp_elem_idx][idx],
                                    tmp_diff_list[0],idx) is False:
                                tmp_diff_list[0].append(i[grp_elem_idx])

                        if len(tmp_diff_list[0])>1:
                            self.diff_group.append(tmp_diff_list)

                        """
                        if i[grp_elem_idx-1][idx]\
                                != i[grp_elem_idx][idx]:
                            #modif if you need
                            self.diff_group.append(
                                [
                                [i[grp_elem_idx-1],
                                i[grp_elem_idx]],
                                idx,
                                self.cont_conf.name_c_idx(idx),
                                self.cont_conf.descr_c_idx(idx)])
                        """

    def is_code_uniform(self, code):
        for i in self.diff_group:
            i = i[0]
            if code == i[0][self.cont_conf.c_idx_of('ktm_code')]:
                return False
        return True

    def return_list_of_diff(self, code):
        for i in self.diff_group:
            i = i[0]
            if code == i[0][self.cont_conf.c_idx_of('ktm_code')]:
                return i
        return None




    def print_diff(self):
        if len(self.diff_group):
            print("\n\n\n\tDiffrences\n\n\n")
            for i in range(len(self.diff_group)):
                self.print_diff_one_code(idx=i)
        else:
            print("\n\tThere is no diffrences\n")


    def print_diff_one_code(self,idx):
        i = self.diff_group[idx]
        print('\n\n')
        print('Idx of differences: %s of %s' %(idx,len(self.diff_group)))
        print(i)
        print('')
        print("KTM code: "+str(i[0][0][self.cont_conf.\
            c_idx_of('ktm_code')]))

        for j in i[0]:
            print('Page ',j[1],' Idx ',j[0],
                    'Schem idx',j[3], 'Part',j[9])

        print('Diffrence:')
        for j in i[0]:
            print(j[i[1]])

        self.print_xpertis_name(idx)

    def print_xpertis_name(self, idx):
        i = self.diff_group[idx]
        for j in i[0]:
            if j[self.cont_conf.c_idx_of('idx')] == 'Xpertis':
                print '\nXpertis'
                print(j[i[1]])
                break



    def fix_all_differences(self):
        if len(self.diff_group):
            self.choose_one_from_diff(diff_group_idx=i)
            self.fix_all_differences()


    def choose_one_from_diff(self,diff_group_idx,idx=None,diff_type=None,
            choose=None,user_name=None,update_diff=False):
        i=self.diff_group[diff_group_idx]
        if idx is None:
            idx=i[1]
        if diff_type is None:
            diff_type=i[3]
        if choose is None:
            print('\n\nMore data for: '+
                    str(i[0][0][self.cont_conf.sort_key_idx]))
            self.print_diff_one_code(diff_group_idx)


            print('\nChoose t name of '+self.cont_conf.name_c_idx(idx)+
                    ' for '+i[0][0][self.cont_conf.sort_key_idx])
            print('\n0: Enter different name\n')

            for i_idx in range(0,len(i[0])):
                print(str(i_idx+1)+': '+i[0][i_idx][idx].encode('utf-8'))

            choose = get_integer(text_to_display='Enter number to choose '+
                'option(Enter to skip): ',min_value=0,max_value=len(i[0]),
                nothing_as_None=True)
        if choose == 0:
            if user_name:
                self.make_data_uniform(
                        main_param_name=i[0][0][self.cont_conf.sort_key_idx],
                        idx=idx,name_to_change=user_name)
            else:
                user_name =  raw_input('Enter your name:\n')
                user_name = user_name.decode(sys.stdin.encoding)
                self.make_data_uniform(
                        main_param_name=i[0][0][self.cont_conf.sort_key_idx],
                        idx=idx,name_to_change=user_name)
        elif choose>0 and choose<=len(i[0]):
            self.make_data_uniform(
                    main_param_name=i[0][0][self.cont_conf.sort_key_idx],
                    idx=idx,name_to_change=i[0][choose-1][idx])
        elif choose == None:
            pass

        if update_diff:
            self.find_diff_group()


    def make_data_uniform(self, main_param_name, idx, name_to_change):
        for i in self.main_list_to_write:
            if i[self.cont_conf.sort_key_idx] == main_param_name:
                i[idx] = name_to_change

    def is_on_list(self, elem, list_to_check, idx):
        try:
            for i in list_to_check:
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

    def remove_unnecessary_quot_marks(self, plain_text=False,
            debug_mode=False):
        for elem in range(0,len(self.main_list_to_write)):
            for field in range(0,len(self.main_list_to_write[elem])):
                old = self.main_list_to_write[elem][field]
                if plain_text:
                    if True:
                        """
                        if self.main_list_to_write[elem][field].startswith('"'):
                            self.main_list_to_write[elem][field] = \
                                    self.main_list_to_write[elem][field][1:]
                        if self.main_list_to_write[elem][field].endswith('"'):
                            self.main_list_to_write[elem][field] = \
                                    self.main_list_to_write[elem][field][:-1]
                        """
                        for i in range(0,2):
                            self.main_list_to_write[elem][field] = \
                                    self.main_list_to_write[elem][field].\
                                    replace('""','"')
                self.main_list_to_write[elem][field] = \
                        self.main_list_to_write[elem][field].\
                        replace(u'\u2018','\'')
                self.main_list_to_write[elem][field] = \
                        self.main_list_to_write[elem][field].\
                        replace(u'\u2019','\'')
                self.main_list_to_write[elem][field] = \
                        self.main_list_to_write[elem][field].\
                        replace(u'\u201a','\'')
                self.main_list_to_write[elem][field] = \
                        self.main_list_to_write[elem][field].\
                        replace(u'\u201b','\'')
                self.main_list_to_write[elem][field] = \
                        self.main_list_to_write[elem][field].\
                        replace(u'\u201c','"')
                self.main_list_to_write[elem][field] = \
                        self.main_list_to_write[elem][field].\
                        replace(u'\u201d','"')
                self.main_list_to_write[elem][field] = \
                        self.main_list_to_write[elem][field].\
                        replace(u'\u201e','"')
                self.main_list_to_write[elem][field] = \
                        self.main_list_to_write[elem][field].\
                        replace(u'\u201f','"')
                if debug_mode and old != self.main_list_to_write[elem][field]:
                    print(old)
                    print(self.main_list_to_write[elem][field])
                    print('')
        print('fixed double quote marks')


#UserInterface(check_only_name='ktm_code')
UserInterface()
