pyenv local system
python ./technical.py all No
pyenv local 3.5.0
python ./regression-low.py all No
pyenv local 3.5.0
python ./regression-high.py all No
python ./regression-result.py all No
pyenv local system
