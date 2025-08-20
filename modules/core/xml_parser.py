"""
XML Parser Module
Handles XML parsing operations for COSMED data files
"""
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
import logging

class XmlParser:
    """XML parsing utilities for COSMED data files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_file(self, file_path: str) -> Optional[ET.Element]:
        """
        Parse XML file and return root element
        
        Args:
            file_path: Path to XML file
            
        Returns:
            Root element or None if parsing fails
        """
        try:
            tree = ET.parse(file_path)
            return tree.getroot()
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error in {file_path}: {e}")
            return None
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {file_path}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error parsing {file_path}: {e}")
            return None
    
    def extract_subject_id(self, root: ET.Element) -> Optional[str]:
        """
        Extract subject ID from XML root element
        
        Args:
            root: XML root element
            
        Returns:
            Subject ID or None if not found
        """
        try:
            id_element = root.find(".//Subject/ID")
            if id_element is not None and id_element.text:
                return id_element.text.strip()
            return None
        except Exception as e:
            self.logger.error(f"Error extracting subject ID: {e}")
            return None
    
    def extract_parameters_section(self, root: ET.Element) -> Optional[ET.Element]:
        """
        Extract parameters section from XML root
        
        Args:
            root: XML root element
            
        Returns:
            Parameters section element or None if not found
        """
        try:
            return root.find(".//AdditionalData/Parameters")
        except Exception as e:
            self.logger.error(f"Error extracting parameters section: {e}")
            return None
    
    def parse_parameter_element(self, param_element: ET.Element) -> Dict[str, Any]:
        """
        Parse individual parameter element
        
        Args:
            param_element: Parameter XML element
            
        Returns:
            Dictionary containing parameter data
        """
        return {
            'Name': param_element.get('Name'),
            'UM': param_element.get('UM'),
            'Value': param_element.get('Value'),
            'Rest': param_element.get('Rest'),
            'Warmup': param_element.get('Warmup'),
            'MFO': param_element.get('MFO'),
            'AT': param_element.get('AT'),
            'RC': param_element.get('RC'),
            'Max': param_element.get('Max'),
            'Pred': param_element.get('Pred'),
            'PercPred': param_element.get('PercPred'),
            'Normal': param_element.get('Normal'),
            'Class': param_element.get('Class')
        }
    
    def validate_cosmed_structure(self, root: ET.Element) -> bool:
        """
        Validate that XML has expected COSMED structure
        
        Args:
            root: XML root element
            
        Returns:
            True if structure is valid
        """
        try:
            # Check for essential COSMED elements
            subject_section = root.find(".//Subject")
            params_section = root.find(".//AdditionalData/Parameters")
            
            if subject_section is None:
                self.logger.warning("Missing Subject section in XML")
                return False
                
            if params_section is None:
                self.logger.warning("Missing Parameters section in XML")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating COSMED structure: {e}")
            return False
    
    def get_xml_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic information about XML file
        
        Args:
            file_path: Path to XML file
            
        Returns:
            Dictionary with XML file information
        """
        info = {
            'file_path': file_path,
            'is_valid': False,
            'subject_id': None,
            'parameter_count': 0,
            'has_cosmed_structure': False,
            'error': None
        }
        
        try:
            root = self.parse_file(file_path)
            if root is not None:
                info['is_valid'] = True
                info['subject_id'] = self.extract_subject_id(root)
                info['has_cosmed_structure'] = self.validate_cosmed_structure(root)
                
                # Count parameters
                params_section = self.extract_parameters_section(root)
                if params_section is not None:
                    info['parameter_count'] = len(params_section.findall("Parameter"))
                    
        except Exception as e:
            info['error'] = str(e)
            
        return info
