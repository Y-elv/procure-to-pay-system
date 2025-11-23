"""
Signals for automatic PO generation and workflow handling.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseRequest
from .doc_processing.po_generator import generate_purchase_order


@receiver(post_save, sender=PurchaseRequest)
def handle_request_status_change(sender, instance, created, **kwargs):
    """
    Signal handler for purchase request status changes.
    Automatically generates PO when request is approved.
    """
    # Only process if status changed to approved (not on creation)
    if not created and instance.status == 'approved' and not instance.purchase_order_file:
        # Generate purchase order
        try:
            po_file = generate_purchase_order(instance)
            if po_file:
                instance.purchase_order_file = po_file
                instance.save(update_fields=['purchase_order_file'])
        except Exception as e:
            # Log error but don't fail the save
            print(f"Error generating PO for request {instance.id}: {str(e)}")

