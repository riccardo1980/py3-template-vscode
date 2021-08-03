# cookiecutter template for VSCode Python3 development

## Info
- virtualenv creation
- VSCode setup
- testing/linting tools install
- local git repository init and first commit on main

## Install
```bash
python3 install -U cookiecutter
cookiecutter https://github.com/riccardo1980/py3-template-vscode.git
```

Parameters meaning:
- __project_slug__: base folder of your project
- __package_name__: package name you are going to develop (this will set both folder name and import statement on tests)
- __virtualenv_name__: name of virtualenv that will be created in project root
- __configure_version_control__: git init and main branch creation are performed
- __upgrade_pip__: pip is upgraded to latest version
- __ipython_support__: support for ipython notebooks
- __linter__: linter configuration: one between flake8 or pylint (no for no linter)
- __formatter__: formatter configuration: black (no for no formatter) 

## [Optional] Install ipython notebook support
Activate your virtualenv and issue the following command, with \<ENV\> as your virtual environment name:
```bash
source .venv/bin/activate
pip install notebook
ipython kernel install --user --name=.venv
```

## What you'll get

### Docstring informations on hover

![hinting][hinting]

### flake8/pylint linting

![problems][problems]


[hinting]: imgs/hover.png
[problems]: imgs/problems.png
