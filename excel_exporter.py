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
        Uses ExportManager for modular data processing
        
        Args:
            extracted_data: List of extracted XML data from xml_data_reader
        """
        try:
            self.error_handler.log_info(f"Starting selected parameters export to {self.file_path}", "export_selected_parameters")
            
            if not extracted_data:
                raise ValueError("No data provided for export")
            
            # Use ExportManager's selected parameters list and logic
            selected_params = self.export_manager.SELECTED_PARAMETERS
            
            rows = []
            for file_data in extracted_data:
                row = {
                    'Filename': file_data['filename'],
                    'Subject ID': file_data['subject_id']
                }
                
                # Add selected parameters for specific phases
                for param in file_data['parameters']:
                    param_name = param['Name']
                    unit = param['UM']
                    
                    if param_name in selected_params:
                        base_name = f"{param_name} ({unit})" if unit and unit != "---" else param_name
                        
                        # Define phases for each parameter based on requirements
                        if param_name == 'VO2/kg':
                            # VO2/kg needs MFO, AT, RC, and Max phases
                            phases = ['MFO', 'AT', 'RC', 'Max']
                        else:
                            # All other parameters only need Max phase
                            phases = ['Max']
                        
                        for phase in phases:
                            if param.get(phase) is not None:
                                row[f"{base_name}_{phase}"] = param[phase]
                
                rows.append(row)
            
            # Save with formatting using the modular excel formatter
            self._save_formatted_excel(rows, extracted_data, "Selected Parameters")
            
            self.error_handler.log_info(f"Successfully exported {len(extracted_data)} records with selected parameters", "export_selected_parameters")
            
        except Exception as e:
            self.error_handler.handle_exception(e, "export_selected_parameters", "export_error")
            raise

    def export_max_values_only(self, extracted_data: List[Dict[str, Any]]) -> None:
        """
        Export only maximum values to Excel
        Uses modular approach for consistency
        
        Args:
            extracted_data: List of extracted XML data from xml_data_reader
        """
        try:
            self.error_handler.log_info(f"Starting max values export to {self.file_path}", "export_max_values_only")
            
            if not extracted_data:
                raise ValueError("No data provided for export")
            
            # Create max values rows using modular logic
            rows = []
            for file_data in extracted_data:
                row = {
                    'Filename': file_data['filename'],
                    'Subject ID': file_data['subject_id']
                }
                
                # Add max values for all parameters
                for param in file_data['parameters']:
                    param_name = param['Name']
                    unit = param['UM']
                    max_value = param.get('Max')
                    
                    if max_value is not None and max_value != '':
                        if unit and unit != "---":
                            column_name = f"{param_name} ({unit})"
                        else:
                            column_name = param_name
                        row[column_name] = max_value
                
                rows.append(row)
            
            # Save with formatting using modular formatter
            self._save_formatted_excel(rows, extracted_data, "Max Values Only")
            
            self.error_handler.log_info(f"Successfully exported {len(extracted_data)} records with max values", "export_max_values_only")
            
        except Exception as e:
            self.error_handler.handle_exception(e, "export_max_values_only", "export_error")
            raise

    def export_extracted_xml_data(self, extracted_data: List[Dict[str, Any]]) -> None:
        """
        Export complete extracted XML data to Excel
        Uses modular approach for complete dataset export
        
        Args:
            extracted_data: List of extracted XML data from xml_data_reader
        """
        try:
            self.error_handler.log_info(f"Starting complete dataset export to {self.file_path}", "export_extracted_xml_data")
            
            if not extracted_data:
                raise ValueError("No data provided for export")
            
            # Create complete dataset rows using modular logic
            rows = []
            for file_data in extracted_data:
                # Start with basic file information
                row = {
                    'Filename': file_data['filename'],
                    'Subject ID': file_data['subject_id'],
                    'File Path': file_data['file_path']
                }
                
                # Add all parameters as columns
                for param in file_data['parameters']:
                    param_name = param['Name']
                    unit = param['UM']
                    
                    # Create column names with units
                    base_col_name = f"{param_name}" if not unit or unit == "---" else f"{param_name} ({unit})"
                    
                    # Add all measurement phases
                    phases = ['Value', 'Rest', 'Warmup', 'MFO', 'AT', 'RC', 'Max', 'Pred', 'PercPred', 'Normal', 'Class']
                    for phase in phases:
                        row[f"{base_col_name}_{phase}"] = param.get(phase)
                
                rows.append(row)
            
            # Save with formatting using modular formatter
            self._save_formatted_excel(rows, extracted_data, "Complete Dataset")
            
            self.error_handler.log_info(f"Successfully exported {len(extracted_data)} records with complete dataset", "export_extracted_xml_data")
            
        except Exception as e:
            self.error_handler.handle_exception(e, "export_extracted_xml_data", "export_error")
            raise

    def _save_formatted_excel(self, rows: List[Dict[str, Any]], raw_data: List[Dict[str, Any]], sheet_name: str) -> None:
        """Save rows to Excel with professional formatting using modular formatter"""
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Use modular excel formatter to save with formatting
        with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
            # Write main data
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get workbook for formatting
            workbook = writer.book
            worksheet = workbook[sheet_name]
            
            # Apply professional formatting using modular formatter
            self.excel_formatter.apply_excel_formatting(workbook, sheet_name)
            
            # Add summary sheet using modular formatter
            self.excel_formatter.create_summary_sheet(workbook, raw_data)

    # Additional convenience methods
    
    def get_export_preview(self, extracted_data: List[Dict[str, Any]], export_type: str = "selected", max_rows: int = 5) -> Dict[str, Any]:
        """
        Get preview of export data without saving
        Uses modular approach for consistency
        
        Args:
            extracted_data: Extracted data to preview
            export_type: Type of export ("selected", "max", "complete")
            max_rows: Maximum rows to preview
            
        Returns:
            Preview information dictionary
        """
        try:
            if export_type == "selected":
                # Use same logic as export_selected_parameters
                selected_params = self.export_manager.SELECTED_PARAMETERS
                rows = []
                
                for file_data in extracted_data[:max_rows]:
                    row = {
                        'Filename': file_data['filename'],
                        'Subject ID': file_data['subject_id']
                    }
                    
                    for param in file_data['parameters']:
                        param_name = param['Name']
                        unit = param['UM']
                        
                        if param_name in selected_params:
                            base_name = f"{param_name} ({unit})" if unit and unit != "---" else param_name
                            
                            if param_name == 'VO2/kg':
                                phases = ['MFO', 'AT', 'RC', 'Max']
                            else:
                                phases = ['Max']
                            
                            for phase in phases:
                                if param.get(phase) is not None:
                                    row[f"{base_name}_{phase}"] = param[phase]
                    
                    rows.append(row)
                    
            elif export_type == "max":
                # Max values preview
                rows = []
                for file_data in extracted_data[:max_rows]:
                    row = {
                        'Filename': file_data['filename'],
                        'Subject ID': file_data['subject_id']
                    }
                    
                    for param in file_data['parameters']:
                        param_name = param['Name']
                        unit = param['UM']
                        max_value = param.get('Max')
                        
                        if max_value is not None and max_value != '':
                            if unit and unit != "---":
                                column_name = f"{param_name} ({unit})"
                            else:
                                column_name = param_name
                            row[column_name] = max_value
                    
                    rows.append(row)
            else:
                # Complete dataset preview
                rows = []
                for file_data in extracted_data[:max_rows]:
                    row = {
                        'Filename': file_data['filename'],
                        'Subject ID': file_data['subject_id'],
                        'File Path': file_data['file_path']
                    }
                    
                    for param in file_data['parameters']:
                        param_name = param['Name']
                        unit = param['UM']
                        base_col_name = f"{param_name}" if not unit or unit == "---" else f"{param_name} ({unit})"
                        
                        phases = ['Value', 'Rest', 'Warmup', 'MFO', 'AT', 'RC', 'Max', 'Pred', 'PercPred', 'Normal', 'Class']
                        for phase in phases:
                            row[f"{base_col_name}_{phase}"] = param.get(phase)
                    
                    rows.append(row)
            
            if rows:
                df = pd.DataFrame(rows)
                
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
