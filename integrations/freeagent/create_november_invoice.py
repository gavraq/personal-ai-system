#!/usr/bin/env python3
"""
Create ICBCS invoice for November 2025 with 22 working days.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from freeagent_client import FreeAgentClient
from invoice_subagent import InvoiceSubAgent
from config import FreeAgentConfig

def main():
    # Initialize sub-agent
    print("Initializing FreeAgent sub-agent...\n")

    try:
        config = FreeAgentConfig()

        if not config.is_configured():
            print("❌ FreeAgent not configured. Please run: python cli.py --setup")
            return 1

        client_id, client_secret = config.get_client_credentials()
        client = FreeAgentClient(
            client_id=client_id,
            client_secret=client_secret,
            sandbox=config.is_sandbox()
        )

        # Set tokens if available
        access_token, refresh_token = config.get_tokens()
        if access_token and refresh_token:
            client.set_tokens(access_token, refresh_token)

        subagent = InvoiceSubAgent(client)

    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        return 1

    # Process command to create ICBC invoice
    print("Creating ICBCS invoice draft for November 2025 (22 days)...\n")

    # First, create the draft calculation
    result = subagent.process_command("create ICBC invoice for November 2025 22 days")

    if result['success']:
        print("✅ DRAFT INVOICE CALCULATED\n")

        # Display calculation details
        calc = result['data']['calculation']
        preview = result['data']['invoice_preview']

        print(f"Invoice Reference: {preview['reference']}")
        print(f"PO Number: {preview['po_reference']}")
        print(f"Invoice Date: {preview['dated_on']}")
        print(f"Due Date: {preview['due_on']}")
        print(f"Description: {preview['comments']}\n")

        print("CALCULATION SUMMARY:")
        print(f"  Days: {calc['days']}")
        print(f"  Daily Rate: £{calc['daily_rate']:,.2f}")
        print(f"  Net Amount: £{calc['net_amount']:,.2f}")
        print(f"  VAT (20%): £{calc['vat_amount']:,.2f}")
        print(f"  TOTAL: £{calc['total_amount']:,.2f}\n")

        # Ask for confirmation to create actual invoice
        print("=" * 60)
        response = input("\nCreate this invoice in FreeAgent? (yes/no): ")

        if response.lower() in ['yes', 'y']:
            print("\nCreating invoice in FreeAgent...")
            create_result = subagent.process_command("create actual ICBC invoice")

            if create_result['success']:
                print("\n✅ INVOICE CREATED SUCCESSFULLY!\n")

                invoice_details = create_result['data']['invoice_details']
                print(f"Invoice ID: {invoice_details['id']}")
                print(f"Reference: {invoice_details['reference']}")
                print(f"Status: {invoice_details['status']}")
                print(f"Total Value: {invoice_details['total_value']}")
                print(f"Due Value: {invoice_details['due_value']}")
                print(f"FreeAgent URL: {invoice_details['url']}\n")

                return 0
            else:
                print(f"\n❌ ERROR creating invoice: {create_result['message']}")
                return 1
        else:
            print("\nInvoice creation cancelled.")
            return 0
    else:
        print(f"❌ ERROR: {result['message']}")
        if 'error' in result:
            print(f"Details: {result['error']}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
