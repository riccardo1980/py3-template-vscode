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
- __linter__: linter configuration: one between 'flake8' or 'pylint' ('no' for no linter)
- __formatter__: formatter configuration: 'black' ('no' for no formatter) 


## Extend to further tools
Each tool is described with a folder inside `{{cookiecutter.project_slug}}/tools_config`: folder name must be equal to the tool.
A number of object must be present in the folder:
- __requirements.txt__: a text file with requirements, one per line
- __vscode_settings.json__: a JSON formatted text file, containing vscode configuratin for that tool
- [OPTIONAL] __config_files__: a folder: each file in first level will be copied in root project

In order to support a tool you need to create a folder in `{{cookiecutter.project_slug}}/tools_config` matching the name of the tool.

If a different tool kind (other than currently supported __formatter__, __linter__, __import_sorter__) is needed, you need also to:
1. create a variable `cookiecutter.json` that will hold the new kind
2. add the variable in `tools_list` of function `do_post_hook()` of `hooks/post_gen_project.py`    

## [Optional] Install ipython notebook support
If you have chosen to not support ipython kernel at cookie creation, you can still install and configure kernels at a later stage.
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
