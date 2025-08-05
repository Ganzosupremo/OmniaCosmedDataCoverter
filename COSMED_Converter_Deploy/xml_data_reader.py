import os
import xml.etree.ElementTree as ET

class XmlDataReader:
    def __init__(self, dir_path: str = None):
        self.dir_path: str = os.path.abspath(dir_path) if dir_path else None

    def _parse_xml_file(self, file_path: str) -> ET.Element | None:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            return root
        except ET.ParseError as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def read_data(self) -> list[dict]:
        self._validate_directory_path()

        xml_files_data: list[dict] = []
        for root, dirs, files in os.walk(self.dir_path):
            for filename in files:
                if filename.endswith(".xml"):
                    file_path: str = os.path.join(root, filename)
                    xml_data_root: ET.Element | None = self._parse_xml_file(file_path)
                    if xml_data_root is not None:
                        xml_files_data.append({
                            'file_path': file_path,
                            'root_element': xml_data_root
                        })
                    else:
                        raise ValueError(f"Failed to parse XML file: {file_path}")
        
        return xml_files_data

    def extract_id_and_parameters(self) -> list[dict]:
        """
        Extract ID and all parameters with their values up to Max from XML files.
        
        Returns:
            List of dictionaries containing extracted data for each XML file.
        """
        self._validate_directory_path()
        
        extracted_data: list[dict] = []
        
        for root, dirs, files in os.walk(self.dir_path):
            for filename in files:
                if filename.endswith(".xml"):
                    file_path: str = os.path.join(root, filename)
                    xml_data_root: ET.Element | None = self._parse_xml_file(file_path)
                    
                    if xml_data_root is not None:
                        # Extract ID from Subject element
                        subject_id = None
                        id_element = xml_data_root.find(".//Subject/ID")
                        if id_element is not None:
                            subject_id = id_element.text
                        
                        # Extract parameters
                        parameters = []
                        parameters_section = xml_data_root.find(".//AdditionalData/Parameters")
                        if parameters_section is not None:
                            for param in parameters_section.findall("Parameter"):
                                param_data = {
                                    'Name': param.get('Name'),
                                    'UM': param.get('UM'),
                                    'Value': param.get('Value'),
                                    'Rest': param.get('Rest'),
                                    'Warmup': param.get('Warmup'),
                                    'MFO': param.get('MFO'),
                                    'AT': param.get('AT'),
                                    'RC': param.get('RC'),
                                    'Max': param.get('Max'),
                                    'Pred': param.get('Pred'),
                                    'PercPred': param.get('PercPred'),
                                    'Normal': param.get('Normal'),
                                    'Class': param.get('Class')
                                }
                                parameters.append(param_data)
                        
                        extracted_data.append({
                            'file_path': file_path,
                            'filename': filename,
                            'subject_id': subject_id,
                            'parameters': parameters
                        })
                    else:
                        raise ValueError(f"Failed to parse XML file: {file_path}")
        
        return extracted_data

    def _validate_directory_path(self):
        if not self.dir_path:
            raise ValueError("Folder path must be provided.")
        # Validate that the normalized path exists and is a directory
        if not os.path.exists(self.dir_path):
            raise ValueError(f"Path does not exist: {self.dir_path}")
        if not os.path.isdir(self.dir_path):
            raise ValueError(f"Provided path is not a directory: {self.dir_path}")
