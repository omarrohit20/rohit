pyenv global 3.5.0
pyenv local 3.5.0
python ./classifier.py all
python ./regression.py all
python ./result.py
pyenv global system
pyenv local system
