@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM Stop console click-select (Quick Edit) from freezing the run,
REM and never wait for a keypress.
call :disable_quickedit

echo Starting regression scripts...
cd /d "%~dp0machine-learning\regression"
echo Now in directory: %CD%

REM Run inline (not start /B) so this window stays alive until work is done,
REM with stdin detached so Python cannot wait for Enter.
cmd /c "regression_run_futures.bat <nul"
set ERR=%ERRORLEVEL%
if %ERR% neq 0 echo Error running regression_run_futures.bat (exit %ERR%)

cd /d "%~dp0"
echo All scripts have finished.
exit /b %ERR%

:disable_quickedit
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Add-Type -Name QE -Namespace Win32 -MemberDefinition '[DllImport(\"kernel32.dll\")] public static extern IntPtr GetStdHandle(int n); [DllImport(\"kernel32.dll\")] public static extern bool GetConsoleMode(IntPtr h, out uint m); [DllImport(\"kernel32.dll\")] public static extern bool SetConsoleMode(IntPtr h, uint m);' | Out-Null;" ^
  "$h=[Win32.QE]::GetStdHandle(-10); $m=0;" ^
  "if([Win32.QE]::GetConsoleMode($h,[ref]$m)){ [void][Win32.QE]::SetConsoleMode($h, (($m -band (-bnot 64)) -bor 128)) }" >nul 2>&1
exit /b 0
