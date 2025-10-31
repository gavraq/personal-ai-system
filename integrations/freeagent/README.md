# FreeAgent Invoice Sub-Agent

A Python library that provides a natural language interface for managing FreeAgent invoices through their API.

## Features

- **Natural Language Commands**: Control your invoices using conversational commands
- **Enhanced Automatic Re-Authentication**: 🆕 Smart OAuth token management with automatic refresh and retry logic
- **Seamless Authentication Recovery**: 🆕 Automatically handles expired tokens with zero user intervention
- **Authentication Commands**: 🆕 Built-in commands to check and refresh authentication status
- **Complete Invoice Creation**: Handles all invoice details including PO numbers, units, VAT calculations
- **Intelligent Sequence Management**: Maintains proper invoice numbering with gap detection
- **Rate Limiting**: Built-in rate limiting and retry logic with exponential backoff
- **Comprehensive Error Handling**: Custom exceptions with intelligent recovery suggestions
- **CLI Interface**: Command-line tool for quick operations
- **Configuration Management**: Flexible configuration via files or environment variables

## Installation

```bash
# Clone or copy the freeagent_subagent directory to your project
pip install requests  # Only dependency
```

## Quick Start

### 1. Configure API Credentials

**IMPORTANT**: This sub-agent has been successfully tested with the existing "FreeAgent AI Agent" app credentials. You can reuse these working credentials:

- **Client ID**: `970GvhTqju_QFVpCf3vpLw`
- **Client Secret**: `xPbMcBYC9ShPJTyPxu3uTw`
- **App Name**: FreeAgent AI Agent
- **Mode**: Production (not sandbox)

#### Option A: Use Working Credentials
```python
from freeagent_subagent import FreeAgentConfig

config = FreeAgentConfig()
config.set('client_id', '970GvhTqju_QFVpCf3vpLw')
config.set('client_secret', 'xPbMcBYC9ShPJTyPxu3uTw')
config.set('sandbox', False)  # Production mode
config.save_config()
```

#### Option B: Environment Variables  
```bash
export FREEAGENT_CLIENT_ID="970GvhTqju_QFVpCf3vpLw"
export FREEAGENT_CLIENT_SECRET="xPbMcBYC9ShPJTyPxu3uTw"
export FREEAGENT_SANDBOX="false"  # Production mode
```

### 2. Authorize Your Application

**RECOMMENDED**: Use the pre-configured OAuth Playground for quick setup:

1. **Visit this pre-configured OAuth Playground URL**:
```
https://developers.google.com/oauthplayground/#step1&scopes=claude_code_subagent&url=https%3A%2F%2Fapi.freeagent.com%2Fv2%2Fcompany&content_type=application%2Fjson&http_method=GET&useDefaultOauthCred=unchecked&oauthEndpointSelect=Custom&oauthAuthEndpointValue=https%3A%2F%2Fapi.freeagent.com%2Fv2%2Fapprove_app&oauthTokenEndpointValue=https%3A%2F%2Fapi.freeagent.com%2Fv2%2Ftoken_endpoint&includeCredentials=unchecked&accessTokenType=bearer&autoRefreshToken=checked&accessType=offline&prompt=consent&response_type=code&wrapLines=on
```

2. **Configure OAuth Playground**:
   - Click gear/cog icon → "Use your own OAuth credentials"
   - OAuth Client ID: `970GvhTqju_QFVpCf3vpLw`
   - OAuth Client Secret: `xPbMcBYC9ShPJTyPxu3uTw`
   - Click "Close"

3. **Get Tokens**:
   - Step 1: Enter scope "claude_code_subagent" → "Authorize APIs"
   - Sign in to your FreeAgent production account
   - Step 2: "Exchange authorization code for tokens"
   - Copy both Access Token and Refresh Token

4. **Save Tokens**:
```python
from freeagent_subagent import FreeAgentConfig

config = FreeAgentConfig()
config.save_tokens('YOUR_ACCESS_TOKEN', 'YOUR_REFRESH_TOKEN')
```

### 3. Use the Sub-Agent

```python
from freeagent_subagent import create_subagent

# Create sub-agent (handles token refresh automatically)
subagent = create_subagent()

# Use natural language commands
result = subagent.process_command("list invoices")
print(result)

result = subagent.process_command("show overdue invoices")
print(result)

# Create invoices with complete details
result = subagent.process_command("create ICBC invoice for July 2025 14 days")
print(result)

# Check totals
result = subagent.process_command("what's the total outstanding")
print(result)

# 🆕 Enhanced authentication management
result = subagent.process_command("check auth status")
print(result)  # Detailed authentication status

# Automatic token refresh happens seamlessly during any command
```

## 🆕 Enhanced Authentication System

