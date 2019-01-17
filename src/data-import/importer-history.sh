#!/bin/bash 
. ~/.bash_profile
python ./cleaner.py
python ./S2cripHistoryImporterNsePy.py all Yes
