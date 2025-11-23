"""
Utility functions for extracting data from proforma invoices.
Supports PDF and image files using pdfplumber, PyPDF2, and OCR.
"""
import os
import re
from typing import Dict, List, Optional
import pdfplumber
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image
import cv2
import numpy as np


def extract_from_pdf_pdfplumber(file_path: str) -> Dict:
    """
    Extract text and data from PDF using pdfplumber.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Dictionary with extracted data
    """
    extracted_data = {
        'vendor': None,
        'items': [],
        'total': None,
        'raw_text': ''
    }
    
    try:
        with pdfplumber.open(file_path) as pdf:
            full_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text.append(text)
            
            extracted_data['raw_text'] = '\n'.join(full_text)
            
            # Try to extract vendor name (usually at top)
            vendor_match = re.search(r'(?:vendor|supplier|from|company)[\s:]+([A-Za-z\s&]+)', 
                                    extracted_data['raw_text'], re.IGNORECASE)
            if vendor_match:
                extracted_data['vendor'] = vendor_match.group(1).strip()
            
            # Try to extract total amount
            total_patterns = [
                r'total[:\s]+[\$€£]?([\d,]+\.?\d*)',
                r'amount[:\s]+[\$€£]?([\d,]+\.?\d*)',
                r'grand\s+total[:\s]+[\$€£]?([\d,]+\.?\d*)',
            ]
            for pattern in total_patterns:
                match = re.search(pattern, extracted_data['raw_text'], re.IGNORECASE)
                if match:
                    total_str = match.group(1).replace(',', '')
                    try:
                        extracted_data['total'] = float(total_str)
                        break
                    except ValueError:
                        continue
            
            # Try to extract items from tables
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if len(table) > 1:  # Has header and rows
                        for row in table[1:]:  # Skip header
                            if len(row) >= 3:
                                item_data = {
                                    'name': str(row[0]) if row[0] else '',
                                    'quantity': str(row[1]) if len(row) > 1 and row[1] else '1',
                                    'price': str(row[2]) if len(row) > 2 and row[2] else '0',
                                }
                                extracted_data['items'].append(item_data)
    
    except Exception as e:
        print(f"Error extracting from PDF with pdfplumber: {str(e)}")
    
    return extracted_data


def extract_from_pdf_pypdf2(file_path: str) -> Dict:
    """
    Extract text from PDF using PyPDF2 (fallback method).
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Dictionary with extracted data
    """
    extracted_data = {
        'vendor': None,
        'items': [],
        'total': None,
        'raw_text': ''
    }
    
    try:
        reader = PdfReader(file_path)
        full_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
        
        extracted_data['raw_text'] = '\n'.join(full_text)
        
        # Basic extraction (same patterns as pdfplumber)
        vendor_match = re.search(r'(?:vendor|supplier|from|company)[\s:]+([A-Za-z\s&]+)', 
                                extracted_data['raw_text'], re.IGNORECASE)
        if vendor_match:
            extracted_data['vendor'] = vendor_match.group(1).strip()
        
        total_match = re.search(r'total[:\s]+[\$€£]?([\d,]+\.?\d*)', 
                               extracted_data['raw_text'], re.IGNORECASE)
        if total_match:
            total_str = total_match.group(1).replace(',', '')
            try:
                extracted_data['total'] = float(total_str)
            except ValueError:
                pass
    
    except Exception as e:
        print(f"Error extracting from PDF with PyPDF2: {str(e)}")
    
    return extracted_data


def extract_from_image_ocr(file_path: str) -> Dict:
    """
    Extract text from image using OCR (pytesseract).
    
    Args:
        file_path: Path to image file
        
    Returns:
        Dictionary with extracted data
    """
    extracted_data = {
        'vendor': None,
        'items': [],
        'total': None,
        'raw_text': ''
    }
    
    try:
        # Preprocess image for better OCR
        image = cv2.imread(file_path)
        if image is None:
            return extracted_data
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Perform OCR
        text = pytesseract.image_to_string(thresh)
        extracted_data['raw_text'] = text
        
        # Extract vendor
        vendor_match = re.search(r'(?:vendor|supplier|from|company)[\s:]+([A-Za-z\s&]+)', 
                                text, re.IGNORECASE)
        if vendor_match:
            extracted_data['vendor'] = vendor_match.group(1).strip()
        
        # Extract total
        total_match = re.search(r'total[:\s]+[\$€£]?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if total_match:
            total_str = total_match.group(1).replace(',', '')
            try:
                extracted_data['total'] = float(total_str)
            except ValueError:
                pass
    
    except Exception as e:
        print(f"Error extracting from image with OCR: {str(e)}")
    
    return extracted_data


def extract_proforma_data(file_path: str) -> Dict:
    """
    Main function to extract data from proforma invoice.
    Tries multiple methods in order of preference.
    
    Args:
        file_path: Path to proforma file (PDF or image)
        
    Returns:
        Dictionary with extracted vendor, items, and total
    """
    if not os.path.exists(file_path):
        return {'vendor': None, 'items': [], 'total': None, 'raw_text': ''}
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Try PDF extraction first
    if file_ext == '.pdf':
        # Try pdfplumber first (better for tables)
        data = extract_from_pdf_pdfplumber(file_path)
        if not data['raw_text']:
            # Fallback to PyPDF2
            data = extract_from_pdf_pypdf2(file_path)
        return data
    
    # Try image OCR
    elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        return extract_from_image_ocr(file_path)
    
    else:
        return {'vendor': None, 'items': [], 'total': None, 'raw_text': ''}

