#!/usr/bin/env python3
"""
Create two ICBC invoices for October 2025:
1. Invoice with 9 days under PO32334
2. Invoice with 9 days under PO32906
"""

import sys
import json
from freeagent_client import FreeAgentClient
from invoice_subagent import InvoiceSubAgent
from config import FreeAgentConfig

def create_custom_icbc_invoice(subagent, days, month, year, po_number):
    """Create a custom ICBC invoice with specific PO number."""
    try:
        # Calculate invoice details
        daily_rate = 1700.00
        net_amount = daily_rate * days
        vat_amount = net_amount * 0.20
        total_amount = net_amount + vat_amount

        # Get next invoice number
        next_number = subagent._get_next_icbc_invoice_number()

        # Get ICBC contact
        contacts = subagent._get_contacts()
        icbc_contact = None

        for contact in contacts:
            org_name = contact.get('organisation_name', contact.get('organisation', '')).upper()
            if 'ICBC' in org_name or 'STANDARD BANK' in org_name:
                icbc_contact = contact.get('url')
                break

        if not icbc_contact:
            return {
                'success': False,
                'message': 'ICBC contact not found in FreeAgent'
            }

        # Determine date range for October 2025
        # First invoice: Oct 1-15 (using end date Oct 15)
        # Second invoice: Oct 16-31 (using end date Oct 31)
        if po_number == "PO32334":
            dated_on = f'{year}-{month:02d}-15'
            due_on = f'{year}-{month+1:02d}-14'  # 30 days later
            period_desc = f"October 2025 (Period 1) - Gavin Slater"
        else:  # PO32906
            dated_on = f'{year}-{month:02d}-31'
            due_on = f'{year}-{month+1:02d}-30'  # 30 days later
            period_desc = f"October 2025 (Period 2) - Gavin Slater"

        # Create invoice data
        invoice_data = {
            'contact': icbc_contact,
            'reference': f'ICBC STANDARD BANK PLC {next_number:03d}',
            'dated_on': dated_on,
            'due_on': due_on,
            'po_reference': po_number,
            'comments': f'Consultancy for {period_desc}',
            'invoice_items': [
                {
                    'description': f'Consultancy for {period_desc}',
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

        print(f"\nCreating invoice with PO {po_number}:")
        print(f"  Reference: {invoice_data['reference']}")
        print(f"  Date: {dated_on}")
        print(f"  Days: {days}")
        print(f"  Net: £{net_amount:,.2f}")
        print(f"  VAT (20%): £{vat_amount:,.2f}")
        print(f"  Total: £{total_amount:,.2f}")

        # Create the invoice
        new_invoice = subagent.invoice_manager.create_invoice(invoice_data)

        return {
            'success': True,
            'invoice': new_invoice,
            'calculation': {
                'days': days,
                'net_amount': net_amount,
                'vat_amount': vat_amount,
                'total_amount': total_amount
            }
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Error creating invoice: {str(e)}',
            'error': str(e)
        }

def main():
    """Main execution."""
    print("=" * 80)
    print("ICBC October 2025 Invoice Creation")
    print("=" * 80)

    # Initialize configuration and client
    config = FreeAgentConfig()

    if not config.is_configured():
        print("❌ FreeAgent not configured. Please run setup first.")
        sys.exit(1)

    client_id, client_secret = config.get_client_credentials()
    client = FreeAgentClient(
        client_id=client_id,
        client_secret=client_secret,
        sandbox=config.is_sandbox()
    )

    # Set tokens
    access_token, refresh_token = config.get_tokens()
    if access_token and refresh_token:
        client.set_tokens(access_token, refresh_token)

    # Create sub-agent
    subagent = InvoiceSubAgent(client)

    # Check authentication
    print("\nChecking authentication...")
    try:
        subagent.client.ensure_authenticated()
        print("✅ Authentication verified")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)

    # Create Invoice 1 - 9 days under PO32334
    print("\n" + "=" * 80)
    print("Creating Invoice 1: 9 days under PO32334")
    print("=" * 80)

    result1 = create_custom_icbc_invoice(
        subagent=subagent,
        days=9,
        month=10,  # October
        year=2025,
        po_number="PO32334"
    )

    if result1['success']:
        invoice1 = result1['invoice']
        calc1 = result1['calculation']
        print(f"\n✅ Invoice 1 created successfully!")
        print(f"   Reference: {invoice1.get('reference')}")
        print(f"   Status: {invoice1.get('status')}")
        print(f"   Total: £{calc1['total_amount']:,.2f}")
        print(f"   URL: {invoice1.get('url')}")
    else:
        print(f"\n❌ Failed to create Invoice 1: {result1.get('message')}")
        sys.exit(1)

    # Create Invoice 2 - 9 days under PO32906
    print("\n" + "=" * 80)
    print("Creating Invoice 2: 9 days under PO32906")
    print("=" * 80)

    result2 = create_custom_icbc_invoice(
        subagent=subagent,
        days=9,
        month=10,  # October
        year=2025,
        po_number="PO32906"
    )

    if result2['success']:
        invoice2 = result2['invoice']
        calc2 = result2['calculation']
        print(f"\n✅ Invoice 2 created successfully!")
        print(f"   Reference: {invoice2.get('reference')}")
        print(f"   Status: {invoice2.get('status')}")
        print(f"   Total: £{calc2['total_amount']:,.2f}")
        print(f"   URL: {invoice2.get('url')}")
    else:
        print(f"\n❌ Failed to create Invoice 2: {result2.get('message')}")
        sys.exit(1)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n✅ Successfully created 2 ICBC invoices for October 2025")
    print(f"\nInvoice 1 (PO32334):")
    print(f"  Reference: {invoice1.get('reference')}")
    print(f"  Days: {calc1['days']}")
    print(f"  Total: £{calc1['total_amount']:,.2f}")
    print(f"\nInvoice 2 (PO32906):")
    print(f"  Reference: {invoice2.get('reference')}")
    print(f"  Days: {calc2['days']}")
    print(f"  Total: £{calc2['total_amount']:,.2f}")
    print(f"\nCombined Total: £{calc1['total_amount'] + calc2['total_amount']:,.2f}")
    print("=" * 80)

if __name__ == '__main__':
    main()
