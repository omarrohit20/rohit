#!/bin/bash 
. ~/.bash_profile
pyenv local 3.5.0
python ./S2cripHistoryImporterYahoo.py update Yes
python ./S2cripHistoryImporterYahoo.py update No

