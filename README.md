# 🫁 COSMED XML Data Converter

A comprehensive Python application for converting COSMED cardiopulmonary exercise test (CPET) data from XML files to Excel spreadsheets. Features multiple interfaces: Python API, Command-Line Interface (CLI), and modern GUI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🎯 Features

### ✨ Core Functionality
- **Batch Processing**: Process multiple XML files simultaneously
- **Three Export Formats**: Selected parameters, Max values only, or Complete dataset
- **Automatic Data Extraction**: Extract Subject ID and 15 key cardiopulmonary parameters
- **Professional Excel Output**: Formatted spreadsheets with proper headers and units
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

### 📊 Export Types

1. **Selected Parameters** (15 key metrics):
   - VO2/kg (ml/min/kg) at MFO, AT, RC, and Max phases
   - VCO2/kg (ml/min/kg) at MFO, AT, RC, and Max phases
   - VE/kg (L/min/kg) at MFO, AT, RC, and Max phases
   - HR (bpm) at AT, RC, and Max phases

2. **Max Values Only**:
   - Maximum values for all available parameters
   - Simplified dataset for peak performance analysis

3. **Complete Dataset**:
   - All measurement phases (Rest, Warmup, MFO, AT, RC, Max, Predicted, etc.)
   - Comprehensive data for detailed research and analysis

### 🖥️ Multiple Interfaces

#### 1. **Modern GUI Application** ⭐
- Built with CustomTkinter for modern appearance
- Dark/Light theme support
- Real-time progress tracking
- Auto-open result files
- Comprehensive help system

#### 2. **Command-Line Interface**
- Professional argument parsing
- Verbose output mode
- Batch processing capabilities
- Integration with automation scripts

#### 3. **Python API**
- Direct integration into existing workflows
- Programmatic access to all features
- Extensible class-based architecture

## 🚀 Quick Start

### Installation

1. **Clone or Download**:
   ```bash
   git clone <repository-url>
   cd CostmoDataConverter
   ```

2. **Automatic Setup** (Recommended):
   
   **Windows**:
   ```cmd
   setup.bat
   ```
   
   **macOS/Linux**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Manual Installation**:
   ```bash
   python -m pip install pandas>=2.0.0 openpyxl>=3.1.0 customtkinter>=5.2.0
   ```

### Usage

#### 🖥️ GUI Application (Recommended)

**Windows**:
```cmd
run_gui.bat
```

**macOS/Linux**:
```bash
./run_gui.sh
```

Or directly:
```bash
python advanced_gui.py
```

#### 💻 Command Line Interface

```bash
# Selected parameters export
python main.py input_folder output_file.xlsx --type selected

# Max values only
python main.py input_folder output_file.xlsx --type max

# Complete dataset
python main.py input_folder output_file.xlsx --type complete

# With verbose output
python main.py input_folder output_file.xlsx --type selected --verbose

# List files without processing
python main.py input_folder --list
```

#### 🐍 Python API

```python
from xml_data_reader import XmlDataReader
from excel_exporter import ExcelExporter

# Extract data
reader = XmlDataReader("path/to/xml/folder")
data = reader.extract_id_and_parameters()

# Export to Excel
exporter = ExcelExporter("output.xlsx")
exporter.export_selected_parameters(data)
```

## 📊 Export Options

### 1. Selected Parameters (Default) - **Recommended**
```bash
python main.py test_files --export selected
```
- **15 key cardiopulmonary parameters**
- **VO2/kg at MFO, AT, RC, and Max phases**
- **Perfect for focused analysis**

### 2. Max Values Only
```bash
python main.py test_files --export max
```
- **Maximum values for all parameters**
- **Simplified for peak performance analysis**

### 3. Complete Dataset
```bash
python main.py test_files --export complete
```
- **All measurement phases** (Rest, Warmup, MFO, AT, RC, Max, etc.)
- **Comprehensive data for research**

## 💻 Command Line Interface

### Basic Commands
```bash
# List XML files in directory
python main.py test_files --list

# Export with default settings
python main.py test_files

# Custom output file with verbose logging
python main.py test_files my_results.xlsx --export selected --verbose

# Show help
python main.py --help
```

### Real-world Examples
```bash
# Process data from USB drive
python main.py "D:\COSMED_Data\2024_Tests" --export selected --verbose

# Quick peak analysis
python main.py "C:\Data\CPET_Results" peak_analysis.xlsx --export max

# Research dataset
python main.py study_data research_data.xlsx --export complete
```

## 📋 Extracted Parameters

All 15 COSMED parameters are automatically extracted:

