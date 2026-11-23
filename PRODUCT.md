# Kubernetes Todo App - Product Context

## Product Summary
A modern, visually stunning Todo application running on Kubernetes that demonstrates:
- Full-stack integration (Frontend UI ↔ Nginx ↔ PostgreSQL)
- Kubernetes orchestration in action
- Production-grade architecture
- Database persistence and service discovery

## Target Users
- Portfolio reviewers
- Technical interviewers
- Systems engineer hiring managers
- Anyone evaluating Kubernetes skills

## Core Goals
1. **Demonstrate Kubernetes** - Show services working together seamlessly
2. **Beautiful UI** - Modern, polished, production-grade interface
3. **Full-stack integration** - Frontend talks to backend talks to database
4. **Show system architecture** - Display Kubernetes components visually

## Key Features
1. **Todo Management** - Add, complete, delete todos (CRUD operations)
2. **Database Persistence** - All data stored in PostgreSQL
3. **System Status Dashboard** - Shows:
   - Connected services (Nginx, PostgreSQL)
   - Database connection status
   - Response times
   - Running environment info
4. **Modern Design** - Minimal, clean, professional UI

## Technical Stack
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript (no frameworks - shows raw skills)
- **Backend**: Nginx (serves frontend + proxies API requests)
- **Database**: PostgreSQL (data persistence)
- **Orchestration**: Kubernetes (Docker Desktop)

## Success Metrics
- Todos persist in database across page reloads
- UI is fast, responsive, and beautiful
- System status shows real Kubernetes environment info
- Code is clean, well-commented, production-ready
- Portfolio-worthy in appearance and functionality

## Design Principles
- **Minimalist**: No clutter, every element has purpose
- **Modern**: Current design trends (clean typography, subtle shadows, smooth transitions)
- **Professional**: Looks like a real production application
- **Accessible**: Clear contrast, readable text, intuitive interactions
- **Fast**: Smooth animations, instant feedback

## Content Strategy
- Minimal copy, maximum clarity
- System status displayed clearly but not intrusively
- Empty state messaging (when no todos)
- Success/error feedback for user actions

## Deployment Context
- Running in Docker Desktop Kubernetes cluster
- Nginx handles both static assets and API requests
- PostgreSQL stores all data durably
- Designed to impress hiring managers and interviewers
