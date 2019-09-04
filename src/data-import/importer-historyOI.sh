#!/bin/bash 
. ~/.bash_profile
pyenv local 3.5.0
python ./S2cripHistoryOIImporter.py all
python ./S2cripHistoryOIImporterNext.py all