1. Create a virtual environment, override the following line in `.vscode/settngs.json` with the path of your interpreter in the virtualenv
```bash
"python.pythonPath": "/path/to/env/bin/python3"
```
2. Activate virtual environment and install required packages:
```bash
pip 3 install -r requirements.txt
```
3. Open `test.py` and check:  
    - whether a popup hint appears when you hover the line `import sys`  
![hinting][hinting]
    - whether the editor lists as an error the absence of a newline at the end
![problems][problems]

[hinting]: imgs/hover.png
[problems]: imgs/problems.png
