"""
Export Manager Module
Manages different export operations and formats
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from .data_extractor import DataExtractor
from .excel_formatter import ExcelFormatter
from ..utils.path_validator import PathValidator

class ExportManager:
    """Manages data export operations"""
    
    # Standard selected parameters for COSMED analysis (15 key parameters)
    SELECTED_PARAMETERS = [
        "t",                    # Time in seconds
        "Speed",               # Speed in Km/h
        "Pace",                # Pace in mm:ss/km
        "VO2",                 # VO2 in mL/min
        "VO2/kg",              # VO2/kg in mL/min/Kg
        "VCO2",                # VCO2 in mL/min
        "METS",                # Metabolic equivalents
        "RQ",                  # Respiratory quotient
        "VE",                  # Ventilation in L/min
        "Rf",                  # Respiratory frequency in 1/min
        "HR",                  # Heart rate in bpm
        "VO2/HR"               # Oxygen pulse in mL/beat
    ]
    
    def __init__(self):
        self.data_extractor = DataExtractor()
        self.excel_formatter = ExcelFormatter()
        self.path_validator = PathValidator()
    
    def export_selected_parameters(self, input_directory: str, output_file: str) -> Dict[str, Any]:
        """
        Export selected parameters to Excel
        
        Args:
            input_directory: Directory containing XML files
            output_file: Output Excel file path
            
        Returns:
            Export result dictionary
        """
        try:
            # Validate paths
            validated_dir = self.path_validator.validate_directory(input_directory)
            validated_output = self.path_validator.validate_file_path(output_file)
            
            # Extract ALL data first (this method works correctly)
            extracted_data = self.data_extractor.extract_from_directory(validated_dir)
            
            if not extracted_data:
                return {
                    'success': False,
                    'error': 'No data could be extracted from XML files',
                    'files_processed': 0
                }
            
            # Create DataFrame with selected parameters format
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
                    
                    if param_name in self.SELECTED_PARAMETERS:
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
            
            # Save to Excel
            df = pd.DataFrame(rows)
            self._save_with_formatting(df, validated_output, extracted_data, "Selected Parameters")
            
            return {
                'success': True,
                'files_processed': len(extracted_data),
                'output_file': validated_output,
                'parameters_included': self.SELECTED_PARAMETERS
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'files_processed': 0
            }
    
    def export_max_values_only(self, input_directory: str, output_file: str) -> Dict[str, Any]:
        """
        Export only maximum values to Excel
        
        Args:
            input_directory: Directory containing XML files
            output_file: Output Excel file path
            
        Returns:
            Export result dictionary
        """
        try:
            # Validate paths
            validated_dir = self.path_validator.validate_directory(input_directory)
            validated_output = self.path_validator.validate_file_path(output_file)
            
            # Extract max values
            max_data = self.data_extractor.extract_max_values_only(validated_dir)
            
            if not max_data:
                return {
                    'success': False,
                    'error': 'No data could be extracted from XML files',
                    'files_processed': 0
                }
            
            # Create DataFrame
            rows = []
            for file_data in max_data:
                row = {
                    'Filename': file_data['filename'],
                    'Subject ID': file_data['subject_id']
                }
                row.update(file_data['max_parameters'])
                rows.append(row)
            
            df = pd.DataFrame(rows)
            self._save_with_formatting(df, validated_output, max_data, "Max Values Only")
            
            return {
                'success': True,
                'files_processed': len(max_data),
                'output_file': validated_output,
                'export_type': 'max_values'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'files_processed': 0
            }
    
    def export_complete_dataset(self, input_directory: str, output_file: str) -> Dict[str, Any]:
        """
        Export complete dataset to Excel
        
        Args:
            input_directory: Directory containing XML files
            output_file: Output Excel file path
            
        Returns:
            Export result dictionary
        """
        try:
            # Validate paths
            validated_dir = self.path_validator.validate_directory(input_directory)
            validated_output = self.path_validator.validate_file_path(output_file)
            
            # Extract all data
            extracted_data = self.data_extractor.extract_from_directory(validated_dir)
            
            if not extracted_data:
                return {
                    'success': False,
                    'error': 'No data could be extracted from XML files',
                    'files_processed': 0
                }
            
            # Create complete DataFrame
            df = self.excel_formatter.create_formatted_dataframe(extracted_data, "complete")
            self._save_with_formatting(df, validated_output, extracted_data, "Complete Dataset")
            
            return {
                'success': True,
                'files_processed': len(extracted_data),
                'output_file': validated_output,
                'export_type': 'complete'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'files_processed': 0
            }
    
    def export_custom_parameters(self, input_directory: str, output_file: str, parameter_names: List[str]) -> Dict[str, Any]:
        """
        Export custom selection of parameters
        
        Args:
            input_directory: Directory containing XML files
            output_file: Output Excel file path
            parameter_names: List of parameter names to include
            
        Returns:
            Export result dictionary
        """
        try:
            # Validate paths
            validated_dir = self.path_validator.validate_directory(input_directory)
            validated_output = self.path_validator.validate_file_path(output_file)
            
            # Extract selected parameters
            extracted_data = self.data_extractor.extract_selected_parameters(
                validated_dir, 
                parameter_names
            )
            
            if not extracted_data:
                return {
                    'success': False,
                    'error': 'No data could be extracted from XML files',
                    'files_processed': 0
                }
            
            # Create DataFrame
            df = self.excel_formatter.create_formatted_dataframe(extracted_data, "selected")
            self._save_with_formatting(df, validated_output, extracted_data, f"Custom Parameters ({len(parameter_names)})")
            
            return {
                'success': True,
                'files_processed': len(extracted_data),
                'output_file': validated_output,
                'parameters_included': parameter_names
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'files_processed': 0
            }
    
    def _save_with_formatting(self, df: pd.DataFrame, output_file: str, raw_data: List[Dict], sheet_name: str) -> None:
        """
        Save DataFrame with professional formatting
        
        Args:
            df: DataFrame to save
            output_file: Output file path
            raw_data: Raw extracted data for summary
            sheet_name: Name for the main data sheet
        """
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Write main data
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get workbook for formatting
            workbook = writer.book
            worksheet = workbook[sheet_name]
            
            # Apply formatting
            self.excel_formatter.apply_excel_formatting(workbook, sheet_name)
            
            # Add summary sheet
            self.excel_formatter.create_summary_sheet(workbook, raw_data)
    
    def get_available_parameters(self, input_directory: str) -> Dict[str, Any]:
        """
        Get list of available parameters in XML files
        
        Args:
            input_directory: Directory containing XML files
            
        Returns:
            Dictionary with parameter information
        """
        try:
            validated_dir = self.path_validator.validate_directory(input_directory)
            summary = self.data_extractor.get_extraction_summary(validated_dir)
            
            return {
                'success': True,
                'unique_parameters': summary.get('unique_parameters', []),
                'total_files': summary.get('total_xml_files', 0),
                'extractable_files': summary.get('extractable_files', 0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'unique_parameters': []
            }
    
    def validate_export_requirements(self, input_directory: str, export_type: str) -> Dict[str, Any]:
        """
        Validate that export requirements can be met
        
        Args:
            input_directory: Directory containing XML files
            export_type: Type of export ("selected", "max", "complete")
            
        Returns:
            Validation result dictionary
        """
        try:
            validated_dir = self.path_validator.validate_directory(input_directory)
            
            if export_type == "selected":
                # Check if selected parameters are available
                validation = self.data_extractor.validate_parameter_availability(
                    validated_dir, 
                    self.SELECTED_PARAMETERS
                )
                
                return {
                    'success': True,
                    'export_type': export_type,
                    'required_parameters': self.SELECTED_PARAMETERS,
                    'missing_parameters': validation['missing_parameters'],
                    'parameter_coverage': validation['parameter_coverage'],
                    'files_analyzed': validation['files_analyzed']
                }
            else:
                # For max and complete exports, just check basic extraction capability
                summary = self.data_extractor.get_extraction_summary(validated_dir)
                
                return {
                    'success': True,
                    'export_type': export_type,
                    'extractable_files': summary['extractable_files'],
                    'total_files': summary['total_xml_files'],
                    'unique_parameters': len(summary['unique_parameters'])
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'export_type': export_type
            }
    
    def get_export_preview(self, input_directory: str, export_type: str, max_files: int = 3) -> Dict[str, Any]:
        """
        Get preview of export data without creating full export
        
        Args:
            input_directory: Directory containing XML files
            export_type: Type of export
            max_files: Maximum number of files to preview
            
        Returns:
            Preview data dictionary
        """
        try:
            validated_dir = self.path_validator.validate_directory(input_directory)
            
            # Get limited data for preview
            if export_type == "selected":
                preview_data = self.data_extractor.extract_selected_parameters(
                    validated_dir, 
                    self.SELECTED_PARAMETERS
                )[:max_files]
                df = self.excel_formatter.create_formatted_dataframe(preview_data, "selected")
            elif export_type == "max":
                preview_data = self.data_extractor.extract_max_values_only(validated_dir)[:max_files]
                df = self.excel_formatter.create_formatted_dataframe(preview_data, "max")
            else:
                preview_data = self.data_extractor.extract_from_directory(validated_dir)[:max_files]
                df = self.excel_formatter.create_formatted_dataframe(preview_data, "complete")
            
            return {
                'success': True,
                'preview_rows': len(df),
                'preview_columns': list(df.columns),
                'sample_data': df.head().to_dict('records'),
                'total_files_available': len(preview_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'preview_rows': 0
            }
