@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM Stop console click-select (Quick Edit) from freezing the run,
REM and never wait for a keypress.
call :disable_quickedit

echo Starting Chartlink Python scripts in parallel...
cd /d "%~dp0chartlink_import"
echo Now in directory: %CD%

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "$scripts=@('bpm_b_vol.py','bpm_b_mcup.py','bpm_b_indices.py','bpm_s_vol.py','bpm_s_mcdown.py','bpm_s_indices.py');" ^
  "$wd=(Get-Location).Path;" ^
  "$lt=[char]60;" ^
  "$procs=@();" ^
  "foreach($s in $scripts){" ^
  "  $p=Start-Process -FilePath 'cmd.exe' -ArgumentList ('/c python -u '+$s+' '+$lt+'nul') -WorkingDirectory $wd -NoNewWindow -PassThru;" ^
  "  $procs+=$p;" ^
  "  Write-Host ('Launched '+$s+' pid='+$p.Id)" ^
  "}" ^
  "if($procs.Count -gt 0){ Wait-Process -InputObject $procs };" ^
  "$failed=@($procs | Where-Object { $_.ExitCode -ne 0 });" ^
  "if($failed.Count){ Write-Host ('Finished with errors: '+(($failed | ForEach-Object { $_.Id.ToString()+'='+$_.ExitCode }) -join ', ')); exit 1 };" ^
  "Write-Host 'All Chartlink scripts finished.'; exit 0"

exit /b %ERRORLEVEL%

:disable_quickedit
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Add-Type -Name QE -Namespace Win32 -MemberDefinition '[DllImport(\"kernel32.dll\")] public static extern IntPtr GetStdHandle(int n); [DllImport(\"kernel32.dll\")] public static extern bool GetConsoleMode(IntPtr h, out uint m); [DllImport(\"kernel32.dll\")] public static extern bool SetConsoleMode(IntPtr h, uint m);' | Out-Null;" ^
  "$h=[Win32.QE]::GetStdHandle(-10); $m=0;" ^
  "if([Win32.QE]::GetConsoleMode($h,[ref]$m)){ [void][Win32.QE]::SetConsoleMode($h, (($m -band (-bnot 64)) -bor 128)) }" >nul 2>&1
exit /b 0
