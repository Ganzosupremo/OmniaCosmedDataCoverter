@echo off
echo ===============================================
echo COSMED XML Data Converter - Package Creator
echo ===============================================
echo.

REM Create deployment package folder
if exist "COSMED_Converter_Deploy" rmdir /s /q "COSMED_Converter_Deploy"
mkdir "COSMED_Converter_Deploy"

echo Copying essential files...

REM Copy core application files
copy "main.py" "COSMED_Converter_Deploy\"
copy "xml_data_reader.py" "COSMED_Converter_Deploy\"
copy "excel_exporter.py" "COSMED_Converter_Deploy\"
copy "requirements.txt" "COSMED_Converter_Deploy\"

REM Copy setup and run scripts
copy "setup.bat" "COSMED_Converter_Deploy\"
copy "setup.sh" "COSMED_Converter_Deploy\"
copy "run_converter.bat" "COSMED_Converter_Deploy\"
copy "run_converter.sh" "COSMED_Converter_Deploy\"

REM Copy documentation
xcopy "README.md" "COSMED_Converter_Deploy\Docs"
xcopy "INSTALLATION_GUIDE.md" "COSMED_Converter_Deploy\Docs"
xcopy "CLI_USAGE_GUIDE.md" "COSMED_Converter_Deploy\Docs"

REM Copy test files
xcopy "test_files" "COSMED_Converter_Deploy\test_files\" /s /e /i

echo.
echo ===============================================
echo Deployment package created successfully!
echo ===============================================
echo.
echo Package location: COSMED_Converter_Deploy\
echo.
echo To deploy on another computer:
echo 1. Copy the COSMED_Converter_Deploy folder
echo 2. Run setup.bat (Windows) or ./setup.sh (Linux/Mac)
echo 3. Test with: run_converter.bat test_files --list
echo.
echo Package contents:
dir "COSMED_Converter_Deploy"
echo.
pause
