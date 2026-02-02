
ECHO Starting multiple Python scripts in parallel...

REM Change directory to the specified path, including a different drive
CD /D "chartlink_import"
REM Any commands after this line will execute in the new directory
echo Now in directory: %CD%

REM Start the 1 Python script
start "" /B python ./bpm_b_vol.py

REM Start the 2 Python script
start "" /B python ./bpm_b_mcup.py

REM Start the 3 Python script
start "" /B python ./bpm_b_indices.py

REM Start the 4 Python script
start "" /B python ./bpm_s_vol.py

REM Start the 5 Python script
start "" /B python ./bpm_s_mcdown.py

REM Start the 6 Python script
start "" /B python ./bpm_s_indices.py

ECHO All scripts have been launched.



PAUSE
