pyenv local system
python ./technical.py all Yes
pyenv local 3.5.0
python ./classifier.py all Yes
python ./regression.py all Yes
python ./result.py all Yes
pyenv local system
