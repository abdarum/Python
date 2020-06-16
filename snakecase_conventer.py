import os
import traceback
import sys
try:
    import stringcase
except:
    os.system('pip install stringcase')

try:
    from Tkinter import Tk
except ImportError:
    from tkinter import Tk


in_tmp = "xxx"
in_tmp = "xxx"
in_tmp = "xxx"
in_tmp = "xxx"
in_tmp = "xxx"
in_tmp = "xxx"
in_tmp = "sign_up_procedure"



# https://pypi.org/project/stringcase/
copy_to_clipboard = False

if copy_to_clipboard:
  r = Tk()
  r.withdraw()
  r.clipboard_clear()
  r.clipboard_append('i can has clipboardz?')
  r.update() # now it stays on the clipboard after the window is closed
  r.destroy()

out_tmp_snakecase = stringcase.snakecase(in_tmp)
out_tmp_sentencecase = stringcase.sentencecase(in_tmp)

print("\n\n"+out_tmp_snakecase+"\n\n")
print("\n\n"+out_tmp_sentencecase+"\n\n")