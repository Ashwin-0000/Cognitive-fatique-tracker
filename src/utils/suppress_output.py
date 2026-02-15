"""
Utility to suppress stdout/stderr output.
Useful for silencing noisy C++ libraries like MediaPipe/TensorFlow.
"""
import os
import sys
from contextlib import contextmanager


@contextmanager
def suppress_stderr():
    """
    Context manager to suppress stderr output.
    Redirects stderr to os.devnull.
    """
    # Open a pair of null files
    null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
    
    # Save the actual stderr (2) file descriptor
    save = os.dup(2)
    
    try:
        # Assign the null pointers to stderr
        os.dup2(null_fds[1], 2)
        yield
    finally:
        # Restore stderr
        os.dup2(save, 2)
        # Close the null files
        os.close(null_fds[0])
        os.close(null_fds[1])
        os.close(save)
