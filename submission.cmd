@REM Archive the src folder to .\submission\COMP1828_001151378_SRC.zip file
@REM https://superuser.com/questions/97342/7zip-command-line-exclude-folders-by-wildcard-pattern
@REM https://superuser.com/questions/340046/creating-an-archive-from-a-directory-without-the-directory-name-being-added-to-t
7z.exe a .\submission\COMP1828_001151378_SRC.zip .\src -mx0 -xr!__pycache__ -xr!*.map

@REM Copy the report.pdf to the submission folder.
move .\report.pdf .\submission\COMP1828_001151378_REPORT.pdf
