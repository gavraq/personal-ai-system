# Agent Server Integration Guide

Complete guide for deploying and integrating the Claude Agent Server with the Interactive CV website.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Browser                             │
│                  https://www.gavinslater.com                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ├─── API Mode ────────┐
                           │                     │
                           │              ┌──────▼──────┐
                           │              │   Vercel    │
                           │              │ Anthropic   │
                           │              │   API       │
                           │              └─────────────┘
                           │
                           └─── Agent Mode ──────┐
                                                  │
                                           ┌──────▼──────┐
                                           │   Vercel    │
                                           │  WebSocket  │
                                           │   Client    │
                                           └──────┬──────┘
                                                  │ wss://
                                                  │
                                           ┌──────▼──────────────────┐
                                           │  NGINX Proxy Manager    │
                                           │  agent.gavinslater.com  │
                                           │   (Port 443 → 8090)     │
                                           └──────┬──────────────────┘
                                                  │
                                           ┌──────▼──────────────────┐
                                           │  Docker Container       │
                                           │ claude-agent-server     │
                                           │   (Port 8090)           │
                                           │                         │
                                           │  ┌────────────────────┐ │
                                           │  │ Claude Agent SDK   │ │
                                           │  │ (claude CLI)       │ │
                                           │  └────────────────────┘ │
                                           │                         │
                                           │  Volumes Mounted:       │
                                           │  • UFC Context          │
                                           │  • Agent Definitions    │
                                           │  • Obsidian Vault       │
                                           │  • Documents            │
                                           │  • MCP Servers          │
                                           └─────────────────────────┘
```

## Phase 1: Home Server Setup

### 1.1 Copy Files to Home Server

From your local machine:

```bash
# Copy the claude-agent-server directory to home server
scp -r /Users/gavinslater/projects/life/claude-agent-server gavin@home-server:/home/gavin/

# Or use git if already committed
cd /home/gavin/projects/life
git pull
```

### 1.2 Install Dependencies

On home server:

```bash
cd /home/gavin/claude-agent-server
npm install
```

### 1.3 Configure Environment

```bash
cp .env.example .env
nano .env
```

Set the following:

```bash
JWT_SECRET=<generate-strong-secret>
PORT=8090
NODE_ENV=production
LOG_LEVEL=info
```

**Important**: The `JWT_SECRET` must be the same on both Vercel and home server!

Generate a strong secret:

```bash
openssl rand -base64 32
```

### 1.4 Create Required Directories

```bash
# Create documents storage directory
mkdir -p /home/gavin/claude-documents

# Verify other paths exist
ls -la /home/gavin/projects/life/.claude/context
ls -la "/home/gavin/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault"
```

### 1.5 Build and Run Docker Container

```bash
cd /home/gavin/claude-agent-server

# Build the container
docker-compose build

# Start the container
docker-compose up -d

# Check logs
docker logs -f claude-agent-server
```

### 1.6 Authenticate Claude CLI

**Critical Step**: You must authenticate Claude CLI inside the container:

```bash
docker exec -it claude-agent-server claude auth login
```

Follow the prompts to authenticate. Credentials will be stored in the `claude-auth` volume.

### 1.7 Verify Container Health

```bash
# Check container status
docker ps

# Check health endpoint
curl http://localhost:8090/health

# Should return:
# {"status":"healthy","timestamp":"...","uptime":123.45}
```

## Phase 2: NGINX Proxy Manager Configuration

### 2.1 Create Proxy Host

Log into NGINX Proxy Manager (typically http://home-server:81)

**Proxy Host Settings:**

| Field | Value |
|-------|-------|
| Domain Names | `agent.gavinslater.com` |
| Scheme | `http` |
| Forward Hostname / IP | `localhost` (or Docker container IP) |
| Forward Port | `8090` |
| Cache Assets | ❌ Disabled |
| Block Common Exploits | ✅ Enabled |
| **Websockets Support** | **✅ ENABLED (Critical!)** |
| Access List | None (auth handled by JWT) |

**SSL Settings:**

| Field | Value |
|-------|-------|
| SSL Certificate | Request a new SSL Certificate (Let's Encrypt) |
| Force SSL | ✅ Enabled |
| HTTP/2 Support | ✅ Enabled |
| HSTS Enabled | ✅ Enabled |
| Email Address for Let's Encrypt | your-email@example.com |

### 2.2 DNS Configuration

Add an A record in your DNS provider:

```
Type: A
Name: agent
Value: <your-home-server-public-ip>
TTL: 3600
```

Or if using dynamic DNS:

```
Type: CNAME
Name: agent
Value: your-dynamic-dns-hostname
TTL: 3600
```

### 2.3 Test NGINX Configuration

```bash
# From home server
curl -k https://agent.gavinslater.com/health

