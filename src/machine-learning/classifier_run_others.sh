pyenv local system
python ./technical.py all No
pyenv local 3.5.0
python ./classifier-high.py all No
python ./classifier-low.py all No
python ./classifier-result.py all No
pyenv local system
