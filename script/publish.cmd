
@echo off

choice /C YN /m "ready to publish %*?"
if not "%errorlevel%"=="1" (
    exit /b
)
uv publish %*
