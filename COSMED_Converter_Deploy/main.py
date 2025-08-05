from xml_data_reader import XmlDataReader
from excel_exporter import ExcelExporter
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="COSMED XML Data Converter - Extract and export cardiopulmonary exercise test data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Export Options:
  selected    Export custom selection of 15 key parameters including VO2/kg at MFO, AT, RC, and Max
  max         Export only maximum values for all parameters (simplified)
  complete    Export all measurement phases (Rest, Warmup, MFO, AT, RC, Max, etc.)

Examples:
  python main.py test_files selected_data.xlsx --export selected
  python main.py test_files max_values.xlsx --export max
  python main.py test_files complete_data.xlsx --export complete
  python main.py test_files --export selected  (uses default output filename)
        """
    )
    
    parser.add_argument(
        "input_path",
        help="Path to folder containing XML files"
    )
    
    parser.add_argument(
        "output_file",
        nargs="?",
        help="Output Excel file path (optional, defaults based on export type)"
    )
    
    parser.add_argument(
        "--export", "-e",
        choices=["selected", "max", "complete"],
        default="selected",
        help="Export type: selected (default), max, or complete"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List XML files found in the input path without processing"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate input path
    if not os.path.exists(args.input_path):
        print(f"Error: Input path '{args.input_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(args.input_path):
        print(f"Error: Input path '{args.input_path}' is not a directory.")
        sys.exit(1)
    
    # Set default output filename if not provided
    if not args.output_file:
        export_type_names = {
            "selected": "selected_parameters.xlsx",
            "max": "max_values.xlsx",
            "complete": "complete_data.xlsx"
        }
        args.output_file = export_type_names[args.export]
    
    # Initialize XML reader
    xml_reader = XmlDataReader(args.input_path)
    
    try:
        # List files if requested
        if args.list:
            print(f"Scanning directory: {args.input_path}")
            xml_files = []
            for root, dirs, files in os.walk(args.input_path):
                for filename in files:
                    if filename.endswith(".xml"):
                        xml_files.append(os.path.join(root, filename))
            
            if xml_files:
                print(f"Found {len(xml_files)} XML files:")
                for xml_file in xml_files:
                    print(f"  - {xml_file}")
            else:
                print("No XML files found in the specified directory.")
            return
        
        # Extract data
        if args.verbose:
            print(f"Extracting data from XML files in: {args.input_path}")
        
        extracted_data = xml_reader.extract_id_and_parameters()
        
        if not extracted_data:
            print("No XML files found or no data could be extracted.")
            sys.exit(1)
        
        if args.verbose:
            print(f"Successfully extracted data from {len(extracted_data)} files")
            for data in extracted_data:
                print(f"  - {data['filename']} (Subject: {data['subject_id']})")
        
        # Export data based on selected option
        exporter = ExcelExporter(args.output_file)
        
        if args.export == "selected":
            if args.verbose:
                print(f"Exporting selected parameters to: {args.output_file}")
            exporter.export_selected_parameters(extracted_data)
            print(f"✓ Selected parameters exported to: {args.output_file}")
            print("  Contains: 15 key parameters including VO2/kg at MFO, AT, RC, and Max")
            
        elif args.export == "max":
            if args.verbose:
                print(f"Exporting max values to: {args.output_file}")
            exporter.export_max_values_only(extracted_data)
            print(f"✓ Max values exported to: {args.output_file}")
            print("  Contains: Maximum values for all parameters")
            
        elif args.export == "complete":
            if args.verbose:
                print(f"Exporting complete data to: {args.output_file}")
            exporter.export_extracted_xml_data(extracted_data)
            print(f"✓ Complete data exported to: {args.output_file}")
            print("  Contains: All measurement phases for all parameters")
        
        if args.verbose:
            print(f"Export completed successfully!")
            print(f"Data from {len(extracted_data)} subjects exported with proper formatting.")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()