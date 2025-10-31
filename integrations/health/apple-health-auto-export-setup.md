# Apple Health Auto Export - Setup Guide

## Overview
This guide walks you through configuring the Health Auto Export iOS app to automatically sync your Apple Health data to the local health service every 30 minutes.

## Prerequisites
- ✅ Health service running on `localhost:3001`
- ✅ iPhone with Health app containing health data
- ⏸️ Health Auto Export app installed from App Store
- ⏸️ Health Auto Export Premium subscription (7-day free trial available)

## Step 1: Install Health Auto Export App

1. Open App Store on your iPhone
2. Search for "Health Auto Export - JSON+CSV"
3. Install the app by Lybron
4. Open the app and grant Health app permissions when prompted

## Step 2: Create REST API Automation

### 2.1 Create New Automation
1. Open Health Auto Export app
2. Tap **Automations** tab (bottom navigation)
3. Tap **"+"** button (top right) to create new automation
4. Select **"REST API"** as automation type
5. Give it a name: **"Health Service Sync"**

### 2.2 Configure REST API Endpoint
1. **Endpoint URL**: Enter your Mac's local IP address (not localhost!)
   - Find your Mac's IP: System Settings → Network → Your active connection
   - Format: `http://[YOUR_MAC_IP]:3001/api/apple-health/auto-export`
   - Example: `http://192.168.1.100:3001/api/apple-health/auto-export`

   **Note**: Use your Mac's IP address (not `localhost` or `127.0.0.1`) because the iPhone needs to reach your Mac over the local network.

2. **Request Method**: POST (should be default)
3. **Headers**: Leave blank (no authentication required)
4. **Content-Type**: application/json (automatically set)
5. **Timeout**: 30 seconds (default is fine)

### 2.3 Select Data Type - Health Metrics
1. Tap **"Data Type"**
2. Select **"Health Metrics"**
3. Tap **"Select Metrics"**
4. Enable these **Core Metrics**:
   - ✅ Step Count
   - ✅ Heart Rate
   - ✅ Active Energy Burned
   - ✅ Walking + Running Distance
   - ✅ Body Mass (Weight)

5. Enable these **Additional Metrics**:
   - ✅ Sleep Analysis
   - ✅ Resting Heart Rate
   - ✅ Apple Exercise Time
   - ✅ Flights Climbed
   - ✅ VO2 Max

6. Tap **"Done"** to save metric selection

### 2.4 Configure Export Settings
1. **Export Format**: JSON (required)
2. **Export Version**: Latest/Newest version available
3. **Time Period**: **"Since Last Sync"** (incremental updates - recommended)
4. **Aggregation**: None (or as preferred)
5. **Sync Cadence**: **30 minutes**
   - This means up to 48 syncs per day
   - Balances data freshness with battery usage

### 2.5 Optional: Create Second Automation for Workouts
If you want workout data:
1. Create another automation (repeat Step 2.1)
2. Name it: **"Workout Sync"**
3. Same endpoint URL
4. Select **"Workouts"** as data type
5. Enable all workout types or select specific ones:
   - ✅ Running
   - ✅ Walking
   - ✅ Cycling
   - ✅ Strength Training
   - (Select others as needed)
6. Same sync settings: JSON, Since Last Sync, 30 minutes

### 2.6 Enable Automations
1. Toggle the automation **ON** (green switch)
2. Enable **notifications** (optional but helpful for debugging)
3. Tap **"Save"** or **"Done"**

## Step 3: Verify Health Service is Running

### 3.1 Start the Health Service
```bash
cd /Users/gavinslater/projects/life/health-integration/health-service
npm start
```

Expected output:
```
Health Data Service running on port 3001
Connected to SQLite database: ./data/health.db
Created/verified table: apple_health_auto_export
```

### 3.2 Test the Endpoint
From your Mac terminal:
```bash
curl http://localhost:3001/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-05T...",
  "version": "1.0.0",
  "services": {
    "database": true,
    "parkrun": true
  }
}
```

## Step 4: Test Manual Sync

### 4.1 Manual Export Test
1. In Health Auto Export app, find your **"Health Service Sync"** automation
2. Tap the automation to open it
3. Tap **"Export Now"** or manual trigger button
4. Wait for completion (you should see a success notification)

### 4.2 Verify Data Reception
Check the health service logs for:
```
Received Apple Health Auto Export data
Stored Auto Export import with ID: 1, metrics: 5, workouts: 0
Processed Auto Export data: X metric data points, 0 workouts
```

