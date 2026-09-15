"""dyla_match: jewellery visual matcher (Dyla take-home, Problem 2)."""
import pillow_heif

# Registers HEIC/HEIF support with Pillow's Image.open() -- iPhones save photos in this format by
# default, and it's an advertised content type in backend/main.py's upload validation. Registered once
# here, at package import time, so every Image.open() call anywhere in this package or its callers
# (backend/main.py, dyla_match.cli) can decode a HEIC file without each call site needing to know about it.
pillow_heif.register_heif_opener()
