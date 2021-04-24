#!/usr/bin/env bash

set -e 

VIRTUALENV_NAME={{cookiecutter.virtualenv_name}}
TEST_REQ_FILE="requirements-test.txt"
GITIGNORE_TEMPLATE=.gitignore.template

log_msg(){
  echo -e "$1"
}

log_msg "Creating virtualenv: $VIRTUALENV_NAME" 
python3 -m venv $VIRTUALENV_NAME 

log_msg "Adding test requirements" 
source $VIRTUALENV_NAME/bin/activate
pip3 install -r $TEST_REQ_FILE
  
log_msg "Creating .gitignore from template"
mv $GITIGNORE_TEMPLATE .gitignore

if ! grep -Fxq $VIRTUALENV_NAME .gitignore 
then
  log_msg "Adding virtualenv folder to .gitignore"
  echo $VIRTUALENV_NAME >> .gitignore
fi

log_msg "Adding virtualenv folder to .flake8 exclude"

cat > .flake8 << EOF
[flake8]
exclude = $VIRTUALENV_NAME
EOF

log_msg "Configuring version control"
git init && git add . && git commit -m "first commit"
git branch -m main