The FreeAgent sub-agent now includes comprehensive authentication management that handles OAuth token lifecycle automatically.

### Automatic Re-Authentication

**Zero-Intervention Token Management**: When your access token expires, the system automatically refreshes it and retries the failed request.

```python
# This happens automatically - no user action required
subagent = create_subagent()

# If token expires during this request, it's automatically refreshed
result = subagent.process_command("list invoices")
# ✅ Token refreshed successfully, retrying request...
# ✅ Command completed successfully
```

### Authentication Status Checking

**Detailed Status Information**: Check the health of your authentication setup.

```python
result = subagent.process_command("check auth status")
print(result['data'])
# Output: {
#   'has_access_token': True,
#   'has_refresh_token': True,
#   'token_expires_at': '2025-09-19T17:33:43.005416',
#   'is_expired': False,
#   'api_accessible': True,
#   'needs_refresh': False
# }
```

### Manual Token Refresh

**On-Demand Token Refresh**: Manually refresh tokens when needed.

```python
result = subagent.process_command("refresh tokens")
# ✅ Authentication tokens refreshed successfully
```

### Authentication Error Recovery

**Intelligent Error Handling**: Clear guidance when authentication issues occur.

```python
# When authentication fails, you get specific instructions:
{
  'success': False,
  'message': '🔄 Authentication tokens have expired. Please run the setup command to re-authenticate.',
  'error_type': 'token_expired',
  'action_required': 'run_setup',
  'setup_command': 'python cli.py --setup'
}
```

### Enhanced Client Methods

**Programmatic Authentication Management**: Use authentication methods directly.

```python
from freeagent_subagent import FreeAgentClient

client = FreeAgentClient(client_id, client_secret)
client.set_tokens(access_token, refresh_token)

# Check authentication status
status = client.check_authentication_status()
print(f"API accessible: {status['api_accessible']}")

# Ensure valid authentication (with automatic refresh)
client.ensure_authenticated()  # Throws exception if cannot authenticate

# Manual token refresh
client.refresh_access_token()
```

## Real-World Examples

### Invoice Management
```python
# Create and test the sub-agent (automatic token management)
subagent = create_subagent()

# Check unpaid invoices
result = subagent.process_command("show unpaid invoices")
print(result['message'])  # "Found 7 unpaid invoices"

# Query specific client invoices
result = subagent.process_command("tell me the ICBC Standard invoices that are unpaid")
# Returns: 2 invoices totaling £18,459.83
```

### Complete Invoice Creation with Full Automation
```python
# Create ICBC consulting invoice with all details - fully automated
result = subagent.process_command("create ICBC invoice for July 2025 14 days")

# Automatically creates draft invoice ICBC STANDARD BANK PLC 018:
print(result['message'])  # "ICBC invoice calculated for July 2025 (14 days)"

# Then create the actual invoice in FreeAgent
actual_result = subagent.create_actual_invoice(result['data']['invoice_preview'])
print(actual_result['message'])  # "Invoice ICBC STANDARD BANK PLC 018 created successfully"

# Final result: ICBC STANDARD BANK PLC 018 with:
# - PO Number: PO32334 (automatic detection from existing invoices)
# - Daily Rate: £1,700.00 (from historical rate analysis)  
# - Units: "Days" (proper API field: item_type)
# - Net Amount: £23,800.00 (14 × £1,700)
# - VAT: £4,760.00 (20%)
# - Total: £28,560.00
# - Description: "Consultancy for July 2025 - Gavin Slater"
# - Sequence: Automatically detected next number (018)
```

**Production Results**:
- ✅ Successfully connected to BRIGHT SLATE LTD production account
- ✅ Retrieved 25 total invoices with complete pagination
- ✅ Identified 7 unpaid invoices worth £152,879.03
- ✅ Created real invoices with proper sequencing (016, 017, 018)
- ✅ 🆕 Enhanced automatic OAuth token refresh with intelligent retry logic
- ✅ 🆕 Zero-downtime authentication recovery during expired token scenarios
- ✅ 🆕 Authentication status monitoring and manual refresh capabilities
- ✅ Complete invoice creation with all FreeAgent fields populated

## Available Commands

### Listing Commands
- `"list invoices"` - Show recent invoices
- `"show overdue invoices"` - List overdue invoices
- `"show unpaid invoices"` - List unpaid invoices
- `"invoice summary"` - Get overview of all invoices

### Invoice Actions
- `"send invoice 123"` - Send invoice by ID
- `"mark invoice 123 paid"` - Mark invoice as paid
- `"show invoice 123"` - Get invoice details

