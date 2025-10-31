# Risk Agents App - Quick Start

**Status**: ✅ MVP Complete - Ready for Real-World Testing

---

## Start the Application

```bash
cd /Users/gavinslater/projects/life/risk-agents-app
docker-compose up
```

**Access**:
- 🌐 **Frontend**: http://localhost:3050
- 🔧 **Backend API**: http://localhost:8050
- 📚 **API Docs**: http://localhost:8050/docs

---

## Stop the Application

```bash
# Stop (Ctrl+C in terminal, then)
docker-compose down

# Or force stop
docker-compose down -v
```

---

## Quick Commands

### Restart Services
```bash
# Restart backend only
docker-compose restart backend

# Restart frontend only
docker-compose restart frontend

# Restart both
docker-compose restart
```

### View Logs
```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Last 50 lines
docker-compose logs backend | tail -50
```

### Health Checks
```bash
# Backend health
curl http://localhost:8050/health

# Frontend check
curl -I http://localhost:3050

# All API endpoints
open http://localhost:8050/docs
```

---

## Features Overview

### 1. Dashboard (http://localhost:3050/dashboard)
- Usage metrics (skills used, queries made)
- Recent activity
- Quick actions

### 2. Chat Interface (http://localhost:3050/chat)
- Natural language queries
- Real-time AI responses
- Message history

**Try**:
- "What skills are available?"
- "Generate a project charter for a risk reporting system"
- "Explain the VAR Policy"

### 3. Skills Browser (http://localhost:3050/skills)
- 15 Change Agent skills
- Domain filtering
- Direct execution

**Skill Categories**:
- Meeting Management (3 skills)
- Project Setup (3 skills)
- Requirements Gathering (3 skills)
- Project Artifacts (3 skills)
- Status Tracking (3 skills)

### 4. Knowledge Browser (http://localhost:3050/knowledge)
- 6 documents total
- 2 ICBC policies with YAML metadata
- 4 change-agent guides

**Featured**:
- VAR Policy (with governance metadata)
- Stress Testing Framework

---

## Real-World Usage

### Scenario 1: Start a New Project
1. Skills → "Project Charter Generator"
2. Skills → "Stakeholder Analysis"
3. Skills → "RACI Matrix Generator"

### Scenario 2: Meeting Management
1. Skills → "Meeting Minutes Capture"
2. Skills → "Action Item Tracking"
3. Skills → "Follow-up Generator"

### Scenario 3: Requirements Work
1. Skills → "Business Requirements Capture"
2. Skills → "Requirement Validation"
3. Skills → "Use Case Generator"

---

## Track Your Feedback

**Feedback Log**: `/docs/usage-feedback.md`

**Daily Notes**:
- What you tried
- What worked
- What didn't work
- Time saved
- Issues found

---

## Common Issues

### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose build backend
docker-compose up
```

### Frontend Won't Start
```bash
# Check logs
docker-compose logs frontend

# Rebuild
docker-compose build frontend
docker-compose up
```

### Port Already in Use
```bash
# Find process on port 8050 (backend)
lsof -i :8050
kill -9 <PID>

# Find process on port 3050 (frontend)
lsof -i :3050
kill -9 <PID>
```

### Clear Everything and Start Fresh
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

---

## Documentation

**Implementation Plan**: `/risk-agents-app-implementation-plan.md`
**Usage Guide**: `/docs/real-world-usage-guide.md`
**Feedback Log**: `/docs/usage-feedback.md`
**MVP Summary**: `/docs/mvp-completion-summary.md`
**Module Docs**: `/docs/module-*.md`

---

## Next Steps

1. ✅ Start the application
2. ✅ Try all 4 features (dashboard, chat, skills, knowledge)
3. ✅ Use for real tasks (1-2 weeks)
4. ✅ Track feedback daily
5. ✅ Decide: Deploy or improve?

---

## Support

**Issues**: Document in `/docs/usage-feedback.md`
**Questions**: Check `/docs/real-world-usage-guide.md`
**API Reference**: http://localhost:8050/docs

---

**Version**: MVP (Modules 1-7 Complete)
**Status**: Ready for Testing
**Last Updated**: October 27, 2025
