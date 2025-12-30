@echo off
chcp 65001 >nul
python "%~dp0github_checker.py" %*  -f
pause
