# Parkrun API Integration Context

## Status: ✅ Active with Node.js Microservice
- **Service**: Node.js health microservice with parkrun.js v1.3.1
- **Data**: 273+ total parkrun results, 31 runs confirmed in 2025
- **Storage**: SQLite database with API caching

## Data Sources
- **Official Parkrun**: Results via parkrun.js library
- **Local Cache**: SQLite database for performance
- **Real-time API**: Health service REST endpoints

## Key Metrics Available
- **Performance**: Times, positions, age grades, personal bests
- **Consistency**: Weekly participation tracking, venue analysis
- **Trends**: Performance progression, seasonal patterns
- **Venues**: Multi-location performance comparison

## Health Service Architecture
- **Location**: `/Users/gavinslater/projects/life/health-integration/health-service/`
- **Technology**: Express.js server, parkrun.js client, SQLite storage
- **Endpoints**: `/parkrun/*` for various data queries
- **Python Client**: Wrapper for agent integration

## Integration Patterns
- **Weekly Updates**: Automatic Saturday result ingestion
- **Performance Analysis**: Trend identification, goal tracking
- **Venue Insights**: Best performance locations, travel analysis
- **Consistency Monitoring**: Participation pattern tracking

## Agent Integration
- **Primary**: Health Agent (`health-agent`)
- **Queries**: "Show my 2025 parkrun stats", "What's my PB progression?"
- **Analytics**: Performance trends, venue optimization, goal tracking

---
*Full implementation details: `/Users/gavinslater/projects/life/health-integration/CLAUDE.md`*