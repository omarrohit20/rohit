pyenv local system
python ./technical.py all Yes
pyenv local 3.5.0
python ./classifier-high.py all Yes
python ./classifier-low.py all Yes
python ./classifier-result.py all Yes
pyenv local system
