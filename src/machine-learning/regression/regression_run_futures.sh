#!/bin/bash 
. ~/.bash_profile
pyenv local 3.5.0
python ./regression.py Yes Yes
#python ./regression.py No Yes
pyenv local 3.5.0
python ./regression_result.py Yes