| Parameter | Description | Unit |
|-----------|-------------|------|
| **t** | Exercise duration | seconds |
| **Speed** | Treadmill speed | Kmh |
| **Pace** | Running pace | mm:ss/km |
| **VO2** | Oxygen consumption (absolute) | mL/min |
| **VO2/kg** | Oxygen consumption (relative) | mL/min/Kg |
| **VCO2** | Carbon dioxide production | mL/min |
| **METS** | Metabolic equivalents | --- |
| **RQ** | Respiratory quotient | --- |
| **VE** | Ventilation | L/min |
| **Rf** | Respiratory frequency | 1/min |
| **HR** | Heart rate | bpm |
| **HRR** | Heart rate reserve | bpm |
| **VO2/HR** | Oxygen pulse | mL/beat |
| **P Syst** | Systolic blood pressure | mmHg |
| **P Diast** | Diastolic blood pressure | mmHg |

### Key VO2/kg Phases (Selected Export)
- **MFO**: Maximum Fat Oxidation
- **AT**: Anaerobic Threshold  
- **RC**: Respiratory Compensation
- **Max**: Maximum effort

## 🔧 Python API

For advanced users or integration into other tools:

```python
from xml_data_reader import XmlDataReader
from excel_exporter import ExcelExporter

# Extract data from XML files
reader = XmlDataReader("path/to/xml/files")
extracted_data = reader.extract_id_and_parameters()

# Export options
exporter = ExcelExporter("output.xlsx")

# Option A: Selected parameters (custom selection)
exporter.export_selected_parameters(extracted_data)

# Option B: Max values only  
exporter.export_max_values_only(extracted_data)

# Option C: Complete data (all phases)
exporter.export_extracted_xml_data(extracted_data)
```
```

## 📁 Output Structure

### Excel Files Generated
- **One row per test subject**
- **Subject ID and filename** for identification  
- **Properly formatted columns** with units
- **Auto-sized columns** for readability

### Example Output (Selected Parameters)
| filename | subject_id | VO2/kg_MFO | VO2/kg_AT | VO2/kg_RC | VO2/kg_Max | HR_Max |
|----------|------------|------------|-----------|-----------|------------|--------|
| Subject1.xml | P01 | 36.6 | 37.6 | 43.0 | 49.0 | 192 |
| Subject2.xml | P02 | 34.4 | 35.4 | 41.8 | 47.3 | 175 |

## 🛠️ Installation & Setup

### System Requirements
- **Python 3.8+** (Windows, macOS, or Linux)
- **100MB free disk space**
- **Internet connection** (for initial setup)

### Automatic Installation
```bash
# Windows - Double-click or run in Command Prompt
setup.bat

# Linux/Mac - Run in terminal
chmod +x setup.sh && ./setup.sh
```

### Manual Installation (if needed)
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows: .venv\Scripts\activate  
# Linux/Mac: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Command Line Options

| Option | Description |
|--------|-------------|
| `input_path` | **Required**: Folder containing XML files |
| `output_file` | **Optional**: Excel output filename |
| `--export` | Export type: `selected`, `max`, `complete` |
| `--list` | List XML files without processing |
| `--verbose` | Enable detailed output |
| `--help` | Show complete help |

## 🔍 Sample Data

Test the installation with included sample files:
```bash
# List sample XML files
python main.py test_files --list

# Process sample data
python main.py test_files sample_output.xlsx --export selected --verbose
```

## ⚠️ Troubleshooting

### Common Issues
- **Python not found**: Install Python and add to PATH
- **Permission denied**: Close Excel files or run as administrator  
- **No XML files found**: Check folder path and file extensions
- **Package errors**: Update pip and retry installation

### Getting Help
```bash
# Show detailed help
python main.py --help

# Test with verbose output
python main.py test_files --export selected --verbose

# List files to verify detection
python main.py your_data_folder --list
```

## 📚 Documentation

- **[Installation Guide](INSTALLATION_GUIDE.md)** - Detailed setup instructions
- **[CLI Usage Guide](CLI_USAGE_GUIDE.md)** - Complete command reference
- **Sample files** in `test_files/` folder for testing

## 🔧 Dependencies

Automatically installed via `requirements.txt`:
- **pandas** (≥2.0.0) - Data processing and Excel export
- **openpyxl** (≥3.1.0) - Excel file formatting

## 🎉 Ready to Use!

The COSMED XML Data Converter is now ready for deployment on any computer. Simply copy the project folder, run the setup script, and start converting your cardiopulmonary exercise test data!

### Quick Test
```bash
# Windows
run_converter.bat test_files --export selected

# Linux/Mac
./run_converter.sh test_files --export selected
```

**Perfect for clinical researchers, exercise physiologists, and sports scientists working with COSMED CPET data!** ⚡
