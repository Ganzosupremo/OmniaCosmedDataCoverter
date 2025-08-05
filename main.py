from xml_data_reader import XmlDataReader


def main():
    folder_path: str = input("Enter the folder path containing XML files: ")
    xml_reader = XmlDataReader(folder_path)
    try:
        for xml_data in xml_reader.read_data():
            print(f"File: {xml_data['file_path']}")
            print(f"Root Element: {xml_data['root_element'].tag}")
            # You can add more processing of the XML data here if needed
    except ValueError as e:
        print(f"Error: {e}")
        return
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()