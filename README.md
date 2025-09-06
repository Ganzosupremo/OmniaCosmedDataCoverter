# 🫁 COSMED XML Data Converter

A comprehensive Python application for converting COSMED cardiopulmonary exercise test (CPET) data from XML files to Excel spreadsheets, plus advanced phase statistics analysis. Features multiple interfaces: Web Application, Python API, Command-Line Interface (CLI), and modern GUI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Web](https://img.shields.io/badge/Web_Interface-Streamlit-red.svg)

## 🧩 SaaS Architecture

An initial multi-service architecture for running the Phase Analyzer as a SaaS is provided in [SAAS_ARCHITECTURE.md](SAAS_ARCHITECTURE.md). It includes Docker Compose definitions for the Streamlit frontend, FastAPI API, RQ worker, PostgreSQL, Redis and an S3-compatible storage service:

```bash
docker compose up --build
```

The web interface will be available at `http://localhost:8501` and the API health check at `http://localhost:8000/health`.

## 🎯 Features

### ✨ Core Functionality
- **🌐 Web Interface**: Modern browser-based application with Streamlit
- **📊 Phase Statistics Analysis**: Advanced exercise phase analysis with comprehensive statistics
- **📚 Batch Processing**: Process multiple files simultaneously (XML conversion or phase analysis)
- **🎯 Custom Parameter Selection**: Choose specific parameters and phases for targeted analysis
- **Three Export Formats**: Selected parameters, Max values only, or Complete dataset
- **Automatic Data Extraction**: Extract Subject ID and 15 key cardiopulmonary parameters
- **Professional Excel Output**: Formatted spreadsheets with proper headers and units
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

### 🌐 Web Application Features
- **Dual Functionality**: XML conversion AND phase statistics analysis in one interface
- **Real-time Processing**: Live progress updates and instant results preview
- **Parameter Scanning**: Automatically detect available parameters from uploaded files
- **Custom Analysis**: Select specific parameters and measurement phases
- **Batch Analysis**: Upload multiple subjects for comparative analysis
- **Subject-Based Processing**: Each file represents one test subject with flattened output format
- **Interactive Results**: Preview data before downloading with expandable sections

### 📊 Export Types

#### XML Conversion Exports:

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

4. **Custom Parameters**:
   - 🆕 Choose specific parameters and measurement phases
   - Create focused datasets for targeted research
   - Smart parameter selection with VO2/kg multi-phase support

#### Phase Statistics Exports:

1. **Single File Analysis**:
   - Average, Standard Deviation, and Maximum values per phase
   - Phase-by-phase breakdown of exercise data
   - Comprehensive statistical analysis

2. **🆕 Batch Subject Analysis**:
   - **Subjects as Rows**: Each file represents one test subject
   - **Phase_Parameter Columns**: Flattened format (e.g., "EXERCISE 1_HR", "RECOVERY 2_VO2")
   - **3 Statistical Sheets**: Average, StdDev, Max values
   - **Consistent Schema**: Missing phases automatically filled with NaN
   - **Research-Ready Format**: Direct import into statistical software

### 🖥️ Multiple Interfaces

#### 1. **🌐 Web Application** ⭐ **NEW & RECOMMENDED**
- **Modern Streamlit Interface**: Professional web-based application
- **Two Main Functions**:
  - 🔄 **XML Converter**: Convert COSMED XML files to Excel
  - 📊 **Phase Statistics**: Analyze exercise phase data with comprehensive statistics
- **Advanced Features**:
  - Custom parameter selection with smart presets
  - Batch processing with progress tracking
  - Real-time data preview and validation
  - Interactive results display
  - Parameter scanning and detection
- **Subject-Based Batch Analysis**: Each file = one subject, subjects as rows output
- **Cross-platform compatibility**: Works in any modern web browser

#### 2. **Modern GUI Application**
- Built with CustomTkinter for modern appearance
- Dark/Light theme support
- Real-time progress tracking
- Auto-open result files
- Comprehensive help system

#### 3. **Command-Line Interface**
- Professional argument parsing
- Verbose output mode
- Batch processing capabilities
- Integration with automation scripts

#### 4. **Python API**
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

#### 🌐 Web Application (NEW & Recommended)

**Start the web interface**:
```bash
# Navigate to web app directory
cd cosmed-data-converter-web

# Install web dependencies (first time only)
pip install streamlit

# Launch web application
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

**Features Available:**
- **XML Converter Tab**: Convert COSMED XML files to Excel with custom parameter selection
- **Phase Statistics Tab**: 
  - Single file analysis with comprehensive phase statistics
  - Batch analysis with subject-based output format
  - Parameter filtering and custom analysis options
  - Real-time progress tracking and results preview

#### 🖥️ GUI Application

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
# XML Data Conversion
from xml_data_reader import XmlDataReader
from excel_exporter import ExcelExporter

# Extract data
reader = XmlDataReader("path/to/xml/folder")
data = reader.extract_id_and_parameters()

# Export to Excel
exporter = ExcelExporter("output.xlsx")
exporter.export_selected_parameters(data)

# 🆕 Phase Statistics Analysis
from cosmed-data-converter-web.web_modules.core.phase_analyzer import PhaseAnalyzer
import pandas as pd

# Single file analysis
analyzer = PhaseAnalyzer()
df = pd.read_excel("exercise_data.xlsx")
results = analyzer.analyze_dataframe(df)

# Batch analysis (NEW SPEC: subjects as rows)
files = [file1, file2, file3]  # File objects
file_names = ["subject1.xlsx", "subject2.xlsx", "subject3.xlsx"]
batch_results = analyzer.analyze_batch_files(files, file_names)

# Export batch results with subject-based format
excel_bytes = analyzer.export_batch_statistics_to_bytes(batch_results)
```

## 📊 Export Options

### 🔄 XML Conversion Mode
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

### 📊 Phase Statistics Mode (NEW)
Available through the **web interface** at `http://localhost:8501`:

#### Single File Analysis:
- Upload one Excel/CSV file with Phase column
- Get comprehensive statistics per phase (Average, StdDev, Max)
- Export results to Excel with 3 sheets

#### Batch Subject Analysis:
- Upload multiple files (each = one test subject)
- **Output Format**: Subjects as rows, Phase_Parameter as columns
- **3 Statistical Sheets**: Average, StdDev, Max values
- **Example columns**: `EXERCISE 1_HR`, `RECOVERY 2_VO2`, `WARMUP_Speed`
- **Research-ready**: Direct import into R, SPSS, or other statistical software

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

### XML Conversion Output
- **One row per test subject**
- **Subject ID and filename** for identification  
- **Properly formatted columns** with units
- **Auto-sized columns** for readability

#### Example Output (Selected Parameters)
| filename | subject_id | VO2/kg_MFO | VO2/kg_AT | VO2/kg_RC | VO2/kg_Max | HR_Max |
|----------|------------|------------|-----------|-----------|------------|--------|
| Subject1.xml | P01 | 36.6 | 37.6 | 43.0 | 49.0 | 192 |
| Subject2.xml | P02 | 34.4 | 35.4 | 41.8 | 47.3 | 175 |

### 🆕 Phase Statistics Output

#### Single File Analysis:
- **3 sheets**: Average, StdDev, Max
- **Rows**: Exercise phases (WARMUP, EXERCISE 1, RECOVERY 1, etc.)
- **Columns**: Parameters (HR, VO2, Speed, etc.)

#### Batch Subject Analysis (NEW SPEC):
- **3 sheets**: Average, StdDev, Max
- **Rows**: Test subjects (one per uploaded file)
- **Columns**: Phase_Parameter combinations

#### Example Batch Output:
| Subject | WARMUP_HR | EXERCISE 1_HR | EXERCISE 1_VO2 | RECOVERY 1_HR | RECOVERY 1_VO2 |
|---------|-----------|---------------|----------------|---------------|----------------|
| Subject_1_Test | 70.0 | 150.0 | 25.0 | 90.0 | 12.0 |
| Subject_2_Test | 65.0 | 140.0 | 22.0 | 85.0 | 13.0 |
| Subject_3_Test | 72.0 | 145.0 | 24.0 | 88.0 | 14.0 |

**Benefits:**
- ✅ **Research-ready format**: Direct import into statistical software
- ✅ **Consistent schema**: Missing phases automatically filled with NaN
- ✅ **Cross-subject comparison**: Easy to analyze differences between subjects
- ✅ **Scalable**: Handles varying phase structures across subjects

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

# 🆕 For Web Interface (additional step)
cd cosmed-data-converter-web
pip install streamlit
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

# 🆕 For web interface (additional dependencies)
pip install streamlit
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

### XML Conversion Testing:
```bash
# List sample XML files
python main.py test_files --list

# Process sample data
python main.py test_files sample_output.xlsx --export selected --verbose
```

### 🆕 Phase Statistics Testing:
1. **Start the web interface**:
   ```bash
   cd cosmed-data-converter-web
   streamlit run app.py
   ```

2. **Navigate to Phase Statistics tab**

3. **Try single file analysis**: Upload any Excel/CSV file with a 'Phase' column

4. **Try batch analysis**: Upload multiple files to see subject-based output format

**Web Interface URL**: `http://localhost:8501`

## ⚠️ Troubleshooting

### Common Issues
- **Python not found**: Install Python and add to PATH
- **Permission denied**: Close Excel files or run as administrator  
- **No XML files found**: Check folder path and file extensions
- **Package errors**: Update pip and retry installation
- **🆕 Web interface not loading**: Ensure Streamlit is installed (`pip install streamlit`)
- **🆕 Phase column missing**: Ensure uploaded files have a 'Phase' column for statistics analysis

### Getting Help
```bash
# Show detailed help
python main.py --help

# Test with verbose output
python main.py test_files --export selected --verbose

# List files to verify detection
python main.py your_data_folder --list

# 🆕 Test web interface
cd cosmed-data-converter-web
streamlit run app.py
# Then open http://localhost:8501
```

## 📚 Documentation

- **[Installation Guide](INSTALLATION_GUIDE.md)** - Detailed setup instructions
- **[CLI Usage Guide](CLI_USAGE_GUIDE.md)** - Complete command reference
- **Sample files** in `test_files/` folder for testing

## 🔧 Dependencies

Automatically installed via `requirements.txt`:
- **pandas** (≥2.0.0) - Data processing and Excel export
- **openpyxl** (≥3.1.0) - Excel file formatting

### 🆕 Web Interface Dependencies:
- **streamlit** - Modern web application framework
- **Additional packages** automatically installed with Streamlit

Install web dependencies:
```bash
pip install streamlit
```

## 🎉 Ready to Use!

The COSMED XML Data Converter is now ready for deployment on any computer. Simply copy the project folder, run the setup script, and start converting your cardiopulmonary exercise test data!

### Quick Test

#### XML Conversion:
```bash
# Windows
run_converter.bat test_files --export selected

# Linux/Mac
./run_converter.sh test_files --export selected
```

#### 🆕 Web Interface (Recommended):
```bash
cd cosmed-data-converter-web
streamlit run app.py
# Open http://localhost:8501 in your browser
```

**Perfect for clinical researchers, exercise physiologists, and sports scientists working with COSMED CPET data!** ⚡

### 🆕 New Features Summary:
- 🌐 **Modern Web Interface** with dual XML conversion and phase analysis
- 📊 **Advanced Phase Statistics** with single file and batch processing
- 🎯 **Custom Parameter Selection** for targeted analysis
- 👥 **Subject-Based Batch Analysis** with research-ready output format
- 🔄 **Real-time Processing** with interactive results preview
- 📈 **Statistical Analysis** with comprehensive phase-by-phase breakdown
