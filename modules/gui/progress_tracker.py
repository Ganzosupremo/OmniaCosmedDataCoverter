"""
Progress Tracker Module
Handles progress tracking and status updates for GUI operations
"""
import threading
import time
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class ProgressState:
    """Progress state information"""
    current: int = 0
    total: int = 100
    message: str = ""
    stage: str = ""
    percentage: float = 0.0
    is_indeterminate: bool = False
    is_complete: bool = False
    has_error: bool = False
    error_message: str = ""

class ProgressTracker:
    """Tracks and manages progress for long-running operations"""
    
    def __init__(self):
        self.state = ProgressState()
        self.callbacks: list[Callable] = []
        self.lock = threading.Lock()
        self.start_time: Optional[float] = None
        self.is_active = False
    
    def register_callback(self, callback: Callable[[ProgressState], None]) -> None:
        """
        Register callback to receive progress updates
        
        Args:
            callback: Function that accepts ProgressState
        """
        with self.lock:
            if callback not in self.callbacks:
                self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """
        Unregister progress callback
        
        Args:
            callback: Function to remove from callbacks
        """
        with self.lock:
            if callback in self.callbacks:
                self.callbacks.remove(callback)
    
    def start(self, total_items: int = 100, message: str = "Starting...", stage: str = "Initializing") -> None:
        """
        Start progress tracking
        
        Args:
            total_items: Total number of items to process
            message: Initial status message
            stage: Current processing stage
        """
        with self.lock:
            self.state = ProgressState(
                current=0,
                total=total_items,
                message=message,
                stage=stage,
                percentage=0.0,
                is_indeterminate=False,
                is_complete=False,
                has_error=False
            )
            self.start_time = time.time()
            self.is_active = True
        
        self._notify_callbacks()
    
    def update(self, current: int, message: str = None, stage: str = None) -> None:
        """
        Update progress
        
        Args:
            current: Current progress value
            message: Status message (optional)
            stage: Current stage (optional)
        """
        with self.lock:
            if not self.is_active:
                return
            
            self.state.current = min(current, self.state.total)
            self.state.percentage = (self.state.current / self.state.total) * 100 if self.state.total > 0 else 0
            
            if message:
                self.state.message = message
            if stage:
                self.state.stage = stage
        
        self._notify_callbacks()
    
    def increment(self, amount: int = 1, message: str = None, stage: str = None) -> None:
        """
        Increment progress by specified amount
        
        Args:
            amount: Amount to increment
            message: Status message (optional)
            stage: Current stage (optional)
        """
        with self.lock:
            new_current = self.state.current + amount
        
        self.update(new_current, message, stage)
    
    def set_indeterminate(self, is_indeterminate: bool, message: str = None) -> None:
        """
        Set indeterminate progress mode
        
        Args:
            is_indeterminate: Whether progress is indeterminate
            message: Status message
        """
        with self.lock:
            if not self.is_active:
                return
            
            self.state.is_indeterminate = is_indeterminate
            if message:
                self.state.message = message
        
        self._notify_callbacks()
    
    def complete(self, message: str = "Complete", success: bool = True) -> None:
        """
        Mark progress as complete
        
        Args:
            message: Completion message
            success: Whether operation was successful
        """
        with self.lock:
            self.state.current = self.state.total
            self.state.percentage = 100.0
            self.state.message = message
            self.state.is_complete = True
            self.state.is_indeterminate = False
            self.is_active = False
            
            if not success:
                self.state.has_error = True
        
        self._notify_callbacks()
    
    def error(self, error_message: str, stage: str = None) -> None:
        """
        Mark progress as failed with error
        
        Args:
            error_message: Error description
            stage: Stage where error occurred
        """
        with self.lock:
            self.state.has_error = True
            self.state.error_message = error_message
            self.state.message = f"Error: {error_message}"
            self.state.is_complete = True
            self.state.is_indeterminate = False
            self.is_active = False
            
            if stage:
                self.state.stage = stage
        
        self._notify_callbacks()
    
    def reset(self) -> None:
        """Reset progress tracker to initial state"""
        with self.lock:
            self.state = ProgressState()
            self.start_time = None
            self.is_active = False
        
        self._notify_callbacks()
    
    def get_state(self) -> ProgressState:
        """Get current progress state (thread-safe copy)"""
        with self.lock:
            return ProgressState(
                current=self.state.current,
                total=self.state.total,
                message=self.state.message,
                stage=self.state.stage,
                percentage=self.state.percentage,
                is_indeterminate=self.state.is_indeterminate,
                is_complete=self.state.is_complete,
                has_error=self.state.has_error,
                error_message=self.state.error_message
            )
    
    def get_elapsed_time(self) -> Optional[float]:
        """Get elapsed time since progress started"""
        if self.start_time:
            return time.time() - self.start_time
        return None
    
    def get_estimated_remaining_time(self) -> Optional[float]:
        """Get estimated remaining time based on current progress"""
        elapsed = self.get_elapsed_time()
        if elapsed and self.state.current > 0 and not self.state.is_complete:
            rate = self.state.current / elapsed
            remaining_items = self.state.total - self.state.current
            return remaining_items / rate if rate > 0 else None
        return None
    
    def get_formatted_status(self) -> Dict[str, Any]:
        """Get formatted status information"""
        state = self.get_state()
        elapsed = self.get_elapsed_time()
        remaining = self.get_estimated_remaining_time()
        
        return {
            'percentage': f"{state.percentage:.1f}%",
            'progress_text': f"{state.current}/{state.total}",
            'message': state.message,
            'stage': state.stage,
            'elapsed_time': f"{elapsed:.1f}s" if elapsed else "0s",
            'remaining_time': f"{remaining:.1f}s" if remaining else "Unknown",
            'status': self._get_status_description()
        }
    
    def _get_status_description(self) -> str:
        """Get human-readable status description"""
        if self.state.has_error:
            return "Error"
        elif self.state.is_complete:
            return "Complete"
        elif self.state.is_indeterminate:
            return "Processing..."
        elif self.is_active:
            return "In Progress"
        else:
            return "Ready"
    
    def _notify_callbacks(self) -> None:
        """Notify all registered callbacks about progress update"""
        state_copy = self.get_state()
        for callback in self.callbacks:
            try:
                # Call callback in a separate thread to avoid blocking
                threading.Thread(
                    target=callback, 
                    args=(state_copy,), 
                    daemon=True
                ).start()
            except Exception as e:
                print(f"Error in progress callback: {e}")

