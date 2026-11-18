@echo off
setlocal
pushd "%~dp0"

set "EXTRA_PIP_INSTALL_OPTIONS="
if /I "%~1"=="-e" set "EXTRA_PIP_INSTALL_OPTIONS=--editable"

where pixi >nul 2>nul
if errorlevel 1 (
  echo "** ERROR: Pixi was not found on PATH **"
  popd
  exit /B 1
)

pixi install --environment runtime
if errorlevel 1 (
  echo "** ERROR: Pixi environment installation failed **"
  popd
  exit /B 1
)

pixi run --environment runtime uv pip install --python ".pixi\envs\runtime\python.exe" --no-deps %EXTRA_PIP_INSTALL_OPTIONS% .
if errorlevel 1 (
  echo "** ERROR: Package installation failed **"
  popd
  exit /B 1
)

pixi shell --environment runtime
popd
