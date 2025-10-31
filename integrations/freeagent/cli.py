"""
Command line interface for FreeAgent Sub-Agent.
"""

import argparse
import sys
import json
from typing import Dict, Any

# Handle both package and standalone imports
try:
    from . import create_subagent, FreeAgentConfig, ConfigHelper
except ImportError:
    # Running as standalone script - import components directly
    from freeagent_client import FreeAgentClient
    from invoice_subagent import InvoiceSubAgent
    from config import FreeAgentConfig, ConfigHelper
    
    def create_subagent(config=None):
        """Standalone version of create_subagent function."""
        if config is None:
            config = FreeAgentConfig()
            
        if not config.is_configured():
            raise ValueError(
                "FreeAgent not configured. Please set up your credentials first."
            )
            
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
            
        return InvoiceSubAgent(client)


def format_output(result: Dict[str, Any], format_type: str = 'human') -> str:
    """Format output based on specified format."""
    if format_type == 'json':
        return json.dumps(result, indent=2, default=str)
    
    # Human-readable format
    if not result.get('success', False):
        return f"❌ Error: {result.get('message', 'Unknown error')}"
        
    message = result.get('message', '')
    data = result.get('data', {})
    
    output = f"✅ {message}\n"
    
    # Handle different data types
    if isinstance(data, list) and data:
        if result.get('action') == 'list_invoices':
            output += "\nInvoices:\n"
            for inv in data:
                output += f"  📄 #{inv.get('id')} - {inv.get('reference')} - {inv.get('status')} - £{inv.get('total', 0)}\n"
        elif result.get('action') == 'list_overdue':
            output += "\nOverdue Invoices:\n"
            for inv in data:
                output += f"  ⚠️  #{inv.get('id')} - {inv.get('reference')} - {inv.get('days_overdue')} days - £{inv.get('due_amount', 0)}\n"
        elif result.get('action') == 'list_unpaid':
            output += "\nUnpaid Invoices:\n" 
            for inv in data:
                output += f"  💰 #{inv.get('id')} - {inv.get('reference')} - Due: {inv.get('due_date')} - £{inv.get('due_amount', 0)}\n"
                
    elif isinstance(data, dict):
        if result.get('action') == 'invoice_summary':
            status_counts = data.get('status_counts', {})
            total = data.get('total_outstanding', 0)
            output += f"\nInvoice Summary:\n"
            output += f"  📝 Draft: {status_counts.get('draft', 0)}\n"
            output += f"  📤 Sent: {status_counts.get('sent', 0)}\n" 
            output += f"  ✅ Paid: {status_counts.get('paid', 0)}\n"
            output += f"  ⚠️  Overdue: {status_counts.get('overdue', 0)}\n"
            output += f"  💰 Total Outstanding: £{total:.2f}\n"
            
        elif result.get('action') == 'total_outstanding':
            total = data.get('total_outstanding', 0)
            output += f"💰 Total Outstanding: £{total:.2f}\n"
            
    return output


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FreeAgent Invoice Sub-Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "list invoices"
  %(prog)s "show overdue invoices"
  %(prog)s "what's the total outstanding"
  %(prog)s "send invoice 123"
  %(prog)s --setup
  %(prog)s --config-info
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        help='Natural language command to execute'
    )
    
    parser.add_argument(
        '--format',
        choices=['human', 'json'],
        default='human',
        help='Output format (default: human)'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Run interactive configuration setup'
    )
    
    parser.add_argument(
        '--config-info',
        action='store_true', 
        help='Show current configuration status'
    )
    
    parser.add_argument(
        '--env-template',
        action='store_true',
        help='Show environment variables template'
    )
    
    parser.add_argument(
        '--help-commands',
        action='store_true',
        help='Show available commands'
    )
    
    args = parser.parse_args()
    
    # Handle setup and info commands
    if args.setup:
        ConfigHelper.setup_interactive()
        return
        
    if args.env_template:
        ConfigHelper.print_env_template()
        return
        
    if args.config_info:
        config = FreeAgentConfig()
        summary = config.get_summary()
        print("FreeAgent Configuration Status:")
        print("=" * 35)
        for key, value in summary.items():
            status = "✅" if value else "❌"
            print(f"{status} {key.replace('_', ' ').title()}: {value}")
        return
        
    if args.help_commands:
        try:
            subagent = create_subagent()
            print(subagent.get_help())
        except Exception as e:
            print(f"Error: {e}")
            print("Please configure the sub-agent first using --setup")
        return
        
    # Handle regular commands
    if not args.command:
        parser.print_help()
        return
        
    try:
        # Create sub-agent
        subagent = create_subagent()
        
        # Process command
        result = subagent.process_command(args.command)
        
        # Format and print output
        output = format_output(result, args.format)
        print(output)
        
        # Exit with error code if command failed
        if not result.get('success', False):
            sys.exit(1)
            
    except Exception as e:
        if args.format == 'json':
            error_result = {
                'success': False,
                'message': str(e),
                'error': str(e)
            }
            print(json.dumps(error_result, indent=2))
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()