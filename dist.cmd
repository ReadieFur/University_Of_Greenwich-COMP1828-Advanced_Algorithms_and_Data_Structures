@REM https://superuser.com/questions/97342/7zip-command-line-exclude-folders-by-wildcard-pattern
@REM https://superuser.com/questions/340046/creating-an-archive-from-a-directory-without-the-directory-name-being-added-to-t
7z.exe a -t7z .\dist.7z .\src -mx0 -xr!__pycache__
