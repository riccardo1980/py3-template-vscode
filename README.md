# cookiecutter template for VSCode Python3 development

## Info
- virtualenv creation
- VSCode setup
- testing/linting tools install
- local git repository init and first commit on main

## Install
### Prerequisites
```bash
python3 install -U cookiecutter
cookiecutter https://github.com/riccardo1980/py3-template-vscode.git
```

Parameters meaning:
- __project_slug__: base folder of your project
- __package_name__: package name you are going to develop (this will set both folder name and import statement on tests)
- __virtualenv_name__: your virtualenv interpreter

## [Optional] Install ipython notebook support
Activate yoyr virtualenv and issue the following command, with \<ENV\> as your virtual environment name:
```bash
source .venv/bin/activate
pip install notebook
ipython kernel install --user --name=.venv
```

## What you'll get

### Docstring informations on hover

![hinting][hinting]

### flake8 linting

![problems][problems]


[hinting]: imgs/hover.png
[problems]: imgs/problems.png
