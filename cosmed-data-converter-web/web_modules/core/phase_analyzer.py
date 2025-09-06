"""
Phase Analyzer for COSMED data
Analyzes exercise phases and calculates statistics
"""
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import io
from pathlib import Path


class ExercisePhase(Enum):
    """Enumeration of exercise phases"""
    EXERCISE = "exercise"
    WARM_UP = "warm up"
    REST = "rest"
    RECOVERY = "recovery"
    
    @classmethod
    def from_string(cls, phase_str: str) -> Optional['ExercisePhase']:
        """Convert string to ExercisePhase enum, case insensitive"""
        if not isinstance(phase_str, str):
            return None
        
        phase_str = phase_str.lower().strip()
        for phase in cls:
            if phase.value.lower() == phase_str:
                return phase
        return None
    
    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all phase values as strings"""
        return [phase.value for phase in cls]


class PhaseAnalyzer:
    """Analyzes exercise phase data and calculates statistics"""
    
    def __init__(self):
        self.warnings = []
        self.errors = []
    
    def normalize_phase_name(self, phase_str: str) -> str:
        """
        NEW SPEC: Keep phase names exactly as they appear in the file
        No more normalization - preserve the original phase name with numbers
        """
        if not isinstance(phase_str, str):
            return str(phase_str)
        
        # Simply return the phase as-is, just stripped of extra whitespace
        return phase_str.strip()
    
    def read_input_file(self, file_path: str) -> pd.DataFrame:
        """
        Read input file (Excel or CSV) and return DataFrame
        Supports .xlsx, .xls, .csv formats
        Handles structured format: header + units + empty row + data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = file_path.suffix.lower()
        
        try:
            if file_ext == '.csv':
                # Try different encodings for CSV
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    df = pd.read_csv(file_path)  # Fall back to default
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Handle structured file format according to spec
            df = self._process_structured_format(df)
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error reading file {file_path}: {str(e)}")
    
    def _process_structured_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process structured file format:
        - Drop all columns before column 't', but preserve 'Phase' column if it exists
        - Skip units row (row 1) and empty row (row 2)
        - Start analysis from first data row (row 3+)
        """
        # Check if 't' column exists
        if 't' not in df.columns:
            # If no 't' column, assume the file is already in simple format
            self.warnings.append("Column 't' not found. Assuming simple file format without structured headers.")
            return df
        
        # Find the start index (column 't')
        try:
            start_idx = df.columns.get_loc('t')
            
            # Check if Phase column exists and is before 't'
            phase_col_data = None
            if 'Phase' in df.columns:
                phase_idx = df.columns.get_loc('Phase')
                if phase_idx < start_idx:
                    # Save Phase column data before dropping
                    phase_col_data = df['Phase'].copy()
                    self.warnings.append(f"Preserved 'Phase' column from position {phase_idx} (before column 't').")
            
            # Drop all columns before 't'
            df_processed = df.iloc[:, start_idx:].copy()
            
            # Add back the Phase column as the first column if it was before 't'
            if phase_col_data is not None:
                df_processed.insert(0, 'Phase', phase_col_data)
            
            self.warnings.append(f"Dropped {start_idx} columns before column 't' as per specification.")
            
        except KeyError:
            # This shouldn't happen since we checked above, but just in case
            df_processed = df.copy()
        
        # Skip units row (row 1) and empty row (row 2), start from row 3 (index 2)
        if len(df_processed) > 2:
            df_processed = df_processed.iloc[2:].reset_index(drop=True)
            self.warnings.append("Skipped units row and empty row as per structured format specification.")
        else:
            self.warnings.append("File has fewer than 3 rows. Skipping structured format processing.")
        
        return df_processed
    
    def validate_input(self, df: pd.DataFrame) -> None:
        """
        Validate input DataFrame
        Raises errors for critical issues, adds warnings for non-critical ones
        """
        # Check if Phase column exists
        if 'Phase' not in df.columns:
            raise ValueError("Input file must contain a 'Phase' column")
        
        # Check if there are any data rows
        if len(df) == 0:
            raise ValueError("Input file contains no data rows")
        
        # Check for duplicate column names
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            self.warnings.append(f"Duplicate column names found: {duplicate_cols}. They will be renamed automatically.")
    
    def identify_numeric_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Identify columns that are numeric or can be converted to numeric
        Excludes the 'Phase' column
        """
        numeric_cols = []
        non_numeric_cols = []
        
        for col in df.columns:
            if col == 'Phase':
                continue
                
            # Try to convert to numeric
            try:
                # Test conversion on non-null values
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    pd.to_numeric(non_null_values, errors='raise')
                numeric_cols.append(col)
            except (ValueError, TypeError):
                non_numeric_cols.append(col)
        
        if non_numeric_cols:
            self.warnings.append(f"Non-numeric columns will be dropped: {non_numeric_cols}")
        
        return numeric_cols
    
    def prepare_dataframe(self, df: pd.DataFrame, numeric_cols: List[str]) -> pd.DataFrame:
        """
        NEW SPEC: Prepare DataFrame for analysis:
        - Convert numeric columns to float
        - Handle duplicate column names  
        - Keep phase names exactly as they appear (no more "Set n" suffixes)
        """
        # Make a copy to avoid modifying original
        df_work = df.copy()
        
        # Handle duplicate column names
        df_work.columns = pd.io.common.dedup_names(df_work.columns, is_potential_multiindex=False)
        
        # Convert numeric columns to float, errors='coerce' converts invalid values to NaN
        for col in numeric_cols:
            if col in df_work.columns:
                df_work[col] = pd.to_numeric(df_work[col], errors='coerce')
        
        # Prepare phase names - keep exactly as they appear
        phase_names = df_work['Phase'].apply(self.normalize_phase_name)
        
        # NEW SPEC: Phase grouping logic
        # Group phases that are exactly the same, but split when numbers increase within same base phase
        display_phases = []
        phase_groups = []
        current_group = 0
        
        prev_phase = None
        for i, phase in enumerate(phase_names):
            if phase != prev_phase:
                # Phase changed, start new group
                current_group += 1
                prev_phase = phase
            
            display_phases.append(phase)  # Keep exact phase name
            phase_groups.append(current_group)
        
        df_work['Display Phase'] = display_phases
        df_work['_phase_group'] = phase_groups
        
        return df_work
    
    def calculate_phase_statistics(self, df: pd.DataFrame, numeric_cols: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Calculate mean, standard deviation, and max for each phase group
        Returns tuple of (average_df, stddev_df, max_df)
        """
        # Group by display phase name, maintaining order (sort=False)
        grouped = df.groupby('Display Phase', sort=False)[numeric_cols]
        
        # Calculate statistics
        # mean() automatically excludes NaN values
        avg_df = grouped.mean()
        
        # std(ddof=1) calculates sample standard deviation
        std_df = grouped.std(ddof=1)
        
        # max() automatically excludes NaN values
        max_df = grouped.max()
        
        return avg_df, std_df, max_df
    
    def export_to_excel(self, avg_df: pd.DataFrame, std_df: pd.DataFrame, max_df: pd.DataFrame, output_path: str) -> None:
        """
        Export statistics to Excel file with three sheets
        """
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                avg_df.to_excel(writer, sheet_name='Average', index=True)
                std_df.to_excel(writer, sheet_name='StdDev', index=True)
                max_df.to_excel(writer, sheet_name='Max', index=True)
        except Exception as e:
            raise ValueError(f"Error writing Excel file: {str(e)}")
    
    def analyze_file(self, input_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Main analysis function that processes a file and generates phase statistics
        
        Args:
            input_path: Path to input Excel/CSV file
            output_path: Path for output Excel file (optional)
        
        Returns:
            Dictionary with results and metadata
        """
        # Reset warnings and errors
        self.warnings = []
        self.errors = []
        
        try:
            # Read input file
            df = self.read_input_file(input_path)
            
            # Validate input
            self.validate_input(df)
            
            # Identify numeric columns
            numeric_cols = self.identify_numeric_columns(df)
            
            if not numeric_cols:
                raise ValueError("No numeric columns found for analysis")
            
            # Prepare DataFrame
            df_prepared = self.prepare_dataframe(df, numeric_cols)
            
            # Calculate statistics
            avg_df, std_df, max_df = self.calculate_phase_statistics(df_prepared, numeric_cols)
            
            # Generate output path if not provided
            if output_path is None:
                input_file = Path(input_path)
                output_path = input_file.parent / f"{input_file.stem}_phase_stats.xlsx"
            
            # Export to Excel
            self.export_to_excel(avg_df, std_df, max_df, str(output_path))
            
            # Prepare results
            results = {
                'success': True,
                'output_path': str(output_path),
                'input_rows': len(df),
                'numeric_columns': len(numeric_cols),
                'phase_groups': len(avg_df),
                'phases': avg_df.index.tolist(),
                'parameters': numeric_cols,
                'warnings': self.warnings,
                'errors': self.errors,
                'statistics': {
                    'average': avg_df,
                    'stddev': std_df,
                    'max': max_df
                }
            }
            
            return results
            
        except Exception as e:
            self.errors.append(str(e))
            return {
                'success': False,
                'error': str(e),
                'warnings': self.warnings,
                'errors': self.errors
            }
    
    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze a DataFrame directly (for use with uploaded data)
        Returns statistics DataFrames and metadata
        """
        # Reset warnings and errors
        self.warnings = []
        self.errors = []
        
        try:
            # Process structured format if applicable
            df_processed = self._process_structured_format(df.copy())
            
            # NEW SPEC: Handle final RECOVERY rule before other processing
            if len(df_processed) > 0 and 'Phase' in df_processed.columns:
                final_phase = str(df_processed['Phase'].iloc[-1]).strip().upper()
                if final_phase.startswith('RECOVERY'):
                    # Only remove the final phase if it's a RECOVERY, not all final RECOVERY phases
                    # According to spec: "If the final phase in the file is a RECOVERY, ignore it completely"
                    # This means just the final phase, not necessarily all consecutive final RECOVERYs
                    df_processed = df_processed.iloc[:-1].copy()
                    self.warnings.append(f"Removed final RECOVERY phase '{final_phase}' as per specification.")
            
            # Validate input
            self.validate_input(df_processed)
            
            # Identify numeric columns
            numeric_cols = self.identify_numeric_columns(df_processed)
            
            if not numeric_cols:
                raise ValueError("No numeric columns found for analysis")
            
            # Prepare DataFrame
            df_prepared = self.prepare_dataframe(df_processed, numeric_cols)
            
            # Calculate statistics
            avg_df, std_df, max_df = self.calculate_phase_statistics(df_prepared, numeric_cols)
            
            # Prepare results
            results = {
                'success': True,
                'input_rows': len(df),
                'processed_rows': len(df_processed),
                'numeric_columns': len(numeric_cols),
                'phase_groups': len(avg_df),
                'phases': avg_df.index.tolist(),
                'parameters': numeric_cols,
                'warnings': self.warnings,
                'errors': self.errors,
                'statistics': {
                    'average': avg_df,
                    'stddev': std_df,
                    'max': max_df
                }
            }
            
            return results
            
        except Exception as e:
            self.errors.append(str(e))
            return {
                'success': False,
                'error': str(e),
                'warnings': self.warnings,
                'errors': self.errors
            }
    
    def analyze_batch_files(self, files: List[Any], file_names: List[str], selected_parameters: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        NEW SPEC: Analyze multiple files in batch mode
        Each file = one test subject, output has subjects as rows and Phase_Parameter as columns
        
        Args:
            files: List of file objects (BytesIO or similar) 
            file_names: List of corresponding file names
            selected_parameters: Optional list of parameters to include in analysis
        Returns:
            Dictionary with batch analysis results in new format
        """
        batch_results = {
            'success': True,
            'files_processed': 0,
            'total_files': len(files),
            'file_results': {},
            'batch_statistics': None,
            'warnings': [],
            'errors': []
        }
        
        # Store individual subject results
        subject_results = {}
        all_phases = set()
        all_parameters = set()
        
        # Process each file as a separate subject
        for i, (file, filename) in enumerate(zip(files, file_names)):
            try:
                # Reset file pointer
                file.seek(0)
                
                # Read file based on extension
                if filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # Analyze individual file
                file_result = self.analyze_dataframe(df)
                
                if file_result['success']:
                    batch_results['files_processed'] += 1
                    batch_results['file_results'][filename] = file_result
                    
                    # Extract subject name (filename without extension)
                    subject_name = Path(filename).stem
                    
                    # Store subject's phase statistics
                    subject_results[subject_name] = {
                        'average': file_result['statistics']['average'],
                        'stddev': file_result['statistics']['stddev'],
                        'max': file_result['statistics']['max']
                    }
                    
                    # Track all phases and parameters across subjects
                    all_phases.update(file_result['phases'])
                    all_parameters.update(file_result['parameters'])
                    
                else:
                    batch_results['warnings'].append(f"Failed to analyze {filename}: {file_result.get('error', 'Unknown error')}")
                    batch_results['file_results'][filename] = file_result
                    
            except Exception as e:
                error_msg = f"Error processing {filename}: {str(e)}"
                batch_results['warnings'].append(error_msg)
                batch_results['file_results'][filename] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Create batch statistics if we have successful subjects
        if subject_results:
            try:
                # Filter parameters if specified
                if selected_parameters:
                    parameters_to_use = [p for p in selected_parameters if p in all_parameters]
                    if not parameters_to_use:
                        batch_results['warnings'].append("None of the selected parameters were found in the data. Using all available parameters.")
                        parameters_to_use = list(all_parameters)
                else:
                    parameters_to_use = list(all_parameters)
                
                # Create flattened batch statistics according to spec
                batch_stats = self._create_batch_statistics(subject_results, list(all_phases), parameters_to_use)
                batch_results['batch_statistics'] = batch_stats
                
            except Exception as e:
                batch_results['warnings'].append(f"Error creating batch statistics: {str(e)}")
        
        # Update success status
        if batch_results['files_processed'] == 0:
            batch_results['success'] = False
            batch_results['errors'].append("No files were successfully processed")
        
        return batch_results
    
    def _create_batch_statistics(self, subject_results: Dict[str, Dict], all_phases: List[str], parameters: List[str]) -> Dict[str, Any]:
        """
        Create batch statistics according to NEW SPEC:
        - Rows = subjects  
        - Columns = Phase_Parameter
        - Three sheets: Average, StdDev, Max
        """
        results_avg, results_std, results_max = [], [], []
        
        for subject_name, stats in subject_results.items():
            # Initialize rows for this subject
            row_avg = {"Subject": subject_name}
            row_std = {"Subject": subject_name}
            row_max = {"Subject": subject_name}
            
            # Process each phase in the subject's data
            for phase in stats['average'].index:
                for param in parameters:
                    col_name = f"{phase}_{param}"
                    
                    # Get values, defaulting to NaN if missing
                    row_avg[col_name] = stats['average'].at[phase, param] if param in stats['average'].columns else float('nan')
                    row_std[col_name] = stats['stddev'].at[phase, param] if param in stats['stddev'].columns else float('nan')
                    row_max[col_name] = stats['max'].at[phase, param] if param in stats['max'].columns else float('nan')
            
            # For phases not present in this subject, fill with NaN
            for phase in all_phases:
                if phase not in stats['average'].index:
                    for param in parameters:
                        col_name = f"{phase}_{param}"
                        if col_name not in row_avg:
                            row_avg[col_name] = float('nan')
                            row_std[col_name] = float('nan')
                            row_max[col_name] = float('nan')
            
            results_avg.append(row_avg)
            results_std.append(row_std)
            results_max.append(row_max)
        
        # Convert to DataFrames
        final_avg = pd.DataFrame(results_avg)
        final_std = pd.DataFrame(results_std)
        final_max = pd.DataFrame(results_max)
        
        return {
            'success': True,
            'average': final_avg,
            'stddev': final_std,
            'max': final_max,
            'subjects': len(subject_results),
            'phases': all_phases,
            'parameters': parameters
        }
    
    def export_batch_statistics_to_bytes(self, batch_results: Dict[str, Any]) -> bytes:
        """
        NEW SPEC: Export batch statistics to Excel bytes with 3 sheets:
        Average, StdDev, Max (subjects as rows, Phase_Parameter as columns)
        """
        output = io.BytesIO()
        
        try:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                
                # NEW SPEC: Export the 3 main sheets with subjects as rows
                if batch_results['batch_statistics'] and batch_results['batch_statistics']['success']:
                    batch_stats = batch_results['batch_statistics']
                    
                    # Main sheets according to specification
                    batch_stats['average'].to_excel(writer, sheet_name='Average', index=False)
                    batch_stats['stddev'].to_excel(writer, sheet_name='StdDev', index=False)  
                    batch_stats['max'].to_excel(writer, sheet_name='Max', index=False)
                
                # Processing summary sheet
                summary_data = []
                for filename, result in batch_results['file_results'].items():
                    subject_name = Path(filename).stem
                    if result['success']:
                        summary_data.append({
                            'Subject': subject_name,
                            'Filename': filename,
                            'Status': 'Success',
                            'Rows_Processed': result.get('processed_rows', 0),
                            'Phase_Groups': result.get('phase_groups', 0),
                            'Numeric_Columns': result.get('numeric_columns', 0)
                        })
                    else:
                        summary_data.append({
                            'Subject': subject_name,
                            'Filename': filename,
                            'Status': 'Failed',
                            'Error': result.get('error', 'Unknown error'),
                            'Rows_Processed': 0,
                            'Phase_Groups': 0,
                            'Numeric_Columns': 0
                        })
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Processing_Summary', index=False)
            
            output.seek(0)
            return output.read()
            
        except Exception as e:
            raise ValueError(f"Error creating batch Excel bytes: {str(e)}")
        finally:
            output.close()
    
    def export_statistics_to_bytes(self, avg_df: pd.DataFrame, std_df: pd.DataFrame, max_df: pd.DataFrame) -> bytes:
        """
        Export statistics to Excel bytes (for web download)
        """
        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                avg_df.to_excel(writer, sheet_name='Average', index=True)
                std_df.to_excel(writer, sheet_name='StdDev', index=True)
                max_df.to_excel(writer, sheet_name='Max', index=True)
            
            output.seek(0)
            return output.read()
            
        except Exception as e:
            raise ValueError(f"Error creating Excel bytes: {str(e)}")
        finally:
            output.close()