# COSMED XML Data Converter - Installation Guide

This guide will help you install and run the COSMED XML Data Converter on any computer.

## System Requirements

- **Python 3.8 or newer**
- **Windows, macOS, or Linux**
- **At least 100MB free disk space**

## Quick Installation

### Option 1: Automatic Setup (Recommended)

#### Windows:
1. Download/copy the entire project folder to your computer
2. **Double-click `setup.bat`** or open Command Prompt in the folder and run:
   ```cmd
   setup.bat
   ```

#### Linux/Mac:
1. Download/copy the entire project folder to your computer
2. Open terminal in the folder and run:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

### Option 2: Manual Installation

If automatic setup doesn't work:

1. **Install Python** (if not already installed):
   - Windows: Download from https://python.org (check "Add to PATH")
   - macOS: `brew install python3` or download from python.org
   - Ubuntu/Debian: `sudo apt install python3 python3-pip python3-venv`

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## How to Use

### Option 1: Using Run Scripts (Easiest)

#### Windows:
The first example is with the provided test files. Use the second example for real files. 
```cmd
run_converter.bat test_files --export selected
run_converter.bat "C:\Data\CPET" results.xlsx --export max
```

#### Linux/Mac:
```bash
./run_converter.sh test_files --export selected
./run_converter.sh "/home/user/data" results.xlsx --export max
```

### Option 2: Direct Python Commands

1. **Activate virtual environment** (if not already active):
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

2. **Run the converter**:
   ```bash
   python main.py test_files --export selected
   python main.py data_folder results.xlsx --export max --verbose
   ```

## Command Examples

```bash
# List XML files in a folder
run_converter.bat data_folder --list

# Export selected parameters (default)
run_converter.bat data_folder

# Export max values with custom filename
run_converter.bat data_folder peak_results.xlsx --export max

# Export complete dataset with verbose output
run_converter.bat data_folder complete.xlsx --export complete --verbose

# Show help
run_converter.bat --help
```

## Export Types

1. **Selected Parameters** (`--export selected`) - Default
   - 15 key cardiopulmonary parameters
   - Includes VO2/kg at MFO, AT, RC, and Max
   - Best for focused analysis

2. **Max Values Only** (`--export max`)
   - Maximum values for all parameters
   - Simplified dataset for peak performance analysis

3. **Complete Data** (`--export complete`)
   - All measurement phases (Rest, Warmup, MFO, AT, RC, Max, etc.)
   - Comprehensive dataset for detailed research

## Troubleshooting

### Python Not Found
- **Windows**: Reinstall Python and check "Add Python to PATH"
- **Linux**: Install with package manager: `sudo apt install python3`
- **macOS**: Install via Homebrew: `brew install python3`

### Permission Denied Errors
- **Windows**: Run Command Prompt as Administrator
- **Linux/Mac**: Use `sudo` or check file permissions

### Virtual Environment Issues
- Delete `.venv` folder and run setup script again
- Make sure you have `python3-venv` installed (Linux)

### Package Installation Fails
- Update pip: `python -m pip install --upgrade pip`
- Check internet connection
- Try installing packages individually:
  ```bash
  pip install pandas
  pip install openpyxl
  ```

### Excel File Access Denied
- Close the Excel file if it's open
- Check write permissions in the output directory
- Use a different output filename

## File Structure

After installation, your folder should contain:

```
COSMED_Data_Converter/
├── main.py                 # Main CLI application
├── xml_data_reader.py      # XML parsing functionality
├── excel_exporter.py       # Excel export functionality
├── requirements.txt        # Python dependencies
├── setup.bat              # Windows setup script
├── setup.sh               # Linux/Mac setup script
├── run_converter.bat      # Windows run script
├── run_converter.sh       # Linux/Mac run script
├── README.md              # User guide
├── CLI_USAGE_GUIDE.md     # CLI documentation
├── test_files/            # Sample XML files
└── .venv/                 # Virtual environment (created by setup)
```

## Moving to Another Computer

To move the converter to another computer:

1. **Copy the entire project folder** (including `.venv` if it exists)
2. **Run setup script** on the new computer to ensure dependencies
3. **Test with sample data**: `run_converter.bat test_files --list`

## Sample Data

The `test_files/` folder contains sample COSMED XML files for testing:
- Subject P01 (Weinert Philipp)
- Subject P02 (Siepe Theresa)

Use these to verify the installation:
```bash
run_converter.bat test_files --export selected --verbose
```

## Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Verify Python installation: `python --version`
3. Check virtual environment: `.venv` folder should exist
4. Test with sample data first
5. Use `--verbose` flag for detailed error information

## Dependencies

The converter automatically installs these Python packages:
- **pandas** (≥2.0.0) - Data manipulation and Excel export
- **openpyxl** (≥3.1.0) - Excel file creation and formatting

No additional software or licenses required!