class ThreadedOperation:
    """Helper class for running operations with progress tracking"""
    
    def __init__(self, progress_tracker: ProgressTracker):
        self.progress_tracker = progress_tracker
        self.thread: Optional[threading.Thread] = None
        self.is_cancelled = False
    
    def run(self, operation: Callable, *args, **kwargs) -> threading.Thread:
        """
        Run operation in separate thread with progress tracking
        
        Args:
            operation: Function to run
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Thread object
        """
        def wrapped_operation():
            try:
                result = operation(self.progress_tracker, *args, **kwargs)
                if not self.is_cancelled and not self.progress_tracker.state.has_error:
                    self.progress_tracker.complete("Operation completed successfully")
                return result
            except Exception as e:
                if not self.is_cancelled:
                    self.progress_tracker.error(str(e))
                raise
        
        self.thread = threading.Thread(target=wrapped_operation, daemon=True)
        self.thread.start()
        return self.thread
    
    def cancel(self) -> None:
        """Cancel the running operation"""
        self.is_cancelled = True
        if self.thread and self.thread.is_alive():
            # Note: Python doesn't have thread cancellation, so we rely on
            # the operation checking self.is_cancelled periodically
            pass
    
    def is_running(self) -> bool:
        """Check if operation is currently running"""
        return self.thread is not None and self.thread.is_alive()
