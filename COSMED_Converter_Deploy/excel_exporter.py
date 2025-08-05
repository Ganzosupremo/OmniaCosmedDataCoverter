class ExcelExporter:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def export_extracted_xml_data(self, extracted_data: list[dict]):
        """
        Export extracted XML data to Excel with each subject as a row and parameters as columns.
        
        Args:
            extracted_data: List of dictionaries containing extracted XML data from xml_data_reader
        """
        import pandas as pd
        
        if not extracted_data:
            raise ValueError("No data provided for export")
        
        # Prepare rows for the DataFrame
        rows = []
        
        for file_data in extracted_data:
            # Start with basic file information
            row = {
                'filename': file_data['filename'],
                'subject_id': file_data['subject_id'],
                'file_path': file_data['file_path']
            }
            
            # Add all parameters as columns
            for param in file_data['parameters']:
                param_name = param['Name']
                unit = param['UM']
                
                # Create column names with units for clarity
                base_col_name = f"{param_name}" if not unit or unit == "---" else f"{param_name} ({unit})"
                
                # Add all measurement phases as separate columns
                row[f"{base_col_name}_Value"] = param['Value']
                row[f"{base_col_name}_Rest"] = param['Rest']
                row[f"{base_col_name}_Warmup"] = param['Warmup']
                row[f"{base_col_name}_MFO"] = param['MFO']
                row[f"{base_col_name}_AT"] = param['AT']
                row[f"{base_col_name}_RC"] = param['RC']
                row[f"{base_col_name}_Max"] = param['Max']
                row[f"{base_col_name}_Pred"] = param['Pred']
                row[f"{base_col_name}_PercPred"] = param['PercPred']
                row[f"{base_col_name}_Normal"] = param['Normal']
                row[f"{base_col_name}_Class"] = param['Class']
            
            rows.append(row)
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(rows)
        
        # Write to Excel with formatting
        with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Subject_Data', index=False)
            
            # Get the workbook and worksheet for formatting
            workbook = writer.book
            worksheet = writer.sheets['Subject_Data']
            
            # Adjust column widths for better readability
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Set a reasonable width (max 30 characters)
                adjusted_width = min(max_length + 2, 30)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Data exported successfully to {self.file_path}")
        print(f"Exported {len(rows)} subjects with {len(df.columns)} columns")

    def export_max_values_only(self, extracted_data: list[dict]):
        """
        Export only the Max values for each parameter (simplified version).
        
        Args:
            extracted_data: List of dictionaries containing extracted XML data from xml_data_reader
        """
        import pandas as pd
        
        if not extracted_data:
            raise ValueError("No data provided for export")
        
        # Prepare rows for the DataFrame
        rows = []
        
        for file_data in extracted_data:
            # Start with basic file information
            row = {
                'filename': file_data['filename'],
                'subject_id': file_data['subject_id']
            }
            
            # Add only Max values for each parameter
            for param in file_data['parameters']:
                param_name = param['Name']
                unit = param['UM']
                max_value = param['Max']
                
                # Create column name with unit
                if unit and unit != "---":
                    col_name = f"{param_name}_Max ({unit})"
                else:
                    col_name = f"{param_name}_Max"
                
                row[col_name] = max_value
            
            rows.append(row)
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(rows)
        df.to_excel(self.file_path, index=False)
        
        print(f"Max values exported successfully to {self.file_path}")
        print(f"Exported {len(rows)} subjects with {len(df.columns)} columns")

    def export_selected_parameters(self, extracted_data: list[dict]):
        """
        Export only specific parameters and their values as requested.
        
        Extracts:
        - t (s)_Max
        - Speed (Kmh)_Max
        - Pace (mm:ss/km)_Max
        - VO2 (mL/min)_Max
        - VO2/kg (mL/min/Kg)_MFO, _AT, _RC, _Max
        - VCO2 (mL/min)_Max
        - METS_Max
        - RQ_Max
        - VE (L/min)_Max
        - Rf (1/min)_Max
        - HR (bpm)_Max
        - VO2/HR (mL/beat)_Max
        
        Args:
            extracted_data: List of dictionaries containing extracted XML data from xml_data_reader
        """
        import pandas as pd
        
        if not extracted_data:
            raise ValueError("No data provided for export")
        
        # Define the specific parameters and values we want to extract
        target_parameters = {
            't': ['Max'],
            'Speed': ['Max'],
            'Pace': ['Max'],
            'VO2': ['Max'],
            'VO2/kg': ['MFO', 'AT', 'RC', 'Max'],
            'VCO2': ['Max'],
            'METS': ['Max'],
            'RQ': ['Max'],
            'VE': ['Max'],
            'Rf': ['Max'],
            'HR': ['Max'],
            'VO2/HR': ['Max']
        }
        
        # Prepare rows for the DataFrame
        rows = []
        
        for file_data in extracted_data:
            # Start with basic file information
            row = {
                'filename': file_data['filename'],
                'subject_id': file_data['subject_id']
            }
            
            # Add only the specified parameters and values
            for param in file_data['parameters']:
                param_name = param['Name']
                unit = param['UM']
                
                if param_name in target_parameters:
                    # Create base column name with unit
                    if unit and unit != "---":
                        base_col_name = f"{param_name} ({unit})"
                    else:
                        base_col_name = param_name
                    
                    # Add only the specified values for this parameter
                    for value_type in target_parameters[param_name]:
                        col_name = f"{base_col_name}_{value_type}"
                        row[col_name] = param[value_type]
            
            rows.append(row)
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(rows)
        df.to_excel(self.file_path, index=False)
        
        print(f"Selected parameters exported successfully to {self.file_path}")
        print(f"Exported {len(rows)} subjects with {len(df.columns)} columns")
        
        # Print the columns that were exported for verification
        parameter_cols = [col for col in df.columns if col not in ['filename', 'subject_id']]
        print(f"Parameters exported: {', '.join(parameter_cols)}")