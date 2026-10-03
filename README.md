# Screen Target

A tiny Windows utility that draws a six-pixel red point in the centre of the primary display. The window stays above normal applications and lets mouse input pass through, so it can be used as a simple alignment marker without installing an overlay framework.

It uses only Python's standard library and the Win32 API through `ctypes`.

Run `Start Screen Target.bat`, or start it directly:

```powershell
python screen_target.py
```

Stop it with `Ctrl+C` when launched from a terminal, or close the Python process through Task Manager.
