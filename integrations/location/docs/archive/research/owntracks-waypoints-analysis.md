# Owntracks Waypoints vs Custom JSON Locations - Analysis

**Date**: November 1, 2025
**Context**: Evaluating whether to use Owntracks built-in waypoints instead of custom JSON location database

---

## Overview

Owntracks has a built-in **waypoints** feature for defining known locations with geofencing and enter/exit event tracking. This analysis evaluates whether to leverage this vs. the proposed custom JSON location database approach.

---

## Owntracks Waypoints Features

### Data Format

**Waypoint Definition**:
```json
{
    "_type": "waypoint",
    "desc": "Pine Cliffs Resort",
    "lat": 37.094,
    "lon": -8.178,
    "rad": 500,
    "tst": 1609459200,
    "rid": "pinecliffs-resort"
}
```

**Transition Event** (published when entering/leaving):
```json
{
    "_type": "transition",
    "event": "enter",
    "desc": "Pine Cliffs Resort",
    "lat": 37.094,
    "lon": -8.178,
    "tst": 1729267200
}
```

### Key Features

1. **Geo-fencing**
   - Defined radius in meters
   - Automatic enter/exit detection
   - Real-time event publishing

2. **Publishing Mechanism**
   - Published to MQTT topic: `owntracks/<user>/<device>/waypoint`
   - Non-retained messages
   - Can be queried via `owntracks/+/+/waypoint` filter

3. **Identification**
   - `desc`: Human-readable name
   - `rid`: Region ID (auto-generated or custom)
   - `tst`: Timestamp as unique identifier

4. **Types of Waypoints**
   - **Geographical**: lat/lon with radius
   - **Beacon-based** (iOS): UUID, major, minor numbers

---

## Comparison: Owntracks Waypoints vs Custom JSON

### Owntracks Waypoints Approach

**Pros:**
✅ **Native integration** - Built into Owntracks ecosystem
✅ **Real-time events** - Automatic enter/exit detection
✅ **No custom code** - Uses existing Owntracks infrastructure
✅ **MQTT support** - Can subscribe to waypoint events
✅ **Mobile app integration** - Can create/edit waypoints in app
✅ **Geofencing** - Automatic radius-based detection

**Cons:**
❌ **Device-specific** - Waypoints defined per device
❌ **No retroactive analysis** - Only works for future location tracking
❌ **Limited metadata** - Only basic fields (desc, lat, lon, rad)
❌ **No trip context** - Can't easily define "Portugal Oct 2025" location set
❌ **Requires MQTT** - Need to set up waypoint publishing/subscription
❌ **No bulk import** - Would need to manually create ~50+ waypoints
❌ **Historical data limitation** - Past location records don't have waypoint associations

### Custom JSON Location Database

**Pros:**
✅ **Retroactive analysis** - Works with all historical data
✅ **Rich metadata** - Can include any fields (timezone, venue type, activities)
✅ **Trip grouping** - Separate JSON files per trip
✅ **Bulk management** - Easy to create/edit many locations at once
✅ **Flexible structure** - Can nest locations, add categories
✅ **Version control** - JSON files in git for tracking changes
✅ **No infrastructure changes** - Works with current Owntracks setup

**Cons:**
❌ **Custom code required** - Need to build location matching logic
❌ **No real-time events** - Only post-hoc analysis
❌ **Maintenance burden** - Need to keep location database updated
❌ **No mobile app integration** - Can't create locations on-the-go

---

## Proposed Custom JSON Format

### Base Locations (UK)
```json
{
  "locations": [
    {
      "id": "home-esher",
      "name": "Home (Esher)",
      "coordinates": {
        "lat": 51.3712,
        "lon": -0.3648
      },
      "radius": 100,
      "timezone": "Europe/London",
      "type": "residence",
      "tags": ["home", "esher"]
    },
    {
      "id": "bushy-parkrun",
      "name": "Bushy parkrun",
      "coordinates": {
        "lat": 51.4108,
        "lon": -0.3355
      },
      "radius": 200,
      "timezone": "Europe/London",
      "type": "parkrun",
      "activities": ["parkrun", "running"],
      "tags": ["parkrun", "bushy-park", "saturday-morning"]
    }
  ]
}
```

