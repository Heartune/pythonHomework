# Qt Font Error Fix

This module provides a solution for the Qt font error that appears on Linux:
```
qt.qpa.fonts: Unable to open default EUDC font: "%WinDir%\\Fonts\\EUDC.TTE"
```

## The Problem

This error occurs because Qt is looking for a Windows-specific font (EUDC.TTE) in a Windows path (%WinDir%\Fonts\) which doesn't exist on Linux systems.

## The Solution

This module provides two ways to fix the issue:

1. **Import the module before creating QApplication**:
   ```python
   import utils.fix_qt_font_error
   from PyQt5.QtWidgets import QApplication
   app = QApplication(sys.argv)
   ```

2. **Use the provided wrapper function**:
   ```python
   from utils.fix_qt_font_error import create_application
   app = create_application(sys.argv)
   ```

## How It Works

The fix works by:
1. Redirecting stderr and filtering out the specific font error message
2. Setting the QT_QPA_PLATFORM environment variable to 'offscreen' if no display is available
3. Restoring stderr when the module is unloaded

## Additional Notes

- This is a non-intrusive solution that doesn't require modifying the Qt libraries
- The error is just a warning and doesn't affect functionality
- The fix is compatible with both GUI and headless environments
