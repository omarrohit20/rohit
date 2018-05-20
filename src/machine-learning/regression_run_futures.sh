pyenv local system
python ./technical.py all Yes
pyenv local 3.5.0
python ./regression-low.py all Yes
pyenv local 3.5.0
python ./regression-high.py all Yes
python ./regression-result.py Yes
pyenv local system