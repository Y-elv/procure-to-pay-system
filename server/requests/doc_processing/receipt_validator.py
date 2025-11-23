"""
Utility functions for validating receipts against purchase orders.
Extracts data from receipts and compares with PO.
"""
from typing import Dict, List, Optional
from decimal import Decimal
from .proforma_extractor import extract_proforma_data


def validate_receipt_against_po(request) -> Dict:
    """
    Validate receipt file against purchase order.
    
    Args:
        request: PurchaseRequest instance with receipt_file
        
    Returns:
        Dictionary with validation results:
        {
            'is_valid': bool,
            'discrepancy_amount': Decimal,
            'discrepancy_details': {
                'amount_match': bool,
                'items_match': bool,
                'missing_items': List,
                'extra_items': List,
            }
        }
    """
    if not request.receipt_file or not request.purchase_order_file:
        return {
            'is_valid': False,
            'discrepancy_amount': None,
            'discrepancy_details': {
                'error': 'Missing receipt or PO file'
            }
        }
    
    # Extract data from receipt
    receipt_path = request.receipt_file.path
    receipt_data = extract_proforma_data(receipt_path)
    
    # Get PO data from request
    po_amount = request.amount
    receipt_amount = receipt_data.get('total')
    
    # Initialize result
    result = {
        'is_valid': True,
        'discrepancy_amount': Decimal('0.00'),
        'discrepancy_details': {
            'amount_match': True,
            'items_match': True,
            'missing_items': [],
            'extra_items': [],
        }
    }
    
    # Compare amounts
    if receipt_amount:
        receipt_decimal = Decimal(str(receipt_amount))
        po_decimal = Decimal(str(po_amount))
        discrepancy = abs(receipt_decimal - po_decimal)
        
        # Allow small tolerance (0.01)
        if discrepancy > Decimal('0.01'):
            result['is_valid'] = False
            result['discrepancy_amount'] = discrepancy
            result['discrepancy_details']['amount_match'] = False
    
    # Compare items (if available)
    if request.items.exists() and receipt_data.get('items'):
        po_items = {item.item_name.lower(): item for item in request.items.all()}
        receipt_items = {item['name'].lower(): item for item in receipt_data['items'] if item.get('name')}
        
        # Find missing items
        for po_item_name in po_items.keys():
            if po_item_name not in receipt_items:
                result['discrepancy_details']['missing_items'].append(po_item_name)
                result['is_valid'] = False
                result['discrepancy_details']['items_match'] = False
        
        # Find extra items
        for receipt_item_name in receipt_items.keys():
            if receipt_item_name not in po_items:
                result['discrepancy_details']['extra_items'].append(receipt_item_name)
                # Extra items don't necessarily invalidate, but note them
    
    return result

