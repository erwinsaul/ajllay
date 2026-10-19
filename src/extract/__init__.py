"""Modulo de extraccion multiformato (CSV, Excel, PDF) del proyecto Ajllay"""

from src.extract.base import BaseExtractor
from src.extract.pdf_extractor import PDFElectoralExtractor
from src.extract.tabular_extractor import TabularExtractor

__all__ = ["BaseExtractor", "TabularExtractor", "PDFElectoralExtractor"]