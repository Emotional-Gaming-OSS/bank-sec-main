#!/usr/bin/env python3
"""
Migration script from BankSec MVP to Enterprise Architecture
This script helps migrate the existing MVP code to the new Clean Architecture structure
"""

import os
import shutil
import sys
from pathlib import Path

def migrate_backend_structure(source_dir: str, target_dir: str) -> None:
    """
    Migrate backend structure from MVP to Enterprise
    
    Args:
        source_dir: Source directory of MVP backend
        target_dir: Target directory for Enterprise structure
    """
    print(f"🔄 Migrating backend from {source_dir} to {target_dir}")
    
    # Create target directories if they don't exist
    target_path = Path(target_dir)
    backend_path = target_path / "src"
    
    # Copy core files to appropriate locations
    migrations = [
        # Database models -> Domain models
        ("database.py", backend_path / "adapters" / "database" / "models.py"),
        
        # Auth module -> Service layer
        ("auth.py", backend_path / "service" / "use_cases" / "auth_use_cases.py"),
        
        # Simulation engine -> Service layer
        ("simulation_engine.py", backend_path / "service" / "simulation" / "simulation_service.py"),
        
        # Attack scenarios -> Domain/Service
        ("attack_scenarios.py", backend_path / "domain" / "models" / "scenario_templates.py"),
        
        # App.py -> Entrypoints
        ("app.py", backend_path / "entrypoints" / "api" / "legacy_app.py"),
    ]
    
    for source_file, target_file in migrations:
        source_path = Path(source_dir) / source_file
        if source_path.exists():
            print(f"📄 Copying {source_file} -> {target_file}")
            
            # Create parent directory
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, target_file)
            
            # Add migration header
            with open(target_file, 'r+') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(f'"""\nMIGRATED FROM MVP - {source_file}\nThis file has been migrated from the original MVP structure\nand needs to be refactored to follow Clean Architecture principles.\n"""\n\n' + content)
    
    print("✅ Backend structure migration completed")

def migrate_frontend_structure(source_dir: str, target_dir: str) -> None:
    """
    Migrate frontend structure
    
    Args:
        source_dir: Source directory of MVP frontend
        target_dir: Target directory for Enterprise structure
    """
    print(f"🔄 Migrating frontend from {source_dir} to {target_dir}")
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Copy frontend files
    if source_path.exists():
        frontend_target = target_path / "frontend"
        frontend_target.mkdir(parents=True, exist_ok=True)
        
        # Copy all frontend files
        for item in source_path.iterdir():
            if item.is_file():
                shutil.copy2(item, frontend_target / item.name)
            elif item.is_dir():
                shutil.copytree(item, frontend_target / item.name, dirs_exist_ok=True)
        
        print("✅ Frontend structure migration completed")
    else:
        print("⚠️  No frontend directory found")

def create_migration_report(source_dir: str, target_dir: str) -> None:
    """
    Create a migration report with next steps
    
    Args:
        source_dir: Source directory
        target_dir: Target directory
    """
    report = f"""
# BankSec MVP to Enterprise Migration Report

## Migration Summary
- Source Directory: {source_dir}
- Target Directory: {target_dir}
- Migration Date: {__import__('datetime').datetime.now().isoformat()}

## Files Migrated

### Backend Files
- database.py → src/adapters/database/models.py
- auth.py → src/service/use_cases/auth_use_cases.py  
- simulation_engine.py → src/service/simulation/simulation_service.py
- attack_scenarios.py → src/domain/models/scenario_templates.py
- app.py → src/entrypoints/api/legacy_app.py

### Frontend Files
- All frontend files → frontend/

## Next Steps Required

### 1. Refactor Domain Models (High Priority)
- [ ] Convert database models to pure domain entities
- [ ] Remove SQLAlchemy dependencies from domain models
- [ ] Create value objects for complex data types
- [ ] Implement domain events if needed

### 2. Implement Repository Pattern (High Priority)
- [ ] Create repository interfaces in domain layer
- [ ] Implement SQLAlchemy repositories in adapters layer
- [ ] Add unit of work pattern for transactions
- [ ] Implement caching layer with Redis

### 3. Refactor Services (Medium Priority)
- [ ] Move business logic from controllers to use cases
- [ ] Implement dependency injection
- [ ] Add proper error handling and validation
- [ ] Create service interfaces

### 4. Update Entrypoints (Medium Priority)
- [ ] Convert Flask routes to RESTful API endpoints
- [ ] Implement proper request/response DTOs
- [ ] Add authentication middleware
- [ ] Implement proper error handling

### 5. Infrastructure Setup (Medium Priority)
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for caching and sessions
- [ ] Set up Celery for background tasks
- [ ] Configure logging and monitoring

### 6. Testing (Low Priority)
- [ ] Add unit tests for domain models
- [ ] Add integration tests for repositories
- [ ] Add API tests for endpoints
- [ ] Add end-to-end tests

### 7. Documentation (Low Priority)
- [ ] Update API documentation
- [ ] Create deployment guides
- [ ] Write user guides
- [ ] Create architecture documentation

## Migration Commands

### To continue with Step 2 (Database & Redis):
```bash
cd {target_dir}
# Install dependencies
pip install -r requirements.txt
# Set up PostgreSQL
export DATABASE_URL=postgresql://user:password@localhost/banksec_enterprise
# Set up Redis
export REDIS_URL=redis://localhost:6379/0
# Run database migrations
flask db upgrade
```

### To run the application:
```bash
export FLASK_APP=src.entrypoints.api.app
export FLASK_ENV=development
flask run
```

## Important Notes

1. **Backward Compatibility**: The migration maintains backward compatibility by keeping the original routes functional.

2. **Gradual Migration**: You can run both old and new systems in parallel during the transition period.

3. **Data Migration**: Database schema changes will be handled through Alembic migrations in Step 2.

4. **Testing**: Ensure thorough testing at each step before proceeding to the next.

## Support

For questions or issues during migration:
- Check the migration guide in docs/migration.md
- Review the architecture documentation in docs/architecture.md
- Contact the development team

---
Generated by BankSec Migration Script
"""
    
    report_path = Path(target_dir) / "MIGRATION_REPORT.md"
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"📝 Migration report created: {report_path}")

def main():
    """Main migration function"""
    if len(sys.argv) != 3:
        print("Usage: python migrate_mvp.py <source_directory> <target_directory>")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    target_dir = sys.argv[2]
    
    print("🚀 Starting BankSec MVP to Enterprise migration...")
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    
    # Validate source directory
    if not os.path.exists(source_dir):
        print(f"❌ Source directory does not exist: {source_dir}")
        sys.exit(1)
    
    # Create target directory
    os.makedirs(target_dir, exist_ok=True)
    
    try:
        # Migrate backend structure
        backend_source = os.path.join(source_dir, "backend")
        migrate_backend_structure(backend_source, target_dir)
        
        # Migrate frontend structure
        frontend_source = os.path.join(source_dir, "frontend")
        migrate_frontend_structure(frontend_source, target_dir)
        
        # Create migration report
        create_migration_report(source_dir, target_dir)
        
        print("\n🎉 Migration completed successfully!")
        print(f"📁 New structure created in: {target_dir}")
        print("📖 Review MIGRATION_REPORT.md for next steps")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()