# Should return the health check JSON
```

## Phase 3: Vercel Configuration

### 3.1 Add Environment Variables

In Vercel dashboard (https://vercel.com/your-username/interactive-cv-website):

Go to: **Settings → Environment Variables**

Add the following:

| Name | Value | Environment |
|------|-------|-------------|
| `NEXT_PUBLIC_AGENT_WS_URL` | `wss://agent.gavinslater.com/ws` | All |
| `JWT_SECRET` | `<same-secret-as-home-server>` | All |

**Important**: The `JWT_SECRET` must match exactly!

### 3.2 Deploy Updated Code

```bash
cd /Users/gavinslater/projects/life/interactive-cv-website

# Commit the changes
git add .
git commit -m "Add agent server integration with WebSocket support

- Implement AgentClient for WebSocket communication
- Add agent mode toggle in ChatInterface
- Create JWT token generation endpoint
- Support routing between Anthropic API and Agent Server
- Full UFC context loading when using agent mode

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

Vercel will automatically deploy the changes.

### 3.3 Pull Environment Variables Locally

```bash
vercel env pull
```

## Phase 4: Testing

### 4.1 Test Home Server Connection

From your local machine:

```bash
# Install websocat for WebSocket testing
brew install websocat

# Test WebSocket connection (you'll need a valid JWT token)
websocat wss://agent.gavinslater.com/ws?token=<jwt-token>

# Should connect and receive:
# {"type":"connected","connectionId":"conn_xxx",...}
```

### 4.2 Test Web Interface

1. Open https://www.gavinslater.com
2. Log in with admin credentials
3. Navigate to Personal Space
4. Click the **"API Mode"** button in the chat header
5. It should change to **"Agent Mode"** with a purple background
6. Status should show **"Agent Mode ● Connected"** (green dot)
7. Send a test message
8. Response should stream from the agent server

### 4.3 Test UFC Context

Send a message that requires UFC context:

```
"What are my current goals and active projects?"
```

The agent should respond with information from your UFC context files.

### 4.4 Test Document Awareness

1. Upload a document in the Documents tab
2. Switch to Agent Mode
3. Ask: "What documents do I have uploaded?"
4. The agent should list your documents

## Phase 5: Monitoring and Maintenance

### 5.1 Monitor Logs

**Home Server:**

```bash
# Container logs
docker logs -f claude-agent-server

# Follow specific log types
docker logs claude-agent-server 2>&1 | grep ERROR
docker logs claude-agent-server 2>&1 | grep WebSocket
```

**Vercel:**

View logs in Vercel dashboard: **Deployments → Latest → Logs**

### 5.2 Check Health Status

```bash
# Home server health
curl https://agent.gavinslater.com/health

# Vercel health (check deployment logs)
```

### 5.3 Restart Container

If needed:

```bash
docker-compose restart

# Or full rebuild
docker-compose down
docker-compose up -d --build
```

### 5.4 Update Container

```bash
cd /home/gavin/claude-agent-server
git pull
docker-compose down
docker-compose up -d --build
```

### 5.5 Re-authenticate Claude CLI

If authentication expires:

```bash
docker exec -it claude-agent-server claude auth login
```

## Troubleshooting

### Issue: WebSocket Connection Fails

**Symptoms:** "Agent Mode ● Connecting..." never turns green

**Solutions:**

1. Check NGINX WebSocket setting is enabled
2. Verify firewall allows port 443
3. Check container logs: `docker logs claude-agent-server`
4. Test direct connection: `curl http://localhost:8090/health`
5. Verify DNS resolves: `nslookup agent.gavinslater.com`

### Issue: Authentication Failed

**Symptoms:** "Authentication failed" error in logs

**Solutions:**

