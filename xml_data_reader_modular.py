"""
Refactored XML Data Reader using modular architecture
"""
from typing import List, Dict, Any, Optional
from modules import DataExtractor, PathValidator, FileScanner, ErrorHandler

class XmlDataReader:
    """
    Main XML Data Reader class using modular architecture
    Maintains compatibility with existing code while using new modules internally
    """
    
    def __init__(self, dir_path: str = None):
        """
        Initialize XML Data Reader
        
        Args:
            dir_path: Directory path containing XML files
        """
        self.dir_path: Optional[str] = dir_path
        
        # Initialize modules
        self.data_extractor = DataExtractor()
        self.path_validator = PathValidator()
        self.file_scanner = FileScanner()
        self.error_handler = ErrorHandler()
        
        # Validate directory if provided
        if self.dir_path:
            try:
                self.dir_path = self.path_validator.validate_directory(self.dir_path)
            except ValueError as e:
                self.error_handler.handle_exception(e, "XmlDataReader.__init__", "validation_error")
                raise
    
    def read_data(self) -> List[Dict[str, Any]]:
        """
        Read XML data from files (legacy method for compatibility)
        
        Returns:
            List of dictionaries with file_path and root_element
        """
        if not self.dir_path:
            raise ValueError("Directory path must be provided.")
        
        try:
            # Get all XML files
            xml_files = self.file_scanner.find_xml_files(self.dir_path)
            
            xml_files_data = []
            for file_path in xml_files:
                # Parse XML file using xml_parser module
                root = self.data_extractor.xml_parser.parse_file(file_path)
                if root is not None:
                    xml_files_data.append({
                        'file_path': file_path,
                        'root_element': root
                    })
                else:
                    error_msg = f"Failed to parse XML file: {file_path}"
                    self.error_handler.log_warning(error_msg, "read_data")
                    raise ValueError(error_msg)
            
            return xml_files_data
            
        except Exception as e:
            self.error_handler.handle_exception(e, "read_data", "file_processing")
            raise
    
    def extract_id_and_parameters(self) -> List[Dict[str, Any]]:
        """
        Extract ID and all parameters with their values from XML files
        
        Returns:
            List of dictionaries containing extracted data for each XML file
        """
        if not self.dir_path:
            raise ValueError("Directory path must be provided.")
        
        try:
            self.error_handler.log_info(f"Starting extraction from directory: {self.dir_path}", "extract_id_and_parameters")
            
            # Use the data extractor module
            extracted_data = self.data_extractor.extract_from_directory(self.dir_path)
            
            # Log success
            self.error_handler.log_info(f"Successfully extracted data from {len(extracted_data)} files", "extract_id_and_parameters")
            
            return extracted_data
            
        except Exception as e:
            self.error_handler.handle_exception(e, "extract_id_and_parameters", "extraction_error")
            raise
    
    def get_file_summary(self) -> Dict[str, Any]:
        """
        Get summary information about XML files in directory
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.dir_path:
            raise ValueError("Directory path must be provided.")
        
        try:
            return self.data_extractor.get_extraction_summary(self.dir_path)
        except Exception as e:
            self.error_handler.handle_exception(e, "get_file_summary", "summary_error")
            raise
    
    def validate_files(self) -> Dict[str, Any]:
        """
        Validate all XML files in directory
        
        Returns:
            Validation report dictionary
        """
        if not self.dir_path:
            raise ValueError("Directory path must be provided.")
        
        try:
            # Get directory scan summary
            scan_summary = self.file_scanner.scan_directory_summary(self.dir_path)
            
            # Check file accessibility
            accessibility = self.file_scanner.validate_files_accessible(scan_summary['xml_files'])
            
            return {
                'directory': self.dir_path,
                'total_xml_files': scan_summary['xml_count'],
                'total_size': scan_summary['total_size'],
                'accessible_files': accessibility['accessible_count'],
                'inaccessible_files': accessibility['inaccessible_count'],
                'validation_success': accessibility['inaccessible_count'] == 0,
                'scan_errors': scan_summary.get('scan_error'),
                'file_details': accessibility
            }
            
        except Exception as e:
            self.error_handler.handle_exception(e, "validate_files", "validation_error")
            raise
    
    def get_available_parameters(self) -> List[str]:
        """
        Get list of all unique parameter names available in XML files
        
        Returns:
            List of unique parameter names
        """
        if not self.dir_path:
            raise ValueError("Directory path must be provided.")
        
        try:
            summary = self.data_extractor.get_extraction_summary(self.dir_path)
            return summary.get('unique_parameters', [])
        except Exception as e:
            self.error_handler.handle_exception(e, "get_available_parameters", "parameter_discovery")
            raise
    
    def extract_custom_parameters(self, parameter_names: List[str]) -> List[Dict[str, Any]]:
        """
        Extract specific parameters from XML files
        
        Args:
            parameter_names: List of parameter names to extract
            
        Returns:
            List of extracted data with only specified parameters
        """
        if not self.dir_path:
            raise ValueError("Directory path must be provided.")
        
        try:
            self.error_handler.log_info(f"Extracting custom parameters: {parameter_names}", "extract_custom_parameters")
            
            extracted_data = self.data_extractor.extract_selected_parameters(self.dir_path, parameter_names)
            
            self.error_handler.log_info(f"Successfully extracted {len(parameter_names)} parameters from {len(extracted_data)} files", "extract_custom_parameters")
            
            return extracted_data
            
        except Exception as e:
            self.error_handler.handle_exception(e, "extract_custom_parameters", "custom_extraction")
            raise
    
    def _validate_directory_path(self):
        """Legacy method for backward compatibility"""
        if not self.dir_path:
            raise ValueError("Folder path must be provided.")
        
        try:
            self.dir_path = self.path_validator.validate_directory(self.dir_path)
        except ValueError as e:
            self.error_handler.handle_exception(e, "_validate_directory_path", "path_validation")
            raise
