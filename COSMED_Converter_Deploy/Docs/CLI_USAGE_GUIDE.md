# COSMED XML Data Converter - Command Line Usage Guide

The main.py script provides a command-line interface for converting COSMED XML files to Excel spreadsheets with three different export options.

## Basic Usage

```bash
python main.py <input_path> [output_file] --export <type>
```

## Export Types

### 1. Selected Parameters (Default)
```bash
python main.py test_files --export selected
python main.py test_files my_analysis.xlsx --export selected
```
- **Output**: 15 key parameters including VO2/kg at MFO, AT, RC, and Max
- **Best for**: Focused cardiopulmonary analysis
- **Columns**: 17 (filename, subject_id + 15 parameters)

### 2. Max Values Only
```bash
python main.py test_files --export max
python main.py test_files peak_values.xlsx --export max
```
- **Output**: Maximum values for all parameters
- **Best for**: Peak performance analysis
- **Columns**: 17 (filename, subject_id + 15 max values)

### 3. Complete Data
```bash
python main.py test_files --export complete
python main.py test_files full_dataset.xlsx --export complete
```
- **Output**: All measurement phases (Rest, Warmup, MFO, AT, RC, Max, etc.)
- **Best for**: Comprehensive analysis
- **Columns**: 168 (filename, subject_id + all phases for all parameters)

## Command Line Options

### Required Arguments
- `input_path`: Path to folder containing XML files

### Optional Arguments
- `output_file`: Excel output filename (auto-generated if not specified)
- `--export, -e`: Export type (selected, max, complete) - default: selected
- `--list, -l`: List XML files found without processing
- `--verbose, -v`: Enable detailed output
- `--help, -h`: Show help message

## Examples

### Basic Operations
```bash
# List XML files in directory
python main.py test_files --list

# Export with default settings (selected parameters)
python main.py test_files

# Export max values with custom filename
python main.py test_files my_results.xlsx --export max

# Export complete data with verbose output
python main.py test_files full_data.xlsx --export complete --verbose
```

### Real-world Examples
```bash
# Process data from USB drive
python main.py "D:\COSMED_Data\2024_Tests" --export selected --verbose

# Export only peak values for quick analysis
python main.py "C:\Data\CPET_Results" peak_analysis.xlsx --export max

# Generate comprehensive dataset for research
python main.py study_data research_complete.xlsx --export complete
```

## Output Files

The Excel files will contain:
- **One row per test subject**
- **Subject ID and filename** for identification
- **Properly formatted column names** with units
- **Auto-sized columns** for readability

### Selected Parameters Include:
- t (s)_Max - Exercise duration
- Speed (Kmh)_Max - Maximum speed
- Pace (mm:ss/km)_Max - Best pace
- VO2 (mL/min)_Max - Max oxygen consumption
- VO2/kg (mL/min/Kg)_MFO - VO2/kg at max fat oxidation
- VO2/kg (mL/min/Kg)_AT - VO2/kg at anaerobic threshold
- VO2/kg (mL/min/Kg)_RC - VO2/kg at respiratory compensation
- VO2/kg (mL/min/Kg)_Max - Max VO2/kg
- VCO2 (mL/min)_Max - Max CO2 production
- METS_Max - Max metabolic equivalents
- RQ_Max - Max respiratory quotient
- VE (L/min)_Max - Max ventilation
- Rf (1/min)_Max - Max respiratory frequency
- HR (bpm)_Max - Max heart rate
- VO2/HR (mL/beat)_Max - Max oxygen pulse

## Error Handling

The script provides clear error messages for:
- Invalid input paths
- Missing XML files
- File permission issues
- Data extraction errors

## Tips

1. **Use absolute paths** when working with data on external drives
2. **Check file permissions** if you get access denied errors
3. **Use --list first** to verify XML files are detected
4. **Use --verbose** for detailed processing information
5. **Close Excel files** before overwriting existing output files

## Requirements

Make sure you have the required packages installed:
```bash
pip install pandas openpyxl
```