1. Verify `JWT_SECRET` matches on Vercel and home server
2. Generate new token: Visit `/api/agent/token` while logged in
3. Check token expiry (24 hours by default)

### Issue: UFC Context Not Loading

**Symptoms:** Agent doesn't know about goals/projects

**Solutions:**

1. Check volume mounts in `docker-compose.yml`
2. Verify files exist: `docker exec claude-agent-server ls -la /ufc`
3. Check file permissions on host
4. Review container logs for file access errors

### Issue: Claude CLI Not Authenticated

**Symptoms:** "Not authenticated" errors in container logs

**Solution:**

```bash
docker exec -it claude-agent-server claude auth login
```

### Issue: Container Won't Start

**Symptoms:** Container exits immediately

**Solutions:**

1. Check logs: `docker logs claude-agent-server`
2. Verify `JWT_SECRET` is set in `.env`
3. Check volume paths exist on host
4. Verify port 8090 is not in use: `lsof -i :8090`

## Security Considerations

### JWT Token Security

- Tokens expire after 24 hours
- Generated server-side only
- Requires valid NextAuth session
- Transmitted via secure WebSocket (wss://)

### Network Security

- All external access via HTTPS (port 443)
- WebSocket upgrades use TLS
- Only port 8090 exposed to localhost/NGINX
- Firewall rules recommended

### Volume Security

- UFC context mounted read-only
- Obsidian vault read-write (required for knowledge management)
- Documents storage isolated per user

### Best Practices

1. Keep `JWT_SECRET` secure and unique
2. Regularly update Docker image and dependencies
3. Monitor logs for suspicious activity
4. Use strong passwords for NGINX Proxy Manager
5. Keep Let's Encrypt certificates renewed (automatic)

## Backup and Recovery

### Backup Critical Data

```bash
# Backup Claude CLI credentials
docker run --rm -v claude-auth:/data -v $(pwd):/backup alpine tar czf /backup/claude-auth-backup.tar.gz /data

# Backup documents
tar czf claude-documents-backup.tar.gz /home/gavin/claude-documents

# Backup environment
cp /home/gavin/claude-agent-server/.env /home/gavin/claude-agent-server/.env.backup
```

### Restore from Backup

```bash
# Restore Claude CLI credentials
docker run --rm -v claude-auth:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/claude-auth-backup.tar.gz --strip 1"

# Restore documents
tar xzf claude-documents-backup.tar.gz -C /home/gavin/

# Restart container
docker-compose restart
```

## Performance Optimization

### Container Resources

In `docker-compose.yml`, you can add resource limits:

```yaml
services:
  claude-agent:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Connection Pooling

The WebSocket client automatically handles reconnection with exponential backoff.

Max reconnect attempts: 5
Initial delay: 1 second
Backoff multiplier: 2x

### Log Rotation

Configure in `docker-compose.yml`:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Advanced Configuration

### Custom System Prompt

To customize the system prompt built from UFC context, edit:

`/home/gavin/claude-agent-server/src/ufc-loader.ts`

Function: `buildSystemPrompt()`

### Add New MCP Servers

Configure in home server's Claude config:

`/home/gavin/projects/life/.claude/config.json`

The container will have access to all configured MCP servers.

### Enable Debug Logging

In `.env`:

```bash
LOG_LEVEL=debug
NODE_ENV=development
```

Restart container:

```bash
docker-compose restart
```

## Support

For issues or questions:

1. Check container logs: `docker logs claude-agent-server`
2. Check Vercel deployment logs
3. Review NGINX Proxy Manager logs
4. Test components individually (container → NGINX → Vercel)

## Summary

You now have a fully integrated system:

✅ Home server running Claude Agent SDK in Docker
✅ WebSocket server with UFC context loading
✅ NGINX Proxy Manager with SSL/TLS
✅ Vercel web interface with mode toggle
✅ JWT authentication
✅ Full access to MCP servers and specialized agents
✅ Cross-device persistence via Vercel Postgres
✅ Document awareness from Vercel Blob

**To use the system:**

1. Visit https://www.gavinslater.com
2. Log in
3. Go to Personal Space
4. Toggle **Agent Mode** in the chat header
5. Enjoy full UFC context and specialized agent capabilities!
