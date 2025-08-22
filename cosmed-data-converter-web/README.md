# COSMED XML Data Converter - Web Version

A modern web-based application for converting COSMED cardiopulmonary exercise test data from XML format to Excel spreadsheets. Built with Streamlit for an intuitive, professional interface.

## ✨ Features

- 🌐 **Web-based Interface**: No installation required, works in any modern browser
- 📁 **Drag & Drop Upload**: Easy batch processing of multiple XML files
- 🔍 **Smart Parameter Detection**: Automatically scans and identifies available parameters
- 📊 **Four Export Modes**: Flexible data export options for different use cases
- ⚙️ **Custom Parameter Selection**: Choose specific parameters and measurement phases
- 🧠 **Intelligent Defaults**: Smart phase selection based on parameter types
- 🔒 **Privacy-First**: All processing happens locally, no data stored on servers
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- 📈 **Professional Excel Output**: Clean, formatted spreadsheets ready for analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Git (for cloning the repository)

### Installation & Setup
```bash
# Clone the repository
git clone https://github.com/Ganzosupremo/OmniaCosmedDataCoverter.git
cd OmniaCosmedDataCoverter/cosmed-data-converter-web

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install streamlit pandas openpyxl

# Run the application
cd src
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 🏥 Supported COSMED Systems

- **Quark CPET** - Cardiopulmonary Exercise Testing System
- **K5 Series** - Portable Metabolic Testing System  
- **Fitmate Pro** - Fitness Assessment System
- **Any COSMED Device** that exports XML data in standard format

## 📖 How to Use

### Step 1: Upload Files
- Drag and drop your COSMED XML files into the upload area
- Or click "Browse files" to select multiple files
- Supported formats: `.xml` files from COSMED devices

### Step 2: Choose Export Type
Select from four export modes:

#### 🎯 **Selected Parameters** (Recommended)
15 key cardiopulmonary parameters including:
- VO2, VCO2, RER, VE
- Heart Rate, Blood Pressure
- Breathing frequency and tidal volume
- And more essential metrics

#### 📊 **Max Values Only**
Peak performance values for quick analysis:
- Maximum oxygen uptake (VO2 max)
- Peak heart rate, ventilation
- Optimal for fitness assessments

#### 📋 **Complete Dataset**  
All measurement phases and parameters:
- Rest, Warmup, Exercise phases
- Every available parameter
- Comprehensive data export

#### ⚙️ **Custom Parameters**
Advanced mode with full control:
- Select specific parameters from dropdown
- Choose measurement phases (Rest, MFO, AT, RC, Max, Value, etc.)
- Smart defaults based on parameter type
- Perfect for research and detailed analysis

### Step 3: Process & Download
- Click "Convert to Excel" to process your files
- Download your formatted Excel spreadsheet
- Files are automatically named with timestamp

## 📊 Export Types Explained

| Export Type | Use Case | Parameters | Phases |
|-------------|----------|------------|--------|
| **Selected** | General analysis | 15 key metrics | All phases |
| **Max Values** | Fitness testing | All parameters | Max values only |
| **Complete** | Research/Archive | All parameters | All phases |
| **Custom** | Specialized analysis | User-selected | User-selected |

## 🔧 Technical Features

### Smart Parameter Detection
- Automatically scans uploaded files for available parameters
- Identifies measurement phases for each parameter
- Provides parameter descriptions and units

### Intelligent Phase Selection
- **Heart Rate Parameters** → Default to 'Value' phase
- **Blood Pressure Parameters** → Default to 'Value' phase  
- **VO2/kg Parameters** → Default to exercise phases (MFO, AT, RC, Max)
- **Other Parameters** → Default to 'Max' phase

### Professional Excel Output
- Clean, formatted spreadsheets
- Proper column headers with units
- Organized data structure
- Ready for statistical analysis

## 📋 System Requirements

- **Python**: 3.10 or higher
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)
- **Memory**: 2GB RAM minimum (4GB recommended for large datasets)
- **Storage**: 100MB free space for temporary processing

## 🛠️ Development

### Project Structure
```
cosmed-data-converter-web/
├── src/
│   └── app.py              # Main Streamlit application
├── modules/
│   ├── core/
│   │   ├── xml_data_reader.py    # XML parsing
│   │   ├── excel_exporter.py     # Excel generation
│   │   └── excel_formatter.py    # Data formatting
│   └── utils/
└── README.md
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues, questions, or feature requests:
- Create an issue on GitHub
- Check existing documentation
- Review the troubleshooting guide

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.