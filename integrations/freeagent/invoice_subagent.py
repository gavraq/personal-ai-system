"""
FreeAgent Invoice Sub-Agent - Natural language interface for invoice management.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
try:
    from .freeagent_client import FreeAgentClient
    from .invoice_manager import InvoiceManager
except ImportError:
    from freeagent_client import FreeAgentClient
    from invoice_manager import InvoiceManager


class InvoiceSubAgent:
    """
    Sub-agent for handling FreeAgent invoice tasks through natural language commands.
    """
    
    def __init__(self, client: FreeAgentClient):
        self.client = client
        self.invoice_manager = InvoiceManager(client)
        
        # Command patterns for natural language processing
        self.command_patterns = {
            'list_invoices': [
                r'(?i)list (?:all )?invoices?',
                r'(?i)show (?:me )?(?:all )?invoices?',
                r'(?i)get (?:all )?invoices?'
            ],
            'list_overdue': [
                r'(?i)(?:list|show|get) overdue invoices?',
                r'(?i)which invoices? (?:are )?overdue',
                r'(?i)overdue invoices?'
            ],
            'list_unpaid': [
                r'(?i)(?:list|show|get) unpaid invoices?',
                r'(?i)which invoices? (?:are )?unpaid',
                r'(?i)unpaid invoices?'
            ],
            'total_outstanding': [
                r'(?i)(?:what.s|how much) (?:is )?(?:the )?total outstanding',
                r'(?i)total (?:amount )?outstanding',
                r'(?i)how much (?:money )?(?:am i|are we) owed'
            ],
            'invoice_summary': [
                r'(?i)invoice summary',
                r'(?i)invoice (?:status )?overview',
                r'(?i)summarize (?:my )?invoices?'
            ],
            'create_invoice': [
                r'(?i)create (?:a |an )?(?:new )?invoice',
                r'(?i)new invoice',
                r'(?i)make (?:a |an )?(?:new )?invoice'
            ],
            'create_icbc_invoice': [
                r'(?i)create (?:a |an )?(?:new )?invoice (?:for )?ICBC',
                r'(?i)(?:new|draft) ICBC invoice',
                r'(?i)create (?:a |an )?(?:draft )?invoice (?:for )?ICBC (?:Standard|Bank)',
                r'(?i)draft invoice (?:for )?ICBC',
                r'(?i)create ICBC invoice.*'
            ],
            'create_actual_icbc_invoice': [
                r'(?i)create (?:the )?actual ICBC invoice',
                r'(?i)actually create ICBC invoice',
                r'(?i)create real ICBC invoice',
                r'(?i)submit ICBC invoice',
                r'(?i)finalize ICBC invoice'
            ],
            'create_monthly_invoice': [
                r'(?i)create (?:a |an )?monthly invoice (?:for )?(.*)',
                r'(?i)(?:new|draft) monthly invoice (?:for )?(.*)',
                r'(?i)create (?:consulting )?invoice for (\w+) (\d{4})'
            ],
            'send_invoice': [
                r'(?i)send invoice (\d+)',
                r'(?i)email invoice (\d+)'
            ],
            'mark_paid': [
                r'(?i)mark invoice (\d+) (?:as )?paid',
                r'(?i)invoice (\d+) (?:is |was )?paid'
            ],
            'get_invoice': [
                r'(?i)(?:show|get|display) invoice (\d+)',
                r'(?i)invoice (\d+) details'
            ],
            'check_auth_status': [
                r'(?i)check auth(?:entication)? status',
                r'(?i)auth(?:entication)? status',
                r'(?i)check tokens?'
            ],
            'refresh_tokens': [
                r'(?i)refresh tokens?',
                r'(?i)refresh auth(?:entication)?',
                r'(?i)renew tokens?'
            ]
        }
        
        # Store last calculated invoice for creating actual invoice
        self.last_icbc_calculation = None
        
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a natural language command and execute the appropriate action.
        
        Args:
            command: Natural language command string
            
        Returns:
            Dict containing result and any relevant data
        """
        try:
            # Check authentication status before processing commands
            auth_status = self._check_authentication()
            if not auth_status['success']:
                return auth_status
            
            # Match command against patterns
            for action, patterns in self.command_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, command)
                    if match:
                        return self._execute_action(action, match, command)
                        
            return {
                'success': False,
                'message': 'Command not recognized. Try "help" for available commands.',
                'suggestions': self._get_command_suggestions()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing command: {str(e)}',
                'error': str(e)
            }
            
    def _execute_action(self, action: str, match: re.Match, original_command: str) -> Dict[str, Any]:
        """Execute the matched action."""
        
        if action == 'list_invoices':
            return self._handle_list_invoices()
            
        elif action == 'list_overdue':
            return self._handle_list_overdue()
            
        elif action == 'list_unpaid':
            return self._handle_list_unpaid()
            
        elif action == 'total_outstanding':
            return self._handle_total_outstanding()
            
        elif action == 'invoice_summary':
            return self._handle_invoice_summary()
            
        elif action == 'create_invoice':
            return self._handle_create_invoice_prompt()
            
        elif action == 'create_icbc_invoice':
            return self._handle_create_icbc_invoice(original_command)
        
        elif action == 'create_actual_icbc_invoice':
            return self._handle_create_actual_icbc_invoice()
            
        elif action == 'create_monthly_invoice':
            return self._handle_create_monthly_invoice(match, original_command)
            
        elif action == 'send_invoice':
            invoice_id = int(match.group(1))
            return self._handle_send_invoice(invoice_id)
            
        elif action == 'mark_paid':
            invoice_id = int(match.group(1))
            return self._handle_mark_paid(invoice_id)
            
        elif action == 'get_invoice':
            invoice_id = int(match.group(1))
            return self._handle_get_invoice(invoice_id)
            
        elif action == 'check_auth_status':
            return self.check_authentication_status()
            
        elif action == 'refresh_tokens':
            return self.attempt_token_refresh()
            
        else:
            return {'success': False, 'message': 'Unknown action'}
            
    def _handle_list_invoices(self) -> Dict[str, Any]:
        """Handle listing all recent invoices."""
        invoices = self.invoice_manager.list_invoices(view='recent')
        
        formatted_invoices = []
        for inv in invoices:
            formatted_invoices.append({
                'id': inv.get('id'),
                'reference': inv.get('reference'),
                'contact': inv.get('contact'),
                'date': inv.get('dated_on'),
                'due_date': inv.get('due_on'),
                'status': inv.get('status'),
                'total': inv.get('total_value'),
                'due_amount': inv.get('due_value')
            })
            
        return {
            'success': True,
            'action': 'list_invoices',
            'message': f'Found {len(invoices)} recent invoices',
            'data': formatted_invoices
        }
        
    def _handle_list_overdue(self) -> Dict[str, Any]:
        """Handle listing overdue invoices."""
        overdue = self.invoice_manager.get_overdue_invoices()
        
        if not overdue:
            return {
                'success': True,
                'action': 'list_overdue',
                'message': 'No overdue invoices found',
                'data': []
            }
            
        formatted_overdue = []
        total_overdue = 0
        
        for inv in overdue:
            due_amount = float(inv.get('due_value', 0))
            total_overdue += due_amount
            
            formatted_overdue.append({
                'id': inv.get('id'),
                'reference': inv.get('reference'),
                'contact': inv.get('contact'),
                'due_date': inv.get('due_on'),
                'days_overdue': self._calculate_days_overdue(inv.get('due_on')),
                'due_amount': due_amount
            })
            
        return {
            'success': True,
            'action': 'list_overdue',
            'message': f'{len(overdue)} overdue invoices totaling £{total_overdue:.2f}',
            'data': formatted_overdue,
            'total_overdue': total_overdue
        }
        
    def _handle_list_unpaid(self) -> Dict[str, Any]:
        """Handle listing unpaid invoices."""
        unpaid = self.invoice_manager.get_unpaid_invoices()
        
        formatted_unpaid = []
        for inv in unpaid:
            formatted_unpaid.append({
                'id': inv.get('id'),
                'reference': inv.get('reference'),
                'contact': inv.get('contact'),
                'date': inv.get('dated_on'),
                'due_date': inv.get('due_on'),
                'due_amount': inv.get('due_value')
            })
            
        return {
            'success': True,
            'action': 'list_unpaid',
            'message': f'Found {len(unpaid)} unpaid invoices',
            'data': formatted_unpaid
        }
        
    def _handle_total_outstanding(self) -> Dict[str, Any]:
        """Handle calculating total outstanding amount."""
        total = self.invoice_manager.calculate_total_outstanding()
        
        return {
            'success': True,
            'action': 'total_outstanding',
            'message': f'Total outstanding amount: £{total:.2f}',
            'data': {'total_outstanding': total}
        }
        
    def _handle_invoice_summary(self) -> Dict[str, Any]:
        """Handle providing invoice summary."""
        summary = self.invoice_manager.get_invoice_status_summary()
        total_outstanding = self.invoice_manager.calculate_total_outstanding()
        
        return {
            'success': True,
            'action': 'invoice_summary',
            'message': 'Invoice summary generated',
            'data': {
                'status_counts': summary,
                'total_outstanding': total_outstanding,
                'summary_text': f"Draft: {summary['draft']}, Sent: {summary['sent']}, "
                              f"Paid: {summary['paid']}, Overdue: {summary['overdue']}, "
                              f"Outstanding: £{total_outstanding:.2f}"
            }
        }
        
    def _handle_create_invoice_prompt(self) -> Dict[str, Any]:
        """Handle create invoice request - returns prompt for required info."""
        return {
            'success': True,
            'action': 'create_invoice_prompt',
            'message': 'To create an invoice, I need the following information:',
            'data': {
                'required_fields': [
                    'Contact/Customer name or ID',
                    'Invoice date (YYYY-MM-DD)', 
                    'Due date (YYYY-MM-DD)',
                    'Reference number',
                    'Invoice items (description, price, quantity)'
                ],
                'example': {
                    'contact': 'Customer Name or Contact ID',
                    'dated_on': '2024-01-15',
                    'due_on': '2024-02-15',
                    'reference': 'INV001',
                    'invoice_items': [
                        {
                            'description': 'Consulting services',
                            'price': '100.00',
                            'quantity': '8.0',
                            'sales_tax_rate': '20.0'
                        }
                    ]
                }
            }
        }
        
    def _handle_send_invoice(self, invoice_id: int) -> Dict[str, Any]:
        """Handle sending an invoice."""
        try:
            result = self.invoice_manager.send_invoice(invoice_id)
            return {
                'success': True,
                'action': 'send_invoice',
                'message': f'Invoice {invoice_id} sent successfully',
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to send invoice {invoice_id}: {str(e)}',
                'error': str(e)
            }
            
    def _handle_mark_paid(self, invoice_id: int) -> Dict[str, Any]:
        """Handle marking an invoice as paid."""
        try:
            result = self.invoice_manager.mark_invoice_paid(invoice_id)
            return {
                'success': True,
                'action': 'mark_paid',
                'message': f'Invoice {invoice_id} marked as paid',
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to mark invoice {invoice_id} as paid: {str(e)}',
                'error': str(e)
            }
            
    def _handle_get_invoice(self, invoice_id: int) -> Dict[str, Any]:
        """Handle getting invoice details."""
        try:
            invoice = self.invoice_manager.get_invoice(invoice_id)
            return {
                'success': True,
                'action': 'get_invoice',
                'message': f'Invoice {invoice_id} details retrieved',
                'data': invoice
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get invoice {invoice_id}: {str(e)}',
                'error': str(e)
            }
            
    def _handle_create_icbc_invoice(self, original_command: str) -> Dict[str, Any]:
        """Handle creating an ICBC invoice."""
        try:
            # Extract month/year from command if present
            import re
            month_match = re.search(r'(?i)(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', original_command)
            year_match = re.search(r'(\d{4})', original_command)
            days_match = re.search(r'(\d+)\s*days?', original_command)
            
            # Default to current month if not specified
            if month_match:
                month_name = month_match.group(1).lower()
                month_mapping = {
                    'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
                    'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6,
                    'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9,
                    'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12
                }
                month = month_mapping.get(month_name, datetime.now().month)
            else:
                month = datetime.now().month
                
            year = int(year_match.group(1)) if year_match else datetime.now().year
            days = int(days_match.group(1)) if days_match else 14  # Default to 14 days
            
            # Calculate invoice details based on correct ICBC rate
            daily_rate = 1700.00  # Correct rate from current invoices
            net_amount = daily_rate * days
            vat_amount = net_amount * 0.20
            total_amount = net_amount + vat_amount
            
            # Get next invoice number
            next_number = self._get_next_icbc_invoice_number()
            
            # Get the same PO number from the most recent ICBC invoice
            po_number = self._get_current_icbc_po_number()
            
            # Create invoice data with all required fields
            invoice_data = {
                'reference': f'ICBC STANDARD BANK PLC {next_number:03d}',
                'dated_on': f'{year}-{month:02d}-{28 if month == 2 else 30}',  # End of month
                'due_on': f'{year if month < 12 else year+1}-{month+1 if month < 12 else 1:02d}-{28 if month == 11 else 30:02d}',  # 30 days later
                'po_reference': po_number,
                'comments': f'Consultancy for {self._get_month_name(month)} {year} - Gavin Slater',
                'invoice_items': [
                    {
                        'description': f'Consultancy for {self._get_month_name(month)} {year} - Gavin Slater',
                        'quantity': str(float(days)),
                        'price': str(daily_rate),
                        'sales_tax_rate': '20.0',
                        'item_type': 'Days'
                    }
                ],
                'currency': 'GBP',
                'exchange_rate': '1.0',
                'payment_terms_in_days': 30
            }
            
            # Store this calculation for potential actual creation
            self.last_icbc_calculation = {
                'invoice_data': invoice_data,
                'calculation': {
                    'days': days,
                    'daily_rate': daily_rate,
                    'net_amount': net_amount,
                    'vat_amount': vat_amount,
                    'total_amount': total_amount
                }
            }
            
            return {
                'success': True,
                'action': 'create_icbc_invoice',
                'message': f'ICBC invoice calculated for {self._get_month_name(month)} {year} ({days} days)',
                'data': {
                    'invoice_preview': invoice_data,
                    'calculation': {
                        'days': days,
                        'daily_rate': daily_rate,
                        'net_amount': net_amount,
                        'vat_amount': vat_amount,
                        'total_amount': total_amount
                    },
                    'next_step': 'Use "create actual ICBC invoice" to create this in FreeAgent'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating ICBC invoice: {str(e)}',
                'error': str(e)
            }
    
    def _handle_create_actual_icbc_invoice(self) -> Dict[str, Any]:
        """Handle creating the actual ICBC invoice in FreeAgent."""
        try:
            if not self.last_icbc_calculation:
                return {
                    'success': False,
                    'message': 'No ICBC invoice calculation found. Please run "create ICBC invoice" first.',
                    'action_required': 'calculate_first'
                }
            
            invoice_data = self.last_icbc_calculation['invoice_data']
            calculation = self.last_icbc_calculation['calculation']
            
            # Create the actual invoice using existing method
            result = self.create_actual_invoice(invoice_data)
            
            if result['success']:
                # Clear the stored calculation after successful creation
                self.last_icbc_calculation = None
                
                created_invoice = result['data']
                
                # Safely format currency values
                def safe_currency_format(value):
                    try:
                        if isinstance(value, str):
                            # If it's already a string, try to parse it as float first
                            return f"£{float(value):,.2f}"
                        else:
                            return f"£{float(value):,.2f}"
                    except (ValueError, TypeError):
                        return str(value)  # Return as-is if formatting fails
                
                return {
                    'success': True,
                    'action': 'create_actual_icbc_invoice',
                    'message': f'✅ ICBC invoice {created_invoice.get("reference")} created successfully in FreeAgent!',
                    'data': {
                        'invoice': created_invoice,
                        'calculation_summary': {
                            'days': calculation['days'],
                            'daily_rate': f"£{calculation['daily_rate']:,.2f}",
                            'net_amount': f"£{calculation['net_amount']:,.2f}",
                            'vat_amount': f"£{calculation['vat_amount']:,.2f}",
                            'total_amount': f"£{calculation['total_amount']:,.2f}"
                        },
                        'invoice_details': {
                            'id': created_invoice.get('id'),
                            'reference': created_invoice.get('reference'),
                            'status': created_invoice.get('status'),
                            'total_value': safe_currency_format(created_invoice.get('total_value', 0)),
                            'due_value': safe_currency_format(created_invoice.get('due_value', 0)),
                            'url': created_invoice.get('url')
                        }
                    }
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating actual ICBC invoice: {str(e)}',
                'error': str(e)
            }
    
    def _handle_create_monthly_invoice(self, match: re.Match, original_command: str) -> Dict[str, Any]:
        """Handle creating a monthly consulting invoice."""
        try:
            # This is a more generic monthly invoice handler
            return {
                'success': True,
                'action': 'create_monthly_invoice',
                'message': 'Monthly invoice creation requires specific client details',
                'data': {
                    'supported_clients': ['ICBC', 'ICBC Standard Bank'],
                    'example_commands': [
                        'create ICBC invoice for July 2025 14 days',
                        'draft invoice for ICBC Standard Bank'
                    ]
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating monthly invoice: {str(e)}',
                'error': str(e)
            }
    
    def create_actual_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create the actual invoice in FreeAgent."""
        try:
            # First, we need to get the contact URL for ICBC
            # This requires finding the contact in FreeAgent
            contacts = self._get_contacts()
            icbc_contact = None
            
            for contact in contacts:
                org_name = contact.get('organisation_name', contact.get('organisation', '')).upper()
                if 'ICBC' in org_name or 'STANDARD BANK' in org_name:
                    icbc_contact = contact.get('url')
                    break
                    
            if not icbc_contact:
                return {
                    'success': False,
                    'message': 'ICBC contact not found in FreeAgent. Please add ICBC Standard Bank as a contact first.',
                    'action': 'contact_required'
                }
            
            # Add contact to invoice data
            invoice_data['contact'] = icbc_contact
            
            # Add payment terms (30 days default)
            invoice_data['payment_terms_in_days'] = 30
            
            # Update invoice reference with the next sequential number
            fresh_number = self._get_next_icbc_invoice_number()
            invoice_data['reference'] = f'ICBC STANDARD BANK PLC {fresh_number:03d}'
            
            # Invoice reference updated to use proper sequence
            
            # Create the invoice using the invoice manager
            new_invoice = self.invoice_manager.create_invoice(invoice_data)
            
            return {
                'success': True,
                'action': 'invoice_created',
                'message': f'Invoice {new_invoice.get("reference")} created successfully',
                'data': new_invoice
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating invoice in FreeAgent: {str(e)}',
                'error': str(e)
            }
    
    def _get_contacts(self) -> List[Dict[str, Any]]:
        """Get all contacts from FreeAgent."""
        try:
            all_contacts = []
            page = 1
            per_page = 100
            
            while True:
                # Use the protected _make_request method which handles token refresh
                response = self.client._make_request('GET', f'/contacts', params={'page': page, 'per_page': per_page})
                data = response.json()
                contacts = data.get('contacts', [])
                
                if not contacts:
                    break
                    
                all_contacts.extend(contacts)
                
                # Check if there are more pages
                if len(contacts) < per_page:
                    break
                    
                page += 1
                
            return all_contacts
        except Exception as e:
            print(f"Error getting contacts: {e}")
            return []
    
    def _get_next_icbc_invoice_number(self) -> int:
        """Get the next ICBC invoice number by checking ALL invoices."""
        try:
            # Get ALL invoices using pagination to ensure we see everything
            all_invoices = []
            page = 1
            per_page = 100
            
            while True:
                response = self.client._make_request('GET', f'/invoices?page={page}&per_page={per_page}')
                data = response.json()
                invoices = data.get('invoices', [])
                
                if not invoices:
                    break
                    
                all_invoices.extend(invoices)
                
                # Check if there are more pages
                if len(invoices) < per_page:
                    break
                    
                page += 1
            
            # Also try with view=all parameter to get everything
            try:
                all_view_response = self.client._make_request('GET', '/invoices?view=all')
                all_view_invoices = all_view_response.json().get('invoices', [])
                
                # Combine and deduplicate by ID
                invoice_ids = {inv.get('id') for inv in all_invoices}
                for invoice in all_view_invoices:
                    if invoice.get('id') not in invoice_ids:
                        all_invoices.append(invoice)
            except:
                pass  # Continue with what we have if view=all fails
            
            # Find highest ICBC invoice number
            max_number = 0
            icbc_refs_found = []
            
            for invoice in all_invoices:
                ref = invoice.get('reference', '')
                if 'ICBC STANDARD BANK PLC' in ref:
                    icbc_refs_found.append(ref)
                    import re
                    number_match = re.search(r'(\d+)$', ref)
                    if number_match:
                        number = int(number_match.group(1))
                        max_number = max(max_number, number)
            
            # Optionally log debug info
            # print(f"DEBUG: Found {len(icbc_refs_found)} ICBC invoices, highest number: {max_number}")
                        
            return max_number + 1
            
        except Exception as e:
            # Fallback to a safe number if API call fails
            return 20  # Safe fallback - higher than what we see in screenshot
    
    def _get_current_icbc_po_number(self) -> str:
        """Get the current PO number from the most recent ICBC invoice."""
        try:
            # Get recent invoices to find the latest ICBC PO number
            response = self.client._make_request('GET', '/invoices')
            invoices = response.json().get('invoices', [])
            
            # Find the most recent ICBC invoice with a PO number
            for invoice in invoices:
                ref = invoice.get('reference', '')
                if 'ICBC STANDARD BANK PLC' in ref:
                    po_ref = invoice.get('po_reference')
                    if po_ref and po_ref.startswith('PO32'):  # Look for the current PO32xxx series
                        return po_ref
            
            # Use the current PO number from screenshot
            return "PO32334"
            
        except Exception as e:
            # Fallback to known PO number if API call fails
            return "PO32334"  # Default from screenshot
    
    def _get_month_name(self, month: int) -> str:
        """Get month name from month number."""
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        return months[month] if 1 <= month <= 12 else 'Unknown'
            
    def _calculate_days_overdue(self, due_date_str: str) -> int:
        """Calculate days overdue from due date string."""
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            today = datetime.now().date()
            return (today - due_date).days
        except:
            return 0
            
    def _get_command_suggestions(self) -> List[str]:
        """Get list of available commands."""
        return [
            "list invoices",
            "show overdue invoices", 
            "show unpaid invoices",
            "what's the total outstanding",
            "invoice summary",
            "create invoice",
            "create ICBC invoice for July 2025 14 days",
            "create actual ICBC invoice",
            "draft invoice for ICBC",
            "send invoice [ID]",
            "mark invoice [ID] paid",
            "show invoice [ID]"
        ]
        
    def _check_authentication(self) -> Dict[str, Any]:
        """Check authentication status and handle re-authentication if needed."""
        try:
            # Try to ensure we're properly authenticated
            self.client.ensure_authenticated()
            return {'success': True, 'message': 'Authentication verified'}
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if 'refresh' in error_msg or 'expired' in error_msg:
                return {
                    'success': False,
                    'message': '🔄 Authentication tokens have expired. Please run the setup command to re-authenticate.',
                    'error_type': 'token_expired',
                    'action_required': 'run_setup',
                    'setup_command': 'python cli.py --setup'
                }
            elif 'authenticate' in error_msg:
                return {
                    'success': False,
                    'message': '🔐 Authentication required. Please run the setup command to authenticate with FreeAgent.',
                    'error_type': 'not_authenticated', 
                    'action_required': 'run_setup',
                    'setup_command': 'python cli.py --setup'
                }
            else:
                return {
                    'success': False,
                    'message': f'❌ Authentication error: {str(e)}',
                    'error_type': 'authentication_error',
                    'action_required': 'check_config',
                    'suggestion': 'Please check your FreeAgent configuration and try again.'
                }
    
    def check_authentication_status(self) -> Dict[str, Any]:
        """Get detailed authentication status for debugging."""
        try:
            status = self.client.check_authentication_status()
            return {
                'success': True,
                'message': 'Authentication status retrieved',
                'data': status
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error checking authentication: {str(e)}',
                'error': str(e)
            }
    
    def attempt_token_refresh(self) -> Dict[str, Any]:
        """Manually attempt to refresh authentication tokens."""
        try:
            if not self.client.refresh_token:
                return {
                    'success': False,
                    'message': 'No refresh token available. Full re-authentication required.',
                    'action_required': 'run_setup'
                }
            
            self.client.refresh_access_token()
            return {
                'success': True,
                'message': '✅ Authentication tokens refreshed successfully',
                'data': {
                    'access_token_available': bool(self.client.access_token),
                    'refresh_token_available': bool(self.client.refresh_token),
                    'token_expires_at': self.client.token_expires_at.isoformat() if self.client.token_expires_at else None
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Token refresh failed: {str(e)}',
                'error': str(e),
                'action_required': 'run_setup',
                'setup_command': 'python cli.py --setup'
            }

    def get_help(self) -> str:
        """Return help text with available commands."""
        suggestions = self._get_command_suggestions()
        help_text = "Available FreeAgent Invoice Commands:\n\n"
        for i, cmd in enumerate(suggestions, 1):
            help_text += f"{i}. {cmd}\n"
            
        help_text += "\nAuthentication Commands:\n"
        help_text += "- 'check auth status' - Check authentication status\n"
        help_text += "- 'refresh tokens' - Manually refresh authentication tokens\n"
        help_text += "\nExamples:\n"
        help_text += "- 'list invoices' - Show recent invoices\n"
        help_text += "- 'show overdue invoices' - List overdue invoices\n"  
        help_text += "- 'create ICBC invoice for July 2025 14 days' - Create ICBC consulting invoice\n"
        help_text += "- 'create actual ICBC invoice' - Actually create calculated ICBC invoice in FreeAgent\n"
        help_text += "- 'draft invoice for ICBC' - Create ICBC invoice draft\n"
        help_text += "- 'send invoice 123' - Send invoice with ID 123\n"
        help_text += "- 'mark invoice 123 paid' - Mark invoice as paid\n"
        
        help_text += "\nTroubleshooting:\n"
        help_text += "- If you get authentication errors, run: python cli.py --setup\n"
        help_text += "- For token refresh issues, run: 'refresh tokens' command\n"
        
        return help_text