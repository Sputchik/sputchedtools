@echo off
set "origin=%CD%"

python -m build -wnx
twine upload dist/*

python update_link.py
for %%F in (dist\*.whl) do pip install --force-reinstall "%%F"
cd sptz

python -m build -wnx
twine upload dist/*

cd "%origin%"
for /R /D %%G in (*egg-info) do @if exist "%%G" rmdir /S /Q "%%G"
for /R /D %%G in (build) do @if exist "%%G" rmdir /S /Q "%%G"
for /R /D %%G in (dist) do @if exist "%%G" rmdir /S /Q "%%G"