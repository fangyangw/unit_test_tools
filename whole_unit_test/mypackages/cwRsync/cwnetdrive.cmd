@ECHO OFF
REM *****************************************************************
REM
REM CWNETDRIVE.CMD - Batch file template to start your rsync command (s),from local to network drive
REM
REM *****************************************************************

REM arg1 is UNC path of net drive
SET arg1=%1
REM arg2 is the username UNC
SET arg2=%2
REM arg3 is the password UNC
SET arg3=%3
REM arg4 is local file path, exaple: d/result
SET arg4=%4
REM arg5 is remote file path
SET arg5=%5
REM arg6 is net drirve name
SET arg6=%6

REM Make environment variable changes local to this batch file
SETLOCAL

REM Specify where to find rsync and related files
REM Default value is the directory of this batch file
SET CWRSYNCHOME=%~dp0
SET SSHPATH="%CWRSYNCHOME%home\%USERNAME%\.ssh"
REM Create a home directory for .ssh 
IF NOT EXIST %SSHPATH% MKDIR %SSHPATH%

REM Make cwRsync home as a part of system PATH to find required DLLs
SET CWOLDPATH=%PATH%
SET PATH=%CWRSYNCHOME%bin;%PATH%
REM Windows paths may contain a colon (:) as a part of drive designation and 
REM backslashes (example c:\, g:\). However, in rsync syntax, a colon in a 
REM path means searching for a remote host. Solution: use absolute path 'a la unix', 
REM replace backslashes (\) with slashes (/) and put -/cygdrive/- in front of the 

IF %arg2% neq - (
    IF %arg3% neq - (
        NET USE %arg1% /user:%arg2% %arg3%
    )
)
rsync -avp /cygdrive/%arg4% /%arg6%svr/%arg5%
REM ** CUSTOMIZE ** Enter your rsync command(s) here