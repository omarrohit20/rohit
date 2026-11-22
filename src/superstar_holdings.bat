REM Refresh celebrity investor holdings (Nsedata.superstar_holdings). Safe to run daily.
CD /D "%~dp0indian-trading-skills"
echo Now in directory: %CD%
python skills\superstar-holdings\scripts\run_superstar_holdings.py %* <nul
