# COSMED XML Data Converter - Web Version

A web-based application for converting COSMED cardiopulmonary exercise test data from XML format to Excel spreadsheets.

## Features

- 🌐 **Web-based**: No installation required, works in any modern browser
- 📁 **Batch Processing**: Upload and process multiple XML files at once
- 📊 **Multiple Export Options**: Selected parameters, max values, or complete dataset
- 🔒 **Privacy-First**: All processing happens locally, files are not stored
- 📱 **Responsive**: Works on desktop, tablet, and mobile devices

## Quick Start

### Local Development
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Deploy to Streamlit Cloud
1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy automatically

## Supported COSMED Systems

- Quark CPET
- K5 series  
- Fitmate Pro
- Any COSMED system that exports XML data

## Usage

1. **Upload Files**: Select one or more COSMED XML files
2. **Choose Export Type**: Select what data to export
3. **Process**: Click "Convert to Excel" 
4. **Download**: Get your converted Excel file

## Export Types

- **Selected Parameters**: 15 key cardiopulmonary parameters
- **Max Values Only**: Peak performance values  
- **Complete Dataset**: All measurement phases
- **Custom Parameters**: Choose specific data (coming soon)

## Technical Requirements

- Python 3.8+
- Modern web browser
- Internet connection (for web deployment)