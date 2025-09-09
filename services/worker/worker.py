import os
import json
import tempfile
import boto3
from datetime import datetime
from pathlib import Path
from typing import List

from rq import Worker
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the existing batch processing logic
import sys
import os

# Add the app directory to Python path for imports
sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.common.database import get_db, create_tables
from services.common.models import Job, JobStatus, User


def process_batch_job(job_id: str, input_files: List[str], user_id: int):
    """Process a batch job with the existing COSMED analysis logic."""
    
    # Set up database connection
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./phase_analyzer.db")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get job from database
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            print(f"Job {job_id} not found")
            return
        
        # Update job status
        job.status = JobStatus.PROCESSING
        db.commit()
        
        # Set up S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('S3_ENDPOINT_URL'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        bucket_name = os.getenv('S3_BUCKET_NAME', 'phase-analyzer')
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Download input files from S3
            local_files = []
            for file_key in input_files:
                local_file_path = temp_path / Path(file_key).name
                s3_client.download_file(bucket_name, file_key, str(local_file_path))
                local_files.append(str(local_file_path))
            
            # Process files using existing logic
            try:
                output_file = process_cosmed_files(local_files, temp_path)
                
                # Upload result to S3
                output_key = f"results/{user_id}/{job_id}/phase_analysis_results.xlsx"
                s3_client.upload_file(str(output_file), bucket_name, output_key)
                
                # Generate presigned URL for download
                download_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': output_key},
                    ExpiresIn=3600 * 24 * 7  # 7 days
                )
                
                # Update job with success
                job.status = JobStatus.COMPLETED
                job.output_url = download_url
                job.completed_at = datetime.utcnow()
                
            except Exception as e:
                # Update job with error
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                print(f"Error processing job {job_id}: {e}")
        
        db.commit()
        
        # Send email notification
        from services.common.email_service import email_service
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            if job.status == JobStatus.COMPLETED:
                email_service.send_job_completion_email(
                    to_email=user.email,
                    user_name=user.name,
                    job_id=job_id,
                    status="completed",
                    download_url=download_url
                )
            elif job.status == JobStatus.FAILED:
                email_service.send_job_completion_email(
                    to_email=user.email,
                    user_name=user.name,
                    job_id=job_id,
                    status="failed",
                    error_message=job.error_message
                )
        
    except Exception as e:
        print(f"Critical error in job {job_id}: {e}")
        if job:
            job.status = JobStatus.FAILED
            job.error_message = f"Critical error: {str(e)}"
            db.commit()
    finally:
        db.close()


def process_cosmed_files(input_files: List[str], output_dir: Path) -> Path:
    """Process COSMED files using the existing analysis logic."""
    try:
        # Try to use the modular components first
        from modules.core.xml_parser import XMLParser
        from modules.core.data_extractor import DataExtractor
        from modules.core.excel_formatter import ExcelFormatter
        from modules.core.export_manager import ExportManager
        
        # Initialize components
        xml_parser = XMLParser()
        data_extractor = DataExtractor()
        excel_formatter = ExcelFormatter()
        export_manager = ExportManager()
        
        # Process each file
        all_phase_data = []
        
        for file_path in input_files:
            try:
                # Parse XML
                xml_data = xml_parser.parse_file(file_path)
                
                # Extract phase data
                phase_data = data_extractor.extract_phases(xml_data)
                all_phase_data.extend(phase_data)
                
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                continue
        
        if not all_phase_data:
            raise Exception("No valid phase data extracted from input files")
        
        # Format data for Excel
        formatted_data = excel_formatter.format_for_export(all_phase_data)
        
        # Export to Excel
        output_file = output_dir / "phase_analysis_results.xlsx"
        export_manager.export_to_excel(formatted_data, output_file)
        
        return output_file
        
    except ImportError:
        # Fallback to existing XML reader if modular components not available
        print("Modular components not available, using fallback XML reader...")
        return process_cosmed_files_fallback(input_files, output_dir)


def process_cosmed_files_fallback(input_files: List[str], output_dir: Path) -> Path:
    """Fallback processing using the existing xml_data_reader."""
    try:
        # Import the existing XML data reader
        from xml_data_reader import XMLDataReader
        from excel_exporter import ExcelExporter
        
        # Initialize the reader and exporter
        xml_reader = XMLDataReader()
        excel_exporter = ExcelExporter()
        
        # Process all files
        all_data = []
        for file_path in input_files:
            try:
                data = xml_reader.read_xml_file(file_path)
                if data:
                    all_data.extend(data)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                continue
        
        if not all_data:
            raise Exception("No valid data extracted from input files")
        
        # Export to Excel
        output_file = output_dir / "cosmed_analysis_results.xlsx"
        excel_exporter.export_to_excel(all_data, str(output_file))
        
        return output_file
        
    except ImportError as e:
        raise Exception(f"Could not import processing modules: {e}")


def main() -> None:
    """Run an RQ worker processing the 'default' queue."""
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    redis = Redis.from_url(redis_url)
    worker = Worker(["default"], connection=redis)
    worker.work()


# Test functions for worker service
def test_process_batch_job_mock(job_id: str, input_files: List[str], user_id: int):
    """Test function to simulate batch job processing without external dependencies."""
    print(f"TEST MODE: Processing job {job_id} for user {user_id}")
    print(f"TEST MODE: Input files: {input_files}")
    
    # Simulate processing time
    import time
    time.sleep(2)
    
    # Create mock output
    output_data = {
        "job_id": job_id,
        "user_id": user_id,
        "input_files": input_files,
        "processed_at": datetime.now().isoformat(),
        "status": "completed_test",
        "mock_results": {
            "total_files_processed": len(input_files),
            "phases_detected": len(input_files) * 3,  # Mock 3 phases per file
            "processing_time_seconds": 2
        }
    }
    
    print(f"TEST MODE: Job completed with mock data: {output_data}")
    return output_data


def test_validate_file_format(file_path: str) -> bool:
    """Test function to validate file format without processing."""
    # Simple file extension check
    valid_extensions = ['.xml', '.txt', '.csv']
    return any(file_path.lower().endswith(ext) for ext in valid_extensions)


def test_estimate_processing_time(file_count: int) -> int:
    """Test function to estimate processing time based on file count."""
    # Mock estimation: 30 seconds per file + 60 seconds base time
    return (file_count * 30) + 60


def test_check_worker_health() -> dict:
    """Test function to check worker service health."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "worker_id": f"test_worker_{os.getpid()}",
        "available_memory_mb": 1024,  # Mock memory
        "cpu_usage_percent": 25.5,   # Mock CPU usage
        "active_jobs": 0,
        "processed_jobs_today": 42   # Mock count
    }


def test_simulate_job_queue() -> dict:
    """Test function to simulate job queue status."""
    return {
        "queue_name": "default",
        "pending_jobs": 3,
        "active_jobs": 1,
        "completed_jobs_today": 15,
        "failed_jobs_today": 1,
        "average_processing_time_seconds": 120,
        "worker_count": 2,
        "queue_health": "normal"
    }


if __name__ == "__main__":
    main()
