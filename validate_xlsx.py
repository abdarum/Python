import os
#  pip install openpyxl
import pandas as pd
# pip install tk
import tkinter as tk
from tkinter import filedialog

path_to_file = None

root = tk.Tk()
root.withdraw()

path_to_file = filedialog.askopenfilename()


directory_path = r'C:\Users\Kornel\Desktop\tmp\Sylwia'
spreadsheet_filename = 'test.xlsx'

if path_to_file == None:
    path_to_file = os.path.join(directory_path, spreadsheet_filename)

print("Open spreedsheet: {}".format(path_to_file))
df = pd.read_excel(path_to_file, engine='openpyxl')

print(df)

number_of_rows = len(df)
number_of_columns = len(df.columns)

# The way to process each cell of the file
for col in range(number_of_columns):
    for row in range(number_of_rows):

        # Validate and manipulate values
        val = df.iat[row, col]
        print(val)
        