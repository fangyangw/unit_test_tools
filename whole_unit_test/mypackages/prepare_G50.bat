@echo off
%1 mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit
cd /d "%~dp0"

python prepare.py DNBSEQ-G50

@ECHO ...
@ECHO Create complete.
timeout /T 5
