import os
import xml.etree.ElementTree as ET

class XmlDataReader:
    def __init__(self, dir_path: str = None):
        self.dir_path: str = dir_path

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

    def _validate_directory_path(self):
        if not self.dir_path:
            raise ValueError("Folder path must be provided.")
        # Read files from the specified folder
        if not os.path.isdir(self.dir_path):
            raise ValueError(f"Provided path is not a directory: {self.dir_path}")
