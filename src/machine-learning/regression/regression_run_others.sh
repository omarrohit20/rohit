#!/bin/bash 
. ~/.bash_profile
pyenv local 3.5.0
python ./regression.py No No
pyenv local 3.5.0
python ./regression_result.py No
pyenv local system
