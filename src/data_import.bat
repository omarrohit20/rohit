
ECHO Starting multiple Python scripts in parallel...

REM Save the current directory to restore later
SET SCRIPT_DIR=%~dp0

REM Change directory to data-import and start the import script
CD /D "%SCRIPT_DIR%data-import"
echo Now in directory: %CD%
start "" /B cmd /c importer-history.bat
if errorlevel 1 echo Error launching importer-history.bat

REM Restore original directory
CD /D "%SCRIPT_DIR%"

ECHO All scripts have been launched.

PAUSE
