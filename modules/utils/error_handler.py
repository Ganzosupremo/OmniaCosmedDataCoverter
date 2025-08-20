"""
Error Handler Module
Centralized error handling and logging for the application
"""
import logging
import traceback
import sys
from typing import Optional, Dict, Any, Callable
from functools import wraps

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, logger_name: str = "cosmed_converter"):
        self.logger = logging.getLogger(logger_name)
        self._setup_logging()
        self.error_callbacks: Dict[str, Callable] = {}
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def register_error_callback(self, error_type: str, callback: Callable) -> None:
        """
        Register callback for specific error types
        
        Args:
            error_type: Type of error (e.g., "file_error", "parse_error")
            callback: Function to call when this error occurs
        """
        self.error_callbacks[error_type] = callback
    
    def handle_exception(self, exception: Exception, context: str = "", error_type: str = "general") -> Dict[str, Any]:
        """
        Handle exception with logging and callback notification
        
        Args:
            exception: The exception that occurred
            context: Context where the exception occurred
            error_type: Type of error for callback routing
            
        Returns:
            Error information dictionary
        """
        error_info = {
            'exception_type': type(exception).__name__,
            'message': str(exception),
            'context': context,
            'traceback': traceback.format_exc(),
            'handled': True
        }
        
        # Log the error
        log_message = f"{context}: {error_info['exception_type']}: {error_info['message']}"
        self.logger.error(log_message)
        
        # Call registered callback if exists
        if error_type in self.error_callbacks:
            try:
                self.error_callbacks[error_type](error_info)
            except Exception as callback_error:
                self.logger.error(f"Error in callback for {error_type}: {callback_error}")
        
        return error_info
    
    def log_info(self, message: str, context: str = "") -> None:
        """Log informational message"""
        full_message = f"{context}: {message}" if context else message
        self.logger.info(full_message)
    
    def log_warning(self, message: str, context: str = "") -> None:
        """Log warning message"""
        full_message = f"{context}: {message}" if context else message
        self.logger.warning(full_message)
    
    def log_debug(self, message: str, context: str = "") -> None:
        """Log debug message"""
        full_message = f"{context}: {message}" if context else message
        self.logger.debug(full_message)

def safe_execute(error_handler: Optional[ErrorHandler] = None, context: str = "", error_type: str = "general"):
    """
    Decorator for safe function execution with error handling
    
    Args:
        error_handler: ErrorHandler instance
        context: Context description for errors
        error_type: Type of error for callback routing
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_handler:
                    error_info = error_handler.handle_exception(e, context, error_type)
                    return {'success': False, 'error': error_info}
                else:
                    # Fallback error handling
                    return {
                        'success': False, 
                        'error': {
                            'exception_type': type(e).__name__,
                            'message': str(e),
                            'context': context
                        }
                    }
        return wrapper
    return decorator

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message)
        self.field = field
        self.value = value

class ProcessingError(Exception):
    """Custom exception for data processing errors"""
    def __init__(self, message: str, stage: str = None, file_path: str = None):
        super().__init__(message)
        self.stage = stage
        self.file_path = file_path

class ExportError(Exception):
    """Custom exception for export operation errors"""
    def __init__(self, message: str, export_type: str = None, output_file: str = None):
        super().__init__(message)
        self.export_type = export_type
        self.output_file = output_file
