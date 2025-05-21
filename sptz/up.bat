@echo off

set "origin=%CD%"
python -m build -wnx
twine upload dist/*
rmdir /S /Q dist

for /D %%G in (".\src\*egg-info") do rmdir /S /Q "%%G"
rmdir /S /Q build