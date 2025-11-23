"""
Utility functions for generating Purchase Orders (PO) automatically.
Generates PO as PDF or JSON format.
"""
import os
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import json


def generate_po_pdf(request) -> Optional[str]:
    """
    Generate Purchase Order as PDF file.
    
    Args:
        request: PurchaseRequest instance
        
    Returns:
        Path to generated PDF file, or None if error
    """
    try:
        # Create directory if it doesn't exist
        po_dir = os.path.join('media', 'purchase_orders', str(request.id))
        os.makedirs(po_dir, exist_ok=True)
        
        # Generate filename
        filename = f"PO_{request.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = os.path.join(po_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12
        )
        
        # Title
        story.append(Paragraph("PURCHASE ORDER", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # PO Details
        po_data = [
            ['PO Number:', f"PO-{request.id:06d}"],
            ['Date:', datetime.now().strftime('%Y-%m-%d')],
            ['Request Title:', request.title],
            ['Requested By:', request.created_by.get_full_name() or request.created_by.username],
        ]
        
        po_table = Table(po_data, colWidths=[2*inch, 4*inch])
        po_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(po_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Description
        story.append(Paragraph("Description:", heading_style))
        story.append(Paragraph(request.description, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Items table
        if request.items.exists():
            story.append(Paragraph("Items:", heading_style))
            items_data = [['Item', 'Quantity', 'Unit Price', 'Total']]
            for item in request.items.all():
                items_data.append([
                    item.item_name,
                    str(item.quantity),
                    f"${item.price:.2f}",
                    f"${item.total:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(items_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Total amount
        total_data = [
            ['Total Amount:', f"${request.amount:.2f}"]
        ]
        total_table = Table(total_data, colWidths=[4*inch, 2*inch])
        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ]))
        story.append(total_table)
        
        # Build PDF
        doc.build(story)
        
        # Return relative path from media root
        return f'purchase_orders/{request.id}/{filename}'
    
    except Exception as e:
        print(f"Error generating PO PDF: {str(e)}")
        return None


def generate_po_json(request) -> Optional[str]:
    """
    Generate Purchase Order as JSON file.
    
    Args:
        request: PurchaseRequest instance
        
    Returns:
        Path to generated JSON file, or None if error
    """
    try:
        # Create directory if it doesn't exist
        po_dir = os.path.join('media', 'purchase_orders', str(request.id))
        os.makedirs(po_dir, exist_ok=True)
        
        # Generate filename
        filename = f"PO_{request.id}_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = os.path.join(po_dir, filename)
        
        # Build PO data
        po_data = {
            'po_number': f"PO-{request.id:06d}",
            'date': datetime.now().isoformat(),
            'request_id': request.id,
            'title': request.title,
            'description': request.description,
            'amount': str(request.amount),
            'requested_by': {
                'id': request.created_by.id,
                'username': request.created_by.username,
                'full_name': request.created_by.get_full_name() or request.created_by.username,
            },
            'items': [
                {
                    'item_name': item.item_name,
                    'quantity': item.quantity,
                    'price': str(item.price),
                    'total': str(item.total),
                }
                for item in request.items.all()
            ],
            'approvals': [
                {
                    'level': approval.level,
                    'approver': approval.approver.username,
                    'status': approval.status,
                    'comment': approval.comment,
                    'approved_at': approval.updated_at.isoformat() if approval.status == 'approved' else None,
                }
                for approval in request.get_approvals()
            ],
        }
        
        # Write JSON file
        with open(filepath, 'w') as f:
            json.dump(po_data, f, indent=2)
        
        # Return relative path from media root
        return f'purchase_orders/{request.id}/{filename}'
    
    except Exception as e:
        print(f"Error generating PO JSON: {str(e)}")
        return None


def generate_purchase_order(request, format='pdf') -> Optional[str]:
    """
    Main function to generate Purchase Order.
    
    Args:
        request: PurchaseRequest instance
        format: 'pdf' or 'json'
        
    Returns:
        Path to generated file, or None if error
    """
    if format == 'pdf':
        return generate_po_pdf(request)
    elif format == 'json':
        return generate_po_json(request)
    else:
        return None

