# 🏗️ BankSec Enterprise - Clean Architecture Refactoring

## Overview

This is the **enterprise-grade refactoring** of the BankSec cybersecurity training platform. The architecture has been completely redesigned using **Clean Architecture principles** to support 100,000+ concurrent users, banking-grade security standards, and high-velocity feature deployment.

## 🎯 Architecture Goals Achieved

### 1. **Strangler Fig Pattern Implementation**
- ✅ Decoupled frontend from backend templates
- ✅ Headless RESTful API architecture
- ✅ Prepared for React/Next.js migration
- ✅ Asynchronous processing with Celery workers

### 2. **Clean Architecture**
- ✅ **Domain Layer**: Pure business logic and entities
- ✅ **Service Layer**: Application use cases and business rules
- ✅ **Adapters Layer**: Database repositories and external APIs
- ✅ **Entrypoints Layer**: Flask REST API endpoints

### 3. **Database & Data Integrity**
- ✅ PostgreSQL with SQLAlchemy ORM
- ✅ Alembic migration system
- ✅ Redis for caching and sessions
- ✅ Connection pooling configuration

### 4. **Security Hardening**
- ✅ JWT authentication with refresh tokens
- ✅ Proper secrets management
- ✅ Redis-backed rate limiting
- ✅ Structured JSON logging

### 5. **DevOps & Infrastructure**
- ✅ Multi-stage Docker builds
- ✅ Docker Compose orchestration
- ✅ GitHub Actions CI/CD pipeline
- ✅ Monitoring and observability

## 📁 Project Structure

```
banksec_enterprise/
├── src/                          # Source code
│   ├── domain/                   # Core business logic
│   │   ├── models/              # Entities and value objects
│   │   └── repositories/        # Repository interfaces
│   ├── service/                 # Application logic
│   │   ├── use_cases/          # Business use cases
│   │   └── validators/         # Input validation
│   ├── adapters/               # External interfaces
│   │   ├── database/           # Database repositories
│   │   ├── external/          # External API adapters
│   │   └── security/          # Security implementations
│   ├── entrypoints/           # API and web interfaces
│   │   ├── api/              # REST API endpoints
│   │   └── web/              # Web interface (future)
│   └── shared/               # Common utilities
│       ├── utils/            # Helper functions
│       ├── constants/        # Application constants
│       └── exceptions/       # Custom exceptions
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── scripts/                 # Utility scripts
├── config/                  # Configuration files
├── docs/                    # Documentation
├── docker/                  # Docker configurations
└── .github/                # CI/CD workflows
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose (optional)

### Installation

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd banksec_enterprise
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Database Setup:**
```bash
export DATABASE_URL=postgresql://user:password@localhost/banksec_enterprise
export REDIS_URL=redis://localhost:6379/0
flask db upgrade
```

4. **Run Application:**
```bash
export FLASK_APP=src.entrypoints.api.app
export FLASK_ENV=development
flask run
```

### Docker Deployment

```bash
docker-compose up -d
```

## 🔧 Configuration

### Environment Variables

```bash
# Security
SECRET_KEY=your-secure-random-key
JWT_SECRET_KEY=your-jwt-secret-key

# Database
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://localhost:6379/0

# Application
FLASK_ENV=development|production|testing
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR

# External Services
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Configuration Files

- `config.py` - Main configuration class
- `.env` - Environment variables
- `docker-compose.yml` - Docker orchestration

## 📊 Architecture Components

### Domain Layer (`src/domain/`)
- **Entities**: User, Scenario, Transaction, Attempt
- **Value Objects**: UserProfile, TrainingProgress
- **Domain Events**: Business events (future)
- **Repository Interfaces**: Abstract repository definitions

### Service Layer (`src/service/`)
- **Use Cases**: UserUseCases, ScenarioUseCases
- **Business Logic**: Application-specific logic
- **Validation**: Input validation and business rules
- **Orchestration**: Complex business workflows

### Adapters Layer (`src/adapters/`)
- **Database**: SQLAlchemy repositories, models
- **External**: External API integrations
- **Security**: Authentication, authorization implementations

### Entrypoints Layer (`src/entrypoints/`)
- **API**: RESTful endpoints, request/response handling
- **Web**: Future web interface
- **CLI**: Command-line interfaces

## 🔒 Security Features

### Authentication & Authorization
- JWT tokens with refresh rotation
- Role-based access control (RBAC)
- Password strength validation
- Session management with Redis

### Data Protection
- Password hashing with bcrypt
- Input sanitization and validation
- SQL injection prevention
- XSS protection

### Monitoring & Logging
- Structured JSON logging
- Security event tracking
- Audit trail for all actions
- Performance metrics

## 📈 Performance Optimizations

### Database
- Connection pooling (PgBouncer compatible)
- Query optimization with indexes
- Database-level caching
- Read replicas support

### Application
- Redis caching layer
- Background task processing (Celery)
- API response compression
- Static asset optimization

### Infrastructure
- Load balancing ready
- Horizontal scaling support
- CDN integration
- Container orchestration

## 🧪 Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Coverage
```bash
pytest --cov=src tests/
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout

### Scenario Endpoints
- `GET /api/scenarios` - List scenarios
- `GET /api/scenarios/{id}` - Get scenario details
- `POST /api/scenarios/{id}/start` - Start scenario
- `POST /api/scenarios/{id}/action` - Process action

### User Endpoints
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/progress` - Get training progress

## 🚀 Deployment

### Production Checklist
- [ ] Set strong SECRET_KEY
- [ ] Configure PostgreSQL connection
- [ ] Set up Redis cluster
- [ ] Enable HTTPS
- [ ] Configure monitoring
- [ ] Set up log aggregation
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

### Scaling Considerations
- Use PostgreSQL with read replicas
- Implement Redis cluster for caching
- Use CDN for static assets
- Configure load balancers
- Set up monitoring alerts

## 📊 Monitoring & Observability

### Metrics
- Application performance metrics
- Database query performance
- Cache hit rates
- User activity metrics
- Security event tracking

### Logging
- Structured JSON logs
- Centralized log aggregation
- Security audit logs
- Application error tracking

### Alerting
- Performance degradation alerts
- Security incident alerts
- Database connection alerts
- Application error alerts

## 🔧 Development

### Code Style
- Black for formatting
- Flake8 for linting
- MyPy for type checking
- Pre-commit hooks

### Git Workflow
- Feature branches
- Pull request reviews
- Automated testing
- Semantic versioning

### Local Development
```bash
# Setup pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
flake8 src/
black src/

# Type checking
mypy src/
```

## 📋 Migration from MVP

If you're migrating from the BankSec MVP, please refer to:
- `scripts/migrate_mvp.py` - Migration script
- `MIGRATION_REPORT.md` - Detailed migration guide
- `docs/migration/` - Migration documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

- 📧 Email: support@banksec-enterprise.com
- 💬 Slack: #banksec-dev
- 📖 Documentation: docs/
- 🐛 Issues: GitHub Issues

## 🔄 Changelog

### Version 2.0.0 (Enterprise Release)
- ✅ Complete architecture refactoring
- ✅ Clean Architecture implementation
- ✅ PostgreSQL + Redis integration
- ✅ JWT authentication
- ✅ Docker containerization
- ✅ CI/CD pipeline
- ✅ Comprehensive testing
- ✅ Production-ready deployment

---

**BankSec Enterprise** - Training the next generation of cybersecurity professionals with enterprise-grade architecture and banking-level security standards.# banks-enterprise
# banks-enterprise
