# cookiecutter template for basic python development on VSCode
## What you'll get
### docstring informations on hover
![hinting][hinting]
### flake8 linting
![problems][problems]
## Install
```bash
cookiecutter https://github.com/riccardo1980/py3-template-vscode.git
```
Parameters meaning:
- __project_folder__: base folder of your project
- __package_name__: package name yoy are going to develop (this will set both folder name and import statement on tests)
- __python_env_base__: base folder for your virtualenv (check )
- __python_env__: your virtualenv name
- __python_interpreter__: your virtualenv interpreter

Basically, you must be sure that <__python_env_base__>/<__python_env__>/<__python_interpreter__> is the full path of the interpreter you are going to use.
## [Optional] Install ipython notebook support
Activate yoyr virtualenv and issue the following command, with \<ENV\> as your virtual environment name:
```bash
pip install notebook
ipython kernel install --user --name=<ENV>
```

[hinting]: imgs/hover.png
[problems]: imgs/problems.png