Or query the stats endpoint:
```bash
curl http://localhost:3001/api/apple-health/auto-export/stats
```

Expected response:
```json
{
  "success": true,
  "data": {
    "total_imports": 1,
    "total_metrics": 5,
    "total_workouts": 0,
    "successful_imports": 1,
    "failed_imports": 0,
    "last_import": "2025-10-05T14:30:00.000Z",
    "first_import": "2025-10-05T14:30:00.000Z"
  }
}
```

## Step 5: Monitor Automated Syncing

### 5.1 Enable Background Sync
- Ensure **Background Sync** is enabled in automation settings
- Keep your iPhone unlocked periodically (background sync works when device is unlocked)
- The app will attempt to sync every 30 minutes automatically

### 5.2 Check Import History
```bash
# View recent imports (last 7 days)
curl http://localhost:3001/api/apple-health/auto-export/recent?days=7
```

### 5.3 Monitor Health Service Logs
The service will log each import:
```
Received Apple Health Auto Export data { metricsCount: 5, workoutsCount: 0, timestamp: ... }
Stored Auto Export import with ID: 2, metrics: 5, workouts: 0
Processed Auto Export data: 15 metric data points, 0 workouts
```

## Troubleshooting

### iPhone Can't Reach Endpoint
**Problem**: Automation fails with connection error

**Solutions**:
1. Verify both devices are on same WiFi network
2. Check Mac's firewall settings (allow port 3001)
3. Verify health service is running
4. Try Mac's IP address instead of `localhost`
5. Ping your Mac from iPhone (use Network Utility app)

### No Data in Sync
**Problem**: Sync succeeds but no metrics received

**Solutions**:
1. Check metric selection in automation settings
2. Verify "Since Last Sync" has new data since last export
3. Try "Today" or "Yesterday" time period to test
4. Check Health app permissions for Health Auto Export

### Sync Not Running Automatically
**Problem**: Manual sync works but automatic doesn't run

**Solutions**:
1. Verify Background Sync is enabled
2. Unlock iPhone periodically (background sync requires device unlocked)
3. Check iOS Low Power Mode is OFF
4. Verify automation is toggled ON (green)
5. Check app notifications for sync errors

### Database Errors
**Problem**: Health service logs database errors

**Solutions**:
1. Stop health service
2. Check database file exists: `./data/health.db`
3. Restart service to rebuild tables
4. Check disk space

## Monitoring & Maintenance

### Daily Checks
- Health service logs show regular imports
- Stats endpoint shows incrementing import counts
- No error notifications from Health Auto Export app

### Weekly Checks
- Verify metric counts are increasing
- Check failed_imports count (should be 0)
- Review sync frequency (should be ~48/day with 30-min cadence)

### Monthly Review
- Analyze health data trends
- Verify all desired metrics are being captured
- Adjust sync cadence if needed (battery vs. freshness)
- Check database size and cleanup old imports if necessary

## Premium Subscription

### Trial Period
- 7-day free trial available
- Test full functionality before purchasing
- Verify automated sync works reliably

### After Trial
- Purchase Premium if trial successful
- Cost: Check App Store for current pricing
- Benefits: Continued automated REST API sync, all export features

## Next Steps

Once automated sync is working:
1. ✅ Monitor for 24-48 hours to verify reliability
2. ✅ Validate battery impact is acceptable
3. ✅ Purchase Premium subscription if satisfied
4. ✅ Integrate health metrics with health-agent queries
5. ✅ Build health dashboards using fresh data
6. ✅ Set up alerts for goal tracking (weight, steps, etc.)

## Reference: Metric Names

Health Auto Export uses these metric names in JSON:
- `step_count` - Daily steps
- `heart_rate` - Heart rate measurements
- `active_energy_burned` - Active calories
- `walking_running_distance` - Distance walked/ran
- `body_mass` - Weight measurements
- `sleep_analysis` - Sleep sessions
- `resting_heart_rate` - Resting HR
- `apple_exercise_time` - Exercise minutes
- `flights_climbed` - Stairs climbed
- `vo2_max` - VO2 Max estimates

## Support Resources

- **Health Auto Export GitHub**: https://github.com/Lybron/health-auto-export
- **Documentation**: https://www.healthyapps.dev/blog/how-to-sync-apple-health-data-to-rest-api
- **Health Service Logs**: Check console output for error details
- **Database Inspection**: Use SQLite browser to inspect `./data/health.db`
