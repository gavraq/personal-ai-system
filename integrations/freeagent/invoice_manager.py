"""
FreeAgent Invoice Manager - handles all invoice-related operations.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
try:
    from .freeagent_client import FreeAgentClient
except ImportError:
    from freeagent_client import FreeAgentClient


class InvoiceManager:
    """Manages invoice operations through FreeAgent API."""
    
    def __init__(self, client: FreeAgentClient):
        self.client = client
        
    def list_invoices(self, 
                     contact_id: Optional[int] = None,
                     project_id: Optional[int] = None, 
                     from_date: Optional[str] = None,
                     to_date: Optional[str] = None,
                     view: str = 'recent') -> List[Dict[str, Any]]:
        """
        List invoices with optional filters.
        
        Args:
            contact_id: Filter by contact ID
            project_id: Filter by project ID  
            from_date: Filter from date (YYYY-MM-DD)
            to_date: Filter to date (YYYY-MM-DD)
            view: View type ('recent', 'all', 'draft', 'sent', 'paid', 'overdue')
        """
        params = {'view': view}
        
        if contact_id:
            params['contact'] = contact_id
        if project_id:
            params['project'] = project_id
        if from_date:
            params['from_date'] = from_date
        if to_date:
            params['to_date'] = to_date
            
        response = self.client._make_request('GET', '/invoices', params=params)
        return response.json().get('invoices', [])
        
    def get_invoice(self, invoice_id: int) -> Dict[str, Any]:
        """Get a specific invoice by ID."""
        response = self.client._make_request('GET', f'/invoices/{invoice_id}')
        return response.json().get('invoice', {})
        
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new invoice.
        
        Expected invoice_data structure:
        {
            "contact": "contact_url_or_id",
            "dated_on": "2024-01-15",
            "due_on": "2024-02-15", 
            "reference": "INV001",
            "invoice_items": [
                {
                    "description": "Service description",
                    "price": "100.00",
                    "quantity": "1.0",
                    "sales_tax_rate": "0.20"
                }
            ],
            "payment_terms_in_days": 30,
            "currency": "GBP",
            "exchange_rate": "1.0"
        }
        """
        data = {'invoice': invoice_data}
        response = self.client._make_request('POST', '/invoices', data=data)
        return response.json().get('invoice', {})
        
    def update_invoice(self, invoice_id: int, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing invoice."""
        data = {'invoice': invoice_data}
        response = self.client._make_request('PUT', f'/invoices/{invoice_id}', data=data)
        return response.json().get('invoice', {})
        
    def send_invoice(self, invoice_id: int, email_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send an invoice by email.
        
        Args:
            invoice_id: ID of invoice to send
            email_options: Optional email configuration
                {
                    "email": "client@example.com",
                    "subject": "Invoice subject",
                    "body": "Email body text"
                }
        """
        data = {}
        if email_options:
            data.update(email_options)
            
        response = self.client._make_request('PUT', f'/invoices/{invoice_id}/send_email', data=data)
        return response.json()
        
    def mark_invoice_sent(self, invoice_id: int) -> Dict[str, Any]:
        """Mark an invoice as sent (without sending email)."""
        response = self.client._make_request('PUT', f'/invoices/{invoice_id}/mark_as_sent')
        return response.json()
        
    def mark_invoice_paid(self, invoice_id: int, payment_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Mark an invoice as paid.
        
        Args:
            invoice_id: ID of invoice to mark as paid
            payment_data: Optional payment details
                {
                    "dated_on": "2024-01-20",
                    "reference": "Payment ref"
                }
        """
        data = payment_data or {}
        response = self.client._make_request('PUT', f'/invoices/{invoice_id}/mark_as_paid', data=data)
        return response.json()
        
    def get_invoice_pdf(self, invoice_id: int) -> bytes:
        """Download invoice as PDF."""
        response = self.client._make_request('GET', f'/invoices/{invoice_id}.pdf')
        return response.content
        
    def duplicate_invoice(self, invoice_id: int, new_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a duplicate of an existing invoice.
        
        Args:
            invoice_id: ID of invoice to duplicate
            new_date: New date for duplicated invoice (YYYY-MM-DD)
        """
        # Get original invoice
        original = self.get_invoice(invoice_id)
        
        # Prepare new invoice data
        new_invoice_data = {
            'contact': original.get('contact'),
            'project': original.get('project'),
            'dated_on': new_date or datetime.now().strftime('%Y-%m-%d'),
            'due_on': original.get('due_on'),
            'reference': f"{original.get('reference', 'INV')}-COPY",
            'currency': original.get('currency'),
            'exchange_rate': original.get('exchange_rate'),
            'payment_terms_in_days': original.get('payment_terms_in_days'),
            'invoice_items': original.get('invoice_items', []),
            'comments': original.get('comments', ''),
            'sales_tax_rate': original.get('sales_tax_rate')
        }
        
        # Remove fields that shouldn't be copied
        for field in ['url', 'id', 'status', 'total_value', 'paid_value', 'due_value']:
            new_invoice_data.pop(field, None)
            
        return self.create_invoice(new_invoice_data)
        
    def get_invoice_status_summary(self) -> Dict[str, int]:
        """Get a summary of invoices by status."""
        all_invoices = self.list_invoices(view='all')
        
        status_counts = {
            'draft': 0,
            'sent': 0, 
            'paid': 0,
            'overdue': 0,
            'cancelled': 0
        }
        
        for invoice in all_invoices:
            status = invoice.get('status', '').lower()
            if status in status_counts:
                status_counts[status] += 1
                
        return status_counts
        
    def get_overdue_invoices(self) -> List[Dict[str, Any]]:
        """Get all overdue invoices."""
        return self.list_invoices(view='overdue')
        
    def get_unpaid_invoices(self) -> List[Dict[str, Any]]:
        """Get all unpaid invoices (sent but not paid)."""
        return self.list_invoices(view='sent')
        
    def calculate_total_outstanding(self) -> float:
        """Calculate total outstanding amount from unpaid invoices."""
        unpaid = self.get_unpaid_invoices()
        overdue = self.get_overdue_invoices()
        
        total = 0.0
        all_unpaid = unpaid + overdue
        
        for invoice in all_unpaid:
            due_value = invoice.get('due_value', 0)
            if isinstance(due_value, str):
                due_value = float(due_value)
            total += due_value
            
        return total