"""
rbible - Command-line Bible verse lookup tool
"""

__version__ = '1.0.4'


from .reference_detector import detect_references

__all__ = ['detect_references']