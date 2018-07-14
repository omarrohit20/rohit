#!/bin/bash 
. ~/.bash_profile
python ./cleaner.py
python ./S2cripHistoryImporter.py all Yes
