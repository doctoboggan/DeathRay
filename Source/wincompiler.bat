IF EXIST winsetup.py (
echo So far: winsetup.py exist
IF EXIST deathray.py (
echo So far: deathray.py exist
del .\DeathRay
del .\dist
python winsetup.py py2exe 
IF EXIST dist (
md .\dist\gpib_commands
md .\dist\docs
xcopy  .\docs   .\dist\docs  /s
xcopy .\gpib_commands		.\dist\gpib_commands
mv .\dist	.\DeathRay
)ELSE (
echo dist folder does not exist. Something went wrong with py2exe . py2exe faild
)) ELSE (
echo ERROR: deathray.py missing.
)) ELSE (
echo ERROR: winsetup.py missing.
)