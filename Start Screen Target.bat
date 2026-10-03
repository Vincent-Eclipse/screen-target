@echo off
py "%~dp0screen_target.py" 2>nul || python "%~dp0screen_target.py"