### Trip-Specific Locations
```json
{
  "trip_name": "Portugal October 2025",
  "trip_dates": {
    "start": "2025-10-18",
    "end": "2025-10-24"
  },
  "locations": [
    {
      "id": "pinecliffs-resort",
      "name": "Pine Cliffs Resort",
      "coordinates": {
        "lat": 37.094,
        "lon": -8.178
      },
      "radius": 300,
      "timezone": "Europe/Lisbon",
      "type": "accommodation",
      "venue_type": "timeshare_resort",
      "activities": ["golf", "beach", "pool"],
      "tags": ["algarve", "annual-trip", "timeshare"]
    },
    {
      "id": "pinecliffs-golf",
      "name": "Pine Cliffs Golf Course",
      "coordinates": {
        "lat": 37.093,
        "lon": -8.175
      },
      "radius": 500,
      "timezone": "Europe/Lisbon",
      "type": "golf_course",
      "venue_details": {
        "holes": 9,
        "course_type": "clifftop",
        "par": 33
      },
      "activities": ["golf"],
      "tags": ["golf", "clifftop", "algarve"]
    },
    {
      "id": "pingo-doce-vilamoura",
      "name": "Pingo Doce Vilamoura",
      "coordinates": {
        "lat": 37.1040,
        "lon": -8.1266
      },
      "radius": 100,
      "timezone": "Europe/Lisbon",
      "type": "supermarket",
      "tags": ["shopping", "vilamoura"]
    },
    {
      "id": "armacao-pera-beach",
      "name": "Praia de Armação de Pêra",
      "coordinates": {
        "lat": 37.0999,
        "lon": -8.3551
      },
      "radius": 200,
      "timezone": "Europe/Lisbon",
      "type": "beach",
      "tags": ["beach", "excursion", "algarve"]
    },
    {
      "id": "faro-airport",
      "name": "Faro Airport",
      "coordinates": {
        "lat": 37.014,
        "lon": -7.966
      },
      "radius": 500,
      "timezone": "Europe/Lisbon",
      "type": "airport",
      "iata_code": "FAO",
      "tags": ["airport", "faro"]
    }
  ]
}
```

---

## Recommendation: **Hybrid Approach**

### Use Custom JSON for Analysis (Primary)

**Why:**
1. **Historical data compatibility** - Works with all past location data (2010-2025)
2. **Trip-specific contexts** - Easy to define Portugal, Minnesota, Scotland trips
3. **Rich metadata** - Can include venue types, activities, timezones
4. **Bulk management** - Create 50+ locations easily in JSON
5. **Version control** - Track changes to location definitions

**Implementation:**
```
locations/
├── base_locations.json          # Permanent UK locations (15+)
└── trips/
    ├── portugal_2025-10.json    # Pine Cliffs trip
    ├── usa_2025-12.json         # Minnesota Christmas
    └── scotland_2026-03.json    # Future trips
```

### Use Owntracks Waypoints for Real-Time (Optional Enhancement)

**Why:**
1. **Future enhancement** - Can add later for real-time notifications
2. **Mobile convenience** - Create waypoints on-the-go in app
3. **Enter/exit alerts** - Real-time notifications when arriving/leaving

**Use cases:**
- Alert when arriving home after long commute
- Notify when leaving office to catch train
- Track parkrun venue visits automatically

**Implementation approach:**
1. Start with custom JSON (Phase 1-3 of improvement plan)
2. Add Owntracks waypoint support as Phase 6 (future enhancement)
3. Sync custom JSON locations → Owntracks waypoints for future tracking

---

## Decision Matrix

| Feature | Owntracks Waypoints | Custom JSON | Winner |
|---------|-------------------|-------------|--------|
| Historical data analysis | ❌ No | ✅ Yes | **Custom JSON** |
| Trip-specific location sets | ❌ Limited | ✅ Easy | **Custom JSON** |
| Rich metadata | ❌ Basic | ✅ Flexible | **Custom JSON** |
| Bulk management | ❌ Manual | ✅ Easy | **Custom JSON** |
| Version control | ❌ No | ✅ Yes | **Custom JSON** |
| Real-time events | ✅ Yes | ❌ No | **Owntracks** |
| Mobile app integration | ✅ Yes | ❌ No | **Owntracks** |
| Infrastructure required | ✅ Built-in | ❌ Custom | **Owntracks** |
| Portugal trip analysis | ❌ Can't retroactively | ✅ Works perfectly | **Custom JSON** |
| Future trip planning | ⚠️ Manual setup | ✅ Pre-define | **Custom JSON** |

**Score**: Custom JSON wins 7-3 for primary use case (analysis)

---

## Implementation Recommendation

### Phase 1-3: Custom JSON (Weeks 1-4)
Focus on custom JSON location database as documented in ANALYSIS-IMPROVEMENTS.md:
- Foundation work (directory structure, JSON loading)
- Golf analyzer
- Trip analyzer
- Test with Portugal trip historical data

### Phase 6: Owntracks Waypoints Integration (Future, Optional)
Add as enhancement for real-time features:
- Export custom JSON locations → Owntracks waypoints
- Subscribe to waypoint transition events
- Real-time notifications via MQTT

---

## Conclusion

**Use custom JSON location database as the primary approach** because:

1. ✅ **Works retroactively** - Can analyze all historical data including Portugal trip
2. ✅ **Trip-focused** - Easy to define location sets per trip
3. ✅ **Flexible** - Rich metadata, version control, bulk management
4. ✅ **Implementation ready** - Detailed plan already documented

**Consider Owntracks waypoints as future enhancement** for:
- Real-time enter/exit notifications
- Mobile app convenience
- Future trips (after building custom JSON foundation)

---

## Files Updated

- **This analysis**: `/integrations/location/OWNTRACKS-WAYPOINTS-ANALYSIS.md`
- **Main improvement plan**: `/integrations/location/ANALYSIS-IMPROVEMENTS.md` (no changes needed)
- **Status**: Custom JSON approach validated, proceed with implementation plan

**Next Action**: Proceed with Phase 1 of ANALYSIS-IMPROVEMENTS.md using custom JSON location database
