# Network Configuration Reference

## Fixed IP Addresses

| Device | IP Address | Hostname | Purpose |
|--------|-----------|----------|---------|
| **Raspberry Pi** | `192.168.5.190` | pisatellite | Home server (Docker services) |
| **Mac Mini** | `192.168.5.235` | Gavins-Mac-mini | Development machine + Obsidian vault host |

## DNS Configuration

| Domain | Type | Target | Purpose |
|--------|------|--------|---------|
| `www.gavinslater.com` | CNAME | Vercel | Web UI |
| `agent.gavinslater.com` | A | `192.168.5.190` | Agent WebSocket |
| `health.gavinslater.com` | A | `192.168.5.190` | Health API |
| `owntracks.gavinslater.co.uk` | A | `192.168.5.190` | Location tracking (existing) |

## Service Endpoints

### External (Public)
- **Website**: `https://www.gavinslater.com` → Vercel
- **Agent WebSocket**: `wss://agent.gavinslater.com/ws` → Pi:8090
- **Health API**: `https://health.gavinslater.com/api/*` → Pi:3001
- **Location API**: `https://owntracks.gavinslater.co.uk/api/*` → Pi (existing)

### Internal (Docker Network)
- **Health Service**: `http://health-service:3001` or `http://172.20.0.10:3001`
- **Agent Server**: `http://claude-agent:8090` or `http://172.20.0.11:8090`

### Local (Pi)
- **Health Service**: `http://localhost:3001`
- **Agent Server**: `http://localhost:8090`
- **NGINX Proxy Manager**: `http://192.168.5.190:81`

## Network Mount (Obsidian Vault)

### Mac (SMB Server)
**Share Path**: `/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault`
**Share Name**: `obsidian-vault`
**Protocol**: SMB (CIFS)

### Pi (SMB Client)
**Mount Point**: `/mnt/obsidian-vault`
**Mount Command**:
```bash
sudo mount -t cifs //192.168.5.235/obsidian-vault /mnt/obsidian-vault -o credentials=/etc/smb-credentials,uid=1000,gid=1000
```

**fstab Entry**:
```
//192.168.5.235/obsidian-vault /mnt/obsidian-vault cifs credentials=/etc/smb-credentials,uid=1000,gid=1000,_netdev 0 0
```

## Quick Commands Reference

### SSH to Pi
```bash
ssh pi@192.168.5.190
```

### Copy Files to Pi
```bash
# Copy health.db
scp /Users/gavinslater/projects/life/health-integration/health-service/data/health.db \
    pi@192.168.5.190:/home/pi/docker/health-service/data/

# Copy .claude directory
scp -r /Users/gavinslater/projects/life/.claude pi@192.168.5.190:/home/pi/
```

### Test Network Mount
```bash
# From Pi - test SMB connection to Mac
smbclient //192.168.5.235/obsidian-vault -U username

# Mount test
sudo mount -t cifs //192.168.5.235/obsidian-vault /mnt/test-mount -o username=xxx,password=xxx
```

### Test Services
```bash
# Health service
curl http://192.168.5.190:3001/health
curl https://health.gavinslater.com/health

# Agent server
curl http://192.168.5.190:8090/health
wscat -c ws://192.168.5.190:8090/health

# Owntracks (existing)
curl https://owntracks.gavinslater.co.uk/api/0/locations
```

## Firewall Configuration (Pi)

### Ports to Open
- `80` - HTTP (NGINX Proxy Manager)
- `443` - HTTPS (NGINX Proxy Manager)
- `81` - NGINX Proxy Manager Admin
- `3001` - Health Service (internal only, via NGINX)
- `8090` - Agent Server (internal only, via NGINX)

### UFW Configuration (if using)
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 81/tcp
sudo ufw enable
```

## MAC Address (for DHCP Reservation)

**Pi MAC Address**: TBD (run `ip addr show` on Pi)

To reserve IP in router:
1. Access router admin (usually 192.168.5.1)
2. DHCP settings
3. Reserve IP: 192.168.5.190 for Pi's MAC address

---

**Last Updated**: 2025-10-30
**Pi IP**: 192.168.5.190
**Status**: Ready for deployment
