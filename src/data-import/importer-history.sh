#!/bin/bash 
. ~/.bash_profile
pyenv local 3.5.0
python ./cleaner.py
python ./S2cripHistoryImporterNsePy.py all Yes
