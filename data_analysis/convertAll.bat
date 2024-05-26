@echo off
setlocal enabledelayedexpansion

rem Loop through all .ipynb files in the current directory
for %%f in (*.ipynb) do (
    if exist "%%f" (
        echo Converting %%f to Python script...
        jupyter nbconvert --to python "%%f"
    ) else (
        echo No .ipynb files found in the current directory.
    )
)

endlocal
