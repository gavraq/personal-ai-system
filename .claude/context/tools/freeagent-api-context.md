# FreeAgent API Integration Context

## Status: ✅ Enhanced OAuth with Auto-Refresh
- **API Access**: Production FreeAgent account (Bright Slate Limited)
- **Authentication**: OAuth 2.0 with automatic token refresh
- **Client App**: "FreeAgent AI Agent" (Client ID: 970GvhTqju_QFVpCf3vpLw)

## Core Operations
- **Invoice Management**: Create, list, track ICBC invoices
- **Payment Tracking**: Outstanding amounts, payment status
- **ICBC Automation**: PO detection, £1,700/day rate, 14-day terms
- **Financial Reporting**: Cash flow analysis, revenue tracking

## Business Context
- **Primary Client**: ICBC Standard Bank (monthly invoicing)
- **Invoice Sequence**: Currently 016-018 range
- **Outstanding**: ~£152K+ across multiple invoices
- **Rate Structure**: £1,700/day, 3.5 days/week average

## Integration Features
- **Natural Language**: "Create ICBC invoice for August 2025"
- **Smart Detection**: Automatic PO number and rate application
- **Error Recovery**: Graceful OAuth token refresh
- **Production Ready**: Handles real financial transactions

## Agent Integration
- **Primary**: FreeAgent Invoice Agent (`freeagent-invoice-agent`)
- **Commands**: Natural language invoice operations
- **Data Storage**: ~/.config/freeagent/config.json

---
*Full implementation details: `/Users/gavinslater/projects/life/freeagent_subagent/CLAUDE.md`*