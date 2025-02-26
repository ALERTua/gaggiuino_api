
@echo off

del /s /q dist\*.tar.gz
del /s /q dist\*.whl

uv build
