## Setup

If there is first of setting up the enviroment on Windows 10, then maybe required followed steps:
```
# install virtualenv from admin account
pip install virtualenv

# (Run PowerShell as an admin)Enable execution of PowerShell scripts is: 
set-executionpolicy remotesigned
```

Step by step venv install:
* Setup new virtualenv, you can skip if you made it via IDE
```
virtualenv venv
```
or using fixed Python version:
```
<python path> -m venv venv

C:\Users\stefancz_k_ext\AppData\Local\Programs\Python\Python38\python.exe -m venv venv
```

* Activatie(connect to) newly created venv
    * Bash
    ```
    source venv/bin/activate
    ```
    * Windows
    ```
    venv\Scripts\activate
    ```
    
* Install required dependencies
```
pip install -r pip_requirements.txt
```


## Run
Run script
```
python ./<script_name>.py
```
Example of usage with arguments
```
python ./<script_name>.py --parameter_name <parameter_value>
```