### Invoice Creation (Automated)
- `"create ICBC invoice for July 2025 14 days"` - Create ICBC consulting invoice
- `"draft invoice for ICBC Standard"` - Create ICBC draft invoice
- `"create invoice"` - Get invoice creation guidance
- **Note**: Includes automatic PO detection (PO32334), correct daily rate (£1,700), proper units ("Days"), and sequential invoice numbering

### Information Commands
- `"what's the total outstanding"` - Calculate total owed
- `"how much money am I owed"` - Same as above

### 🆕 Authentication Commands
- `"check auth status"` - Check detailed authentication status
- `"refresh tokens"` - Manually refresh OAuth tokens
- `"check tokens"` - Alias for authentication status check

## CLI Usage

The package includes a command-line interface:

```bash
# Setup configuration
python -m freeagent_subagent.cli --setup

# Check configuration status
python -m freeagent_subagent.cli --config-info

# Show available commands
python -m freeagent_subagent.cli --help-commands

# Execute commands
python -m freeagent_subagent.cli "list invoices"
python -m freeagent_subagent.cli "show overdue invoices"
python -m freeagent_subagent.cli "total outstanding"

# 🆕 Authentication management
python -m freeagent_subagent.cli "check auth status"
python -m freeagent_subagent.cli "refresh tokens"

# JSON output format
python -m freeagent_subagent.cli "list invoices" --format json

# Create invoices (fully automated with enhanced auth)
python -m freeagent_subagent.cli "create ICBC invoice for July 2025 14 days"
```

## Programmatic Usage

### Direct API Access

```python
from freeagent_subagent import FreeAgentClient, InvoiceManager

# Create client
client = FreeAgentClient(client_id, client_secret, sandbox=True)
client.set_tokens(access_token, refresh_token)

# Use invoice manager directly
invoice_manager = InvoiceManager(client)

# List invoices
invoices = invoice_manager.list_invoices(view='recent')

# Get overdue invoices
overdue = invoice_manager.get_overdue_invoices()

# Create invoice
new_invoice = invoice_manager.create_invoice({
    "contact": "https://api.sandbox.freeagent.com/v2/contacts/123",
    "dated_on": "2024-01-15",
    "due_on": "2024-02-15",
    "reference": "INV001",
    "invoice_items": [
        {
            "description": "Consulting services",
            "price": "100.00",
            "quantity": "8.0",
            "sales_tax_rate": "0.20"
        }
    ]
})

# Send invoice
invoice_manager.send_invoice(new_invoice['id'])
```

### Custom Invoice Operations

```python
# Get invoice as PDF
pdf_data = invoice_manager.get_invoice_pdf(invoice_id)
with open('invoice.pdf', 'wb') as f:
    f.write(pdf_data)

# Duplicate invoice
duplicate = invoice_manager.duplicate_invoice(original_id, new_date="2024-02-01")

# Calculate outstanding amount
total_outstanding = invoice_manager.calculate_total_outstanding()
```

## Configuration

### Configuration File Location
- `~/.config/freeagent/config.json` (Linux/macOS)
- Config file contains client credentials and tokens

### Environment Variables
```bash
FREEAGENT_CLIENT_ID        # Your app's client ID
FREEAGENT_CLIENT_SECRET    # Your app's client secret  
FREEAGENT_ACCESS_TOKEN     # OAuth access token (optional)
FREEAGENT_REFRESH_TOKEN    # OAuth refresh token (optional)
FREEAGENT_SANDBOX          # "true" for sandbox, "false" for production
FREEAGENT_REDIRECT_URI     # OAuth redirect URI
```

## Error Handling

The library includes comprehensive error handling:

```python
from freeagent_subagent import (
    AuthenticationError, 
    AuthorizationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    APIError
)

try:
    result = subagent.process_command("list invoices")
except AuthenticationError:
    print("Authentication failed - check your tokens")
except RateLimitError as e:
    print(f"Rate limited - retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e}")
```

## Rate Limiting

The client automatically handles rate limiting with:
- Maximum 60 requests per minute
- Automatic retry with exponential backoff
- Respect for API `Retry-After` headers

## Development

### Testing

The sub-agent works with FreeAgent's sandbox environment by default:

```python
# Always test in sandbox first
config = FreeAgentConfig()
config.set('sandbox', True)
```

### Extending Commands

To add new natural language commands:

```python
# Add pattern to InvoiceSubAgent.command_patterns
'new_command': [
    r'(?i)pattern to match',
]

# Add handler method
def _handle_new_command(self):
    # Implementation
    pass
```

## Package Structure

The FreeAgent sub-agent consists of several core components:

### File Overview

