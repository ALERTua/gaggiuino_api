
@echo off

call secrets.cmd

set PUBLISH_TOKEN=%PYPI_TOKEN%
set UV_PUBLISH_USERNAME=__token__
set UV_PUBLISH_PASSWORD=%PYPI_TOKEN%

choice /C YN /m "Have you built the package? Ready to publish?"
if not "%errorlevel%"=="1" (
    exit /b
)
uv publish %*
