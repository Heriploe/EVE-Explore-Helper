@echo off
setlocal

python -m PyInstaller --noconfirm eve_explore_helper_app.spec
if errorlevel 1 exit /b %errorlevel%

echo Build complete. Check dist\ for output executable.
echo settings.json and visited.json are external runtime files created beside the executable.