| File | Purpose | Level | Key Features |
|------|---------|-------|--------------|
| `__init__.py` | Package entry point | High | Exports, convenience functions |
| `invoice_subagent.py` | Natural language interface | High | Command processing, ICBC automation |
| `invoice_manager.py` | Invoice operations | Mid | CRUD operations, calculations |
| `freeagent_client.py` | API client | Low | OAuth, HTTP requests, rate limiting |
| `config.py` | Configuration management | Support | Credentials, tokens, persistence |
| `exceptions.py` | Error handling | Support | Custom exceptions, API errors |
| `cli.py` | Command-line interface | Interface | Terminal access, JSON output |
| `requirements.txt` | Dependencies | Support | Package requirements |
| `README.md` | Documentation | Support | Setup, usage, examples |

### Core Files

#### `__init__.py`
Package initialization and main exports. Provides the `create_subagent()` convenience function for quick setup.

```python
from freeagent_subagent import create_subagent
subagent = create_subagent()  # Auto-configures from config file/env
```

#### `freeagent_client.py`
Low-level FreeAgent API client handling OAuth authentication, token refresh, and HTTP requests.

**Key Features:**
- Automatic OAuth token refresh with config file persistence
- Rate limiting and retry logic with exponential backoff
- Comprehensive error handling for API responses
- Support for both sandbox and production environments

#### `invoice_manager.py`
Mid-level invoice operations providing structured access to FreeAgent invoice functionality.

**Key Operations:**
- List invoices with filtering (recent, overdue, unpaid)
- Create invoices with complete field validation
- Send invoices and mark as paid
- Calculate outstanding amounts and status summaries

#### `invoice_subagent.py` 
High-level natural language interface that processes conversational commands.

**Natural Language Processing:**
- Regex pattern matching for command interpretation
- Intelligent parsing of dates, amounts, and client names
- Automated invoice creation with historical data detection
- ICBC-specific invoice handling with PO/rate detection

#### `config.py`
Configuration management for API credentials, tokens, and settings.

**Configuration Sources:**
- JSON config file (`~/.config/freeagent/config.json`)
- Environment variables (`FREEAGENT_*`)
- Interactive setup wizard
- Automatic token persistence after refresh

#### `exceptions.py`
Custom exception classes for structured error handling.

**Exception Hierarchy:**
- `FreeAgentError` - Base exception
- `AuthenticationError` - Invalid credentials/tokens
- `AuthorizationError` - Permission denied
- `RateLimitError` - API rate limit exceeded
- `ValidationError` - Invalid request data
- `NotFoundError` - Resource not found
- `APIError` - General API errors

#### `cli.py`
Command-line interface for direct terminal usage.

**CLI Features:**
- Supports both package and standalone execution
- Human-readable and JSON output formats
- Interactive configuration setup
- Configuration status checking
- All natural language commands supported

### Supporting Files

#### `requirements.txt`
Python package dependencies. Only requires `requests` for HTTP operations.

```
requests>=2.28.0
```

#### `README.md`
Comprehensive documentation including setup, usage examples, and API reference.

#### `venv/` (Directory)
Python virtual environment containing isolated dependencies for development and testing.

### File Interactions

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     cli.py      │    │   __init__.py    │    │  External App   │
│  (CLI Interface)│    │ (Package Entry)  │    │   (Your Code)   │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────┐
                    │  invoice_subagent.py │
                    │ (Natural Language)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  invoice_manager.py  │
                    │ (Invoice Operations) │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ freeagent_client.py  │
                    │   (API Client)       │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  config.py  │    │ exceptions.py   │    │ FreeAgent API   │
│(Config Mgmt)│    │(Error Handling) │    │ (api.freeagent  │
└─────────────┘    └─────────────────┘    │     .com)       │
                                          └─────────────────┘
```

### Usage Patterns

#### Simple Usage (High Level)
```python
from freeagent_subagent import create_subagent
subagent = create_subagent()
result = subagent.process_command("show unpaid invoices")
```

#### Direct Component Usage (Mid Level)
```python
from freeagent_subagent import FreeAgentClient, InvoiceManager, FreeAgentConfig

config = FreeAgentConfig()
client = FreeAgentClient(config.get('client_id'), config.get('client_secret'))
manager = InvoiceManager(client)
invoices = manager.get_unpaid_invoices()
```

#### Low-Level API Usage
```python
from freeagent_subagent import FreeAgentClient

client = FreeAgentClient(client_id, client_secret, sandbox=False)
client.set_tokens(access_token, refresh_token)
response = client._make_request('GET', '/invoices')
```

## Security Notes

- Never commit API credentials to version control
- Use environment variables or secure config files
- Always test with sandbox environment first
- Tokens are automatically refreshed but store them securely

## License

This project is provided as-is for personal use. Please respect FreeAgent's API terms of service.

## Support

For FreeAgent API documentation: https://dev.freeagent.com/docs/

For issues with this sub-agent, check your configuration and API credentials first.