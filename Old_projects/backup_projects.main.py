import os
import time

__version__ = "0.1"

# 1. The files and directories to be backed up are
# specified in a list.
# Example on Windows:
# source = ['"C:\\My Documents"', 'C:\\Code']
# Example on Mac OS X and Linux:
source = '/home/kornel/Programowanie/Python'


# Notice we had to use double quotes inside the string
# for names with spaces in it.

# 2. The backup must be stored in a
# main backup directory
# Example on Windows:
# target_dir = 'E:\\Backup'
# Example on Mac OS X and Linux:
target_dir = '/home/kornel/backup/Python'
# Remember to change this to which folder you will be using

# Create target directory if it is not present
if not os.path.exists(target_dir):
        os.mkdir(target_dir)  # make directory

# 3. The files are backed up into a zip file.
# 4. The project name is the name of the subdirectory
# in the main directory.
project_name = input('Enter name of your project: ')
project_dir = target_dir + os.sep + project_name
# The current time is the name of the zip archive.
now = time.strftime('%Y%m%d_%H%M%S')


# This looking for some files with name of project
list_of_files = list()
for file in os.listdir(source):
    if file.startswith(project_name+'.'):
         if not file.find('.py') == -1:
            list_of_files.append(file)
    
if len(list_of_files) == 0:
    print("Sorry, project: {} doesn't exist!".format(project_name))
else:
    # Create the subdirectory if it isn't already there
    if not os.path.exists(project_dir):
        os.mkdir(project_dir)
        print('Successfully created directory', project_dir)


'''
# remove extension from file
for i in range(len(list_of_files)):
    list_of_files[i] = list_of_files[i].replace('.py', '', 1)
'''

print(list_of_files)



# Take a comment from the user to
# create the name of the zip file
comment = input('Enter a comment --> ')
# Check if a comment was entered
if len(comment) == 0:
    target = project_dir + os.sep + project_name + '_'  + now + '.zip'
else:
    target = project_dir + os.sep + project_name + '_' +  now + '_' + \
    comment.replace(' ', '_') + '.zip'
# 5. We use the zip command to put the files in a zip archive
zip_command = 'zip {0} {1}'.format(target,' '.join(str(x) for x in list_of_files))

# Run the backup
print('Zip command is:')
print(zip_command)
print('Running:')
if os.system(zip_command) == 0:
    print('Successful backup to', target)
else:
    print('Backup FAILED')

