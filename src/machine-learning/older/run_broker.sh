pyenv global system
pyenv local system
python ./technical.py broker
pyenv global 3.5.0
pyenv local 3.5.0
python ./classifier.py broker
python ./regression.py broker
python ./result.py
pyenv global system
pyenv local system
