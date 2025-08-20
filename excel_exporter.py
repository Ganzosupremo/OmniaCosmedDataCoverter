"""
Refactored Excel Exporter using modular architecture
"""
import pandas as pd
from typing import List, Dict, Any
from modules import ExportManager, ExcelFormatter, ErrorHandler, PathValidator

class ExcelExporter:
    """
    Main Excel Exporter class using modular architecture
    Maintains compatibility with existing code while using new modules internally
    """
    
    def __init__(self, file_path: str):
        """
        Initialize Excel Exporter
        
        Args:
            file_path: Output Excel file path
        """
        self.file_path = file_path
        
        # Initialize modules
        self.export_manager = ExportManager()
        self.excel_formatter = ExcelFormatter()
        self.error_handler = ErrorHandler()
        self.path_validator = PathValidator()
        
        # Validate output file path
        try:
            self.file_path = self.path_validator.validate_file_path(file_path)
        except ValueError as e:
            self.error_handler.handle_exception(e, "ExcelExporter.__init__", "path_validation")
            raise

    def export_selected_parameters(self, extracted_data: List[Dict[str, Any]]) -> None:
        """
        Export selected parameters to Excel (15 key parameters)
        
        Args:
            extracted_data: List of extracted XML data from xml_data_reader
        """
        try:
            self.error_handler.log_info(f"Starting selected parameters export to {self.file_path}", "export_selected_parameters")
            
            if not extracted_data:
                raise ValueError("No data provided for export")
            
            # Use the ExcelFormatter to create DataFrame with selected parameters
            df = self.excel_formatter.create_formatted_dataframe(extracted_data, "selected")
            
            # Save with formatting using the Excel formatter
            self.excel_formatter.save_formatted_excel(extracted_data, self.file_path, "selected")
            
            self.error_handler.log_info(f"Successfully exported {len(extracted_data)} records with selected parameters", "export_selected_parameters")
            
        except Exception as e:
            self.error_handler.handle_exception(e, "export_selected_parameters", "export_error")
            raise

    def export_max_values_only(self, extracted_data: List[Dict[str, Any]]) -> None:
        """
        Export only maximum values to Excel
        
        Args:
            extracted_data: List of extracted XML data from xml_data_reader
        """
        try:
            self.error_handler.log_info(f"Starting max values export to {self.file_path}", "export_max_values_only")
            
            if not extracted_data:
                raise ValueError("No data provided for export")
            
            # Use the ExcelFormatter to create DataFrame with max values
            df = self.excel_formatter.create_formatted_dataframe(extracted_data, "max")
            
            # Save with formatting using the Excel formatter
            self.excel_formatter.save_formatted_excel(extracted_data, self.file_path, "max")
            
            self.error_handler.log_info(f"Successfully exported {len(extracted_data)} records with max values", "export_max_values_only")
            
        except Exception as e:
            self.error_handler.handle_exception(e, "export_max_values_only", "export_error")
            raise

    def export_extracted_xml_data(self, extracted_data: List[Dict[str, Any]]) -> None:
        """
        Export complete extracted XML data to Excel
        
        Args:
            extracted_data: List of extracted XML data from xml_data_reader
        """
        try:
            self.error_handler.log_info(f"Starting complete dataset export to {self.file_path}", "export_extracted_xml_data")
            
            if not extracted_data:
                raise ValueError("No data provided for export")
            
            # Use the ExcelFormatter to create DataFrame with complete data
            df = self.excel_formatter.create_formatted_dataframe(extracted_data, "complete")
            
            # Save with formatting using the Excel formatter
            self.excel_formatter.save_formatted_excel(extracted_data, self.file_path, "complete")
            
            self.error_handler.log_info(f"Successfully exported {len(extracted_data)} records with complete dataset", "export_extracted_xml_data")
            
        except Exception as e:
            self.error_handler.handle_exception(e, "export_extracted_xml_data", "export_error")
            raise

    def get_export_preview(self, extracted_data: List[Dict[str, Any]], export_type: str = "selected", max_rows: int = 5) -> Dict[str, Any]:
        """
        Get preview of export data without saving
        
        Args:
            extracted_data: Extracted data to preview
            export_type: Type of export ("selected", "max", "complete")
            max_rows: Maximum rows to preview
            
        Returns:
            Preview information dictionary
        """
        try:
            # Use the ExcelFormatter to create a preview DataFrame
            preview_data = extracted_data[:max_rows] if len(extracted_data) > max_rows else extracted_data
            df = self.excel_formatter.create_formatted_dataframe(preview_data, export_type)
            
            if not df.empty:
                return {
                    'preview_rows': len(df),
                    'total_columns': len(df.columns),
                    'column_names': list(df.columns),
                    'sample_data': df.head(3).to_dict('records'),
                    'export_type': export_type
                }
            else:
                return {
                    'preview_rows': 0,
                    'total_columns': 0,
                    'column_names': [],
                    'sample_data': [],
                    'export_type': export_type
                }
                
        except Exception as e:
            self.error_handler.handle_exception(e, "get_export_preview", "preview_error")
            return {
                'error': str(e),
                'preview_rows': 0,
                'export_type': export_type
            }
