# FreeAgent Sub-Agent System

## Project Overview
This directory contains a comprehensive FreeAgent API integration system providing natural language interface for invoice management and financial operations. Built specifically for Gavin's Bright Slate Limited business operations with ICBC Standard Bank.

## System Architecture

### Layered Design
- **`InvoiceSubAgent`** - Natural language command processing (high-level)
- **`InvoiceManager`** - Invoice CRUD operations (mid-level)
- **`FreeAgentClient`** - HTTP API client with OAuth (low-level)
- **`FreeAgentConfig`** - Configuration and credential management

### Core Files Structure
```
freeagent_subagent/
├── invoice_subagent.py         # Natural language interface
├── invoice_manager.py          # Invoice CRUD operations
├── freeagent_client.py         # Low-level API client
├── config.py                   # Configuration management
├── cli.py                      # Command-line interface
├── venv/                       # Python virtual environment
└── requirements.txt            # Dependencies: requests only
```

## Business Context

### Production Account Details
- **Business**: Bright Slate Limited (Gavin's contracting company)
- **Primary Client**: ICBC Standard Bank
- **Billing Pattern**: Monthly invoicing, £1,700/day rate
- **Payment Terms**: 14 days for ICBC, varies for other clients
- **Invoice Sequence**: Currently 016-018 range
- **Outstanding**: ~£152K+ across multiple invoices

### ICBC Automation Features
- **PO Detection**: Automatically finds PO numbers (e.g., PO32334) from historical invoices
- **Rate Application**: Uses £1,700/day rate from historical analysis
- **Sequence Management**: Maintains proper invoice numbering progression
- **Terms Application**: Automatically applies 14-day payment terms for ICBC

## Authentication & Configuration

### OAuth Setup
- **App Name**: "FreeAgent AI Agent"
- **Client ID**: `970GvhTqju_QFVpCf3vpLw`
- **Config Location**: `~/.config/freeagent/config.json`
- **Token Management**: Automatic refresh, production-ready
- **Environment Variables**: `FREEAGENT_CLIENT_ID`, `FREEAGENT_CLIENT_SECRET`

### Configuration Management
- **Auto-refresh**: OAuth tokens refreshed automatically
- **Production Mode**: Successfully tested with real financial transactions
- **Error Handling**: Graceful OAuth token refresh and retry logic
- **Rate Limiting**: 60 requests/minute with exponential backoff

## Natural Language Processing

### Command Patterns
**Supported regex patterns for natural language commands:**
- `"list invoices"` - Display all invoices with pagination
- `"show overdue invoices"` - Filter overdue invoices only
- `"total outstanding"` - Calculate sum of unpaid invoices
- `"create ICBC invoice for July 2025 14 days"` - Automated ICBC invoice creation
- `"show unpaid invoices"` - Filter invoices by payment status

### Smart Invoice Creation
- **ICBC Detection**: Recognizes ICBC-related commands and applies automation
- **Date Processing**: Interprets natural language dates (e.g., "July 2025")
- **Rate Application**: Automatically applies correct daily rates
- **PO Assignment**: Searches historical data for relevant PO numbers

## Development Usage

### Primary Integration (Agent-based)
```python
from freeagent_subagent import create_subagent
subagent = create_subagent()
result = subagent.process_command("show unpaid invoices")
print(result)
```

### CLI Interface
```bash
cd freeagent_subagent
python -m freeagent_subagent.cli "list invoices"
python -m freeagent_subagent.cli --setup  # Configuration wizard
```

### Virtual Environment Setup
```bash
cd freeagent_subagent
source venv/bin/activate
pip install -r requirements.txt
```

## Agent Integration

### Agent Delegation
- **Primary Agent**: FreeAgent Invoice Agent (`freeagent-invoice-agent`)
- **Trigger Patterns**: Financial queries, invoice management, payment tracking
- **Context Loading**: Auto-loads business context and authentication state

### Response Format
- **Natural Language**: Human-readable summaries of financial status
- **Structured Data**: JSON-formatted invoice details when needed
- **Error Handling**: Clear error messages with suggested remediation
- **Progress Tracking**: Integration with quantified self financial goals

## Production Validation

### Real-World Testing
- **Live Account**: Successfully tested with Bright Slate Limited production account
- **Invoice Creation**: Created real invoices (ICBC 016-018 sequence)
- **Payment Tracking**: Monitors actual payment cycles and outstanding amounts
- **OAuth Stability**: Handles token refresh cycles in production environment

### Financial Accuracy
- **Rate Verification**: £1,700/day rate confirmed from historical data
- **PO Mapping**: PO numbers validated against actual ICBC patterns
- **Sequence Integrity**: Invoice numbering maintains business continuity
- **Payment Terms**: 14-day terms properly applied for ICBC invoices

## Security Considerations

### OAuth Security
- **Production-grade**: OAuth 2.0 implementation following FreeAgent guidelines
- **Credential Storage**: Secure config file with appropriate permissions
- **Token Refresh**: Automatic renewal without manual intervention
- **API Rate Limiting**: Respects FreeAgent API limits with exponential backoff

### Data Protection
- **Local Storage**: All financial data processed locally
- **API Security**: HTTPS-only communication with FreeAgent
- **No Persistence**: Sensitive data not permanently stored beyond config
- **Access Control**: Configuration files protected with appropriate permissions

## Error Handling & Troubleshooting

### Common Issues
- **Authentication Errors**: Use OAuth Playground for token setup verification
- **Rate Limiting**: Built-in exponential backoff handles automatically
- **Invoice Creation Failures**: Check contact mapping and required field validation
- **Config Issues**: Run `--setup` command for guided configuration

### Debugging
- **Verbose Mode**: CLI supports detailed logging for troubleshooting
- **Token Validation**: Built-in token expiry detection and refresh
- **API Response Handling**: Comprehensive error message interpretation
- **Network Issues**: Automatic retry with backoff for transient failures

## Performance Characteristics

### Response Times
- **Invoice Listing**: 1-2 seconds (with pagination)
- **Invoice Creation**: 2-3 seconds per invoice
- **OAuth Refresh**: Automatic, transparent to user
- **Batch Operations**: Efficient handling of multiple invoice operations

### Scalability
- **Rate Limiting**: 60 requests/minute with exponential backoff
- **Pagination**: Handles large invoice lists efficiently
- **Memory Usage**: Minimal memory footprint for long-running operations
- **Connection Pooling**: Efficient API connection management

This system provides a production-ready, natural language interface to FreeAgent's accounting system, specifically optimized for Gavin's business operations and integrated with his broader Personal AI Infrastructure.