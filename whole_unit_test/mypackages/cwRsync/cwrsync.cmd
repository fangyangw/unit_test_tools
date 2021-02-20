@ECHO OFF
REM *****************************************************************
REM
REM CWRSYNC.CMD - Batch file template to start your rsync command (s).
REM
REM *****************************************************************

REM arg1 is the host of rsync server
SET arg1=%1
REM arg2 is the username of rsync server
SET arg2=%2
REM arg3 is the password of rsync server
SET arg3=%3
REM arg4 is local file path, exaple: d/result
SET arg4=%4
REM arg5 is rsync server file path
SET arg5=%5


REM Make environment variable changes local to this batch file
SETLOCAL
REM SET RSYNC_PASSWORD=rsync-password
SET RSYNC_PASSWORD=%arg3%

REM Specify where to find rsync and related files
REM Default value is the directory of this batch file
SET CWRSYNCHOME="%~dp0"

REM Create a home directory for .ssh 
IF NOT EXIST %CWRSYNCHOME%\home\%USERNAME%\.ssh MKDIR %CWRSYNCHOME%\home\%USERNAME%\.ssh

REM Make cwRsync home as a part of system PATH to find required DLLs
SET CWOLDPATH=%PATH%
SET PATH=%CWRSYNCHOME%\bin;%PATH%

REM Windows paths may contain a colon (:) as a part of drive designation and 
REM backslashes (example c:\, g:\). However, in rsync syntax, a colon in a 
REM path means searching for a remote host. Solution: use absolute path 'a la unix', 
REM replace backslashes (\) with slashes (/) and put -/cygdrive/- in front of the 
REM drive letter:
REM 
REM Example : C:\WORK\* --> /cygdrive/c/work/*
REM 
REM Example 1 - rsync recursively to a unix server with an openssh server :
REM
REM       rsync -r /cygdrive/c/work/ remotehost:/home/user/work/
REM
REM Example 2 - Local rsync recursively 
REM
REM       rsync -r /cygdrive/c/work/ /cygdrive/d/work/doc/
REM
REM Example 3 - rsync to an rsync server recursively :
REM    (Double colons?? YES!!)
REM
REM       rsync -r /cygdrive/c/doc/ remotehost::module/doc
REM       rsync -r /cygdrive/d/rsyncdata/src zlims@zlims-isw-01.genomics.cn::zlims/fs001
REM		  rsync -rP --remove-source-files /cygdrive/%arg1% %arg3%@%arg2%::zlims
REM       rsync -rP /cygdrive/%arg4%/OutputFq/%arg5% %arg2%@%arg1%::zlims
REM       rsync -rP /cygdrive/%arg4%/workspace/%arg5%/L01/metrics %arg2%@%arg1%::zlims/%arg5%/L01/metrics

REM rsync -rtcP /cygdrive/%arg4% %arg2%@%arg1%::zlims/%arg5%
rsync -avP /cygdrive/%arg4% %arg2%@%arg1%::%arg5%

REM
REM Rsync is a very powerful tool. Please look at documentation for other options. 
REM

REM ** CUSTOMIZE ** Enter your rsync command(s) here
