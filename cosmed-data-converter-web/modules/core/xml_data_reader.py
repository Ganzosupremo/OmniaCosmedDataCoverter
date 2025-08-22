"""
XML Data Reader for COSMED data processing
Simplified version for web deployment
"""
import os
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

class XmlDataReader:
    """Reads and processes COSMED XML data files"""
    
    def __init__(self, dir_path: Optional[str] = None):
        """Initialize XML Data Reader"""
        self.dir_path = None
        if dir_path:
            self.dir_path = os.path.abspath(dir_path)
            if not os.path.exists(self.dir_path):
                raise ValueError(f"Directory does not exist: {self.dir_path}")
            if not os.path.isdir(self.dir_path):
                raise ValueError(f"Path is not a directory: {self.dir_path}")
    
    def extract_id_and_parameters(self) -> List[Dict[str, Any]]:
        """Extract ID and all parameters from XML files"""
        if not self.dir_path:
            return []
        
        results = []
        xml_files = [f for f in os.listdir(self.dir_path) if f.lower().endswith('.xml')]
        
        for xml_file in xml_files:
            file_path = os.path.join(self.dir_path, xml_file)
            try:
                file_data = self._parse_xml_file(file_path)
                if file_data:
                    file_data['filename'] = xml_file
                    results.append(file_data)
            except Exception as e:
                print(f"Error processing {xml_file}: {e}")
                continue
        
        return results
    
    def _parse_xml_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse individual XML file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract Subject ID
            subject_id = None
            subject_elem = root.find('.//Subject')
            if subject_elem is not None:
                id_elem = subject_elem.find('ID')
                if id_elem is not None:
                    subject_id = id_elem.text
            
            # Extract Parameters
            parameters = []
            parameters_elem = root.find('.//Parameters')
            if parameters_elem is not None:
                for param in parameters_elem.findall('Parameter'):
                    param_data = {}
                    
                    # Get all attributes
                    for attr_name, attr_value in param.attrib.items():
                        param_data[attr_name] = attr_value
                    
                    if param_data.get('Name'):  # Only include parameters with names
                        parameters.append(param_data)
            
            return {
                'subject_id': subject_id,
                'parameters': parameters
            }
            
        except Exception as e:
            print(f"Error parsing XML file {file_path}: {e}")
            return None