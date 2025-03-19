"""
Fix for Qt font error on Linux.

This script demonstrates how to suppress the Qt font error:
"qt.qpa.fonts: Unable to open default EUDC font: "%WinDir%\\Fonts\\EUDC.TTE""

Usage:
1. Import this module before creating the QApplication
2. Or use the provided wrapper function to create the QApplication

Example:
    # When running as a package
    from LibraryManagementSystem.utils.fix_qt_font_error import create_application
    app = create_application(sys.argv)
    
    # OR when running directly
    from utils.fix_qt_font_error import create_application
    app = create_application(sys.argv)
"""

import os
import sys
from PyQt5.QtWidgets import QApplication

# Set environment variable to use offscreen platform if no display is available
if not os.environ.get('DISPLAY') and not os.environ.get('QT_QPA_PLATFORM'):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Redirect stderr to suppress font error messages
original_stderr = sys.stderr

class FilteredStderr:
    def __init__(self, original):
        self.original = original
        
    def write(self, text):
        # Filter out the EUDC font error
        if "Unable to open default EUDC font" not in text:
            self.original.write(text)
            
    def flush(self):
        self.original.flush()

# Apply the filter
sys.stderr = FilteredStderr(original_stderr)

def create_application(argv=None):
    """
    Create a QApplication with font error suppression.
    
    Args:
        argv: Command line arguments
        
    Returns:
        QApplication instance
    """
    if argv is None:
        argv = sys.argv
    return QApplication(argv)

# Restore stderr when the module is unloaded
def _cleanup():
    sys.stderr = original_stderr

import atexit
atexit.register(_cleanup)
