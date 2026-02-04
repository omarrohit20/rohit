REM Change directory to the specified path, including a different drive
CD /D "reports"
REM Any commands after this line will execute in the new directory
echo Now in directory: %CD%

REM Start the streamlit script
start "" /B streamlit run index.py

ECHO All scripts have been launched.



PAUSE
