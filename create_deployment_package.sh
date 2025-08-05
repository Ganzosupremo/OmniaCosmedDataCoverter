#!/bin/bash

echo "==============================================="
echo "COSMED XML Data Converter - Package Creator"
echo "==============================================="
echo

# Create deployment package folder
if [ -d "COSMED_Converter_Deploy" ]; then
    rm -rf "COSMED_Converter_Deploy"
fi
mkdir "COSMED_Converter_Deploy"

echo "Copying essential files..."

# Copy core application files
cp main.py COSMED_Converter_Deploy/
cp xml_data_reader.py COSMED_Converter_Deploy/
cp excel_exporter.py COSMED_Converter_Deploy/
cp requirements.txt COSMED_Converter_Deploy/

# Copy setup and run scripts
cp setup.bat COSMED_Converter_Deploy/
cp setup.sh COSMED_Converter_Deploy/
cp run_converter.bat COSMED_Converter_Deploy/
cp run_converter.sh COSMED_Converter_Deploy/

# Copy documentation
cp README.md COSMED_Converter_Deploy/
cp INSTALLATION_GUIDE.md COSMED_Converter_Deploy/
cp CLI_USAGE_GUIDE.md COSMED_Converter_Deploy/

# Copy test files
cp -r test_files COSMED_Converter_Deploy/

# Make scripts executable
chmod +x COSMED_Converter_Deploy/setup.sh
chmod +x COSMED_Converter_Deploy/run_converter.sh

echo
echo "==============================================="
echo "Deployment package created successfully!"
echo "==============================================="
echo
echo "Package location: COSMED_Converter_Deploy/"
echo
echo "To deploy on another computer:"
echo "1. Copy the COSMED_Converter_Deploy folder"
echo "2. Run ./setup.sh (Linux/Mac) or setup.bat (Windows)"
echo "3. Test with: ./run_converter.sh test_files --list"
echo
echo "Package contents:"
ls -la COSMED_Converter_Deploy/
echo
