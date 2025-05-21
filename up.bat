@echo off

set "origin=%CD%"

python -m build -wnx
twine upload dist/*

for %%F in (dist\*.whl) do pip install --force-reinstall "%%F"

rmdir /S /Q dist
rmdir /S /Q build

cd sptz
up.bat
cd ..

echo %origin%\*egg-info
pause
for /R /D %%G in (*egg-info) do rmdir /S /Q "%%G"