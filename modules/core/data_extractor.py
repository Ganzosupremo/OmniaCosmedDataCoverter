"""
Data Extractor Module
Handles extraction of COSMED data from XML files
"""
import os
from typing import List, Dict, Any, Optional
from .xml_parser import XmlParser
from ..utils.file_scanner import FileScanner
from ..utils.path_validator import PathValidator

class DataExtractor:
    """Extracts COSMED data from XML files"""
    
    def __init__(self):
        self.xml_parser = XmlParser()
        self.file_scanner = FileScanner()
        self.path_validator = PathValidator()
    
    def extract_from_directory(self, directory: str) -> List[Dict[str, Any]]:
        """
        Extract data from all XML files in directory
        
        Args:
            directory: Directory containing XML files
            
        Returns:
            List of extracted data dictionaries
        """
        validated_dir = self.path_validator.validate_directory(directory)
        xml_files = self.file_scanner.find_xml_files(validated_dir)
        
        extracted_data = []
        
        for file_path in xml_files:
            file_data = self.extract_from_file(file_path)
            if file_data is not None:
                extracted_data.append(file_data)
        
        return extracted_data
    
    def extract_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract data from single XML file
        
        Args:
            file_path: Path to XML file
            
        Returns:
            Extracted data dictionary or None if extraction fails
        """
        validated_path = self.path_validator.validate_file_path(file_path, must_exist=True)
        
        # Parse XML
        root = self.xml_parser.parse_file(validated_path)
        if root is None:
            return None
        
        # Validate COSMED structure
        if not self.xml_parser.validate_cosmed_structure(root):
            return None
        
        # Extract basic info
        filename = os.path.basename(validated_path)
        subject_id = self.xml_parser.extract_subject_id(root)
        
        # Extract parameters
        parameters = self._extract_parameters(root)
        
        return {
            'file_path': validated_path,
            'filename': filename,
            'subject_id': subject_id,
            'parameters': parameters,
            'parameter_count': len(parameters),
            'extraction_success': True
        }
    
    def _extract_parameters(self, root) -> List[Dict[str, Any]]:
        """
        Extract all parameters from XML root
        
        Args:
            root: XML root element
            
        Returns:
            List of parameter dictionaries
        """
        parameters = []
        
        parameters_section = self.xml_parser.extract_parameters_section(root)
        if parameters_section is not None:
            for param_element in parameters_section.findall("Parameter"):
                param_data = self.xml_parser.parse_parameter_element(param_element)
                parameters.append(param_data)
        
        return parameters
    
    def extract_selected_parameters(self, directory: str, parameter_names: List[str]) -> List[Dict[str, Any]]:
        """
        Extract only specified parameters from XML files
        
        Args:
            directory: Directory containing XML files
            parameter_names: List of parameter names to extract
            
        Returns:
            List of extracted data with only selected parameters
        """
        all_data = self.extract_from_directory(directory)
        
        # Filter parameters for each file
        filtered_data = []
        for file_data in all_data:
            filtered_params = []
            for param in file_data['parameters']:
                if param['Name'] in parameter_names:
                    filtered_params.append(param)
            
            filtered_file_data = file_data.copy()
            filtered_file_data['parameters'] = filtered_params
            filtered_file_data['parameter_count'] = len(filtered_params)
            filtered_data.append(filtered_file_data)
        
        return filtered_data
    
    def extract_max_values_only(self, directory: str) -> List[Dict[str, Any]]:
        """
        Extract only Max values from parameters
        
        Args:
            directory: Directory containing XML files
            
        Returns:
            List of data with only Max values
        """
        all_data = self.extract_from_directory(directory)
        
        # Create simplified data structure with only Max values
        max_data = []
        for file_data in all_data:
            max_params = {}
            
            for param in file_data['parameters']:
                param_name = param['Name']
                unit = param['UM']
                max_value = param['Max']
                
                if max_value is not None and max_value != '':
                    # Create descriptive parameter name
                    if unit and unit != '---':
                        key = f"{param_name} ({unit})"
                    else:
                        key = param_name
                    
                    max_params[key] = max_value
            
            max_file_data = {
                'file_path': file_data['file_path'],
                'filename': file_data['filename'],
                'subject_id': file_data['subject_id'],
                'max_parameters': max_params,
                'parameter_count': len(max_params),
                'extraction_success': True
            }
            max_data.append(max_file_data)
        
        return max_data
    
    def get_extraction_summary(self, directory: str) -> Dict[str, Any]:
        """
        Get summary of extraction capabilities for directory
        
        Args:
            directory: Directory to analyze
            
        Returns:
            Summary dictionary with extraction statistics
        """
        validated_dir = self.path_validator.validate_directory(directory)
        
        summary = {
            'directory': validated_dir,
            'total_xml_files': 0,
            'extractable_files': 0,
            'failed_files': 0,
            'total_parameters': 0,
            'unique_parameters': set(),
            'subjects_found': 0,
            'files_with_subjects': 0,
            'extraction_errors': []
        }
        
        try:
            xml_files = self.file_scanner.find_xml_files(validated_dir)
            summary['total_xml_files'] = len(xml_files)
            
            subjects_found = set()
            
            for file_path in xml_files:
                try:
                    file_data = self.extract_from_file(file_path)
                    if file_data is not None:
                        summary['extractable_files'] += 1
                        summary['total_parameters'] += file_data['parameter_count']
                        
                        # Track unique parameter names
                        for param in file_data['parameters']:
                            if param['Name']:
                                summary['unique_parameters'].add(param['Name'])
                        
                        # Track subjects
                        if file_data['subject_id']:
                            subjects_found.add(file_data['subject_id'])
                            summary['files_with_subjects'] += 1
                    else:
                        summary['failed_files'] += 1
                        
                except Exception as e:
                    summary['failed_files'] += 1
                    summary['extraction_errors'].append({
                        'file': file_path,
                        'error': str(e)
                    })
            
            summary['subjects_found'] = len(subjects_found)
            summary['unique_parameters'] = list(summary['unique_parameters'])
            
        except Exception as e:
            summary['extraction_errors'].append({
                'file': 'directory_scan',
                'error': str(e)
            })
        
        return summary
    
    def validate_parameter_availability(self, directory: str, required_parameters: List[str]) -> Dict[str, Any]:
        """
        Validate that required parameters are available in the XML files
        
        Args:
            directory: Directory containing XML files
            required_parameters: List of required parameter names
            
        Returns:
            Validation report dictionary
        """
        all_data = self.extract_from_directory(directory)
        
        report = {
            'required_parameters': required_parameters,
            'available_parameters': set(),
            'missing_parameters': set(),
            'files_analyzed': len(all_data),
            'parameter_coverage': {}  # parameter_name: count_of_files_with_parameter
        }
        
        # Initialize coverage counters
        for param_name in required_parameters:
            report['parameter_coverage'][param_name] = 0
        
        # Analyze each file
        for file_data in all_data:
            file_param_names = {param['Name'] for param in file_data['parameters'] if param['Name']}
            report['available_parameters'].update(file_param_names)
            
            # Count coverage for required parameters
            for param_name in required_parameters:
                if param_name in file_param_names:
                    report['parameter_coverage'][param_name] += 1
        
        # Determine missing parameters
        report['missing_parameters'] = set(required_parameters) - report['available_parameters']
        report['available_parameters'] = list(report['available_parameters'])
        report['missing_parameters'] = list(report['missing_parameters'])
        
        return report
