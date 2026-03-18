#!/bin/bash

# BankSec Enterprise Startup Script
# Comprehensive startup script with error handling and health checks

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

wait_for_service() {
    local service_name=$1
    local check_command=$2
    local max_attempts=${3:-30}
    local attempt=1
    
    log_info "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if eval "$check_command"; then
            log_success "$service_name is ready"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts: $service_name not ready, waiting..."
        sleep 2
        ((attempt++))
    done
    
    log_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

check_environment() {
    log_info "Checking environment configuration..."
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        log_error ".env file not found. Please copy .env.example to .env and configure it."
        exit 1
    fi
    
    # Load environment variables
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    
    # Check required environment variables
    required_vars=("SECRET_KEY" "DATABASE_URL" "REDIS_URL")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Check if using default secret key
    if [ "$SECRET_KEY" = "your-super-secret-key-here-change-me-immediately" ]; then
        log_error "You MUST change the default SECRET_KEY before running in production"
        exit 1
    fi
    
    log_success "Environment configuration is valid"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! check_command python3; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check pip
    if ! check_command pip3; then
        log_error "pip3 is not installed"
        exit 1
    fi
    
    # Check PostgreSQL client
    if ! check_command psql; then
        log_warning "PostgreSQL client not found. Database operations may fail."
    fi
    
    # Check Redis client
    if ! check_command redis-cli; then
        log_warning "Redis client not found. Cache operations may fail."
    fi
    
    log_success "Dependencies check completed"
}

install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source "$PROJECT_DIR/venv/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        pip install -r "$PROJECT_DIR/requirements.txt"
        log_success "Dependencies installed successfully"
    else
        log_error "requirements.txt not found"
        exit 1
    fi
}

check_database() {
    log_info "Checking database connection..."
    
    # Check if PostgreSQL is running
    if [[ "$DATABASE_URL" == postgresql://* ]]; then
        # Extract database connection details
        db_host=$(echo "$DATABASE_URL" | cut -d'@' -f2 | cut -d':' -f1)
        db_port=$(echo "$DATABASE_URL" | cut -d'@' -f2 | cut -d':' -f2 | cut -d'/' -f1)
        
        if ! wait_for_service "PostgreSQL" "timeout 2 bash -c 'echo > /dev/tcp/$db_host/$db_port'" 30; then
            log_error "PostgreSQL is not accessible at $db_host:$db_port"
            exit 1
        fi
    fi
    
    # Test database connection
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    if python3 -c "
from src.adapters.database.database import get_database_health
health = get_database_health()
exit(0 if health.get('connected') else 1)
"; then
        log_success "Database connection successful"
    else
        log_error "Failed to connect to database"
        exit 1
    fi
}

check_redis() {
    log_info "Checking Redis connection..."
    
    # Extract Redis host and port
    redis_host=$(echo "$REDIS_URL" | cut -d'/' -f3 | cut -d':' -f1)
    redis_port=$(echo "$REDIS_URL" | cut -d'/' -f3 | cut -d':' -f2)
    
    if ! wait_for_service "Redis" "timeout 2 bash -c 'echo > /dev/tcp/$redis_host/$redis_port'" 30; then
        log_error "Redis is not accessible at $redis_host:$redis_port"
        exit 1
    fi
    
    # Test Redis connection
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    if python3 -c "
from src.adapters.cache.redis_cache import RedisCache
try:
    cache = RedisCache()
    exit(0 if cache.ping() else 1)
except Exception:
    exit(1)
"; then
        log_success "Redis connection successful"
    else
        log_error "Failed to connect to Redis"
        exit 1
    fi
}

run_migrations() {
    log_info "Running database migrations..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Set Flask app
    export FLASK_APP=src.entrypoints.api.app
    
    # Run migrations
    if flask db upgrade; then
        log_success "Database migrations completed successfully"
    else
        log_error "Failed to run database migrations"
        exit 1
    fi
}

initialize_database() {
    log_info "Initializing database with sample data..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    if python3 scripts/init_db.py; then
        log_success "Database initialization completed"
    else
        log_error "Failed to initialize database"
        exit 1
    fi
}

start_application() {
    log_info "Starting BankSec Enterprise application..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Set Flask environment
    export FLASK_APP=src.entrypoints.api.app
    
    # Choose startup method based on environment
    if [ "$FLASK_ENV" = "production" ]; then
        log_info "Starting in production mode with Gunicorn..."
        
        # Check if Gunicorn config exists
        if [ -f "config/gunicorn.conf.py" ]; then
            gunicorn --config config/gunicorn.conf.py "src.entrypoints.api.app:create_app()"
        else
            gunicorn -w 4 -b 0.0.0.0:5000 "src.entrypoints.api.app:create_app()"
        fi
    else
        log_info "Starting in development mode with Flask..."
        flask run --host=0.0.0.0 --port=${PORT:-5000}
    fi
}

start_with_docker_compose() {
    log_info "Starting with Docker Compose..."
    
    cd "$PROJECT_DIR"
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Start services
    if docker-compose up -d; then
        log_success "Services started with Docker Compose"
        
        # Show service status
        log_info "Service status:"
        docker-compose ps
        
        # Show logs
        log_info "Recent logs:"
        docker-compose logs --tail=50
        
        # Show URLs
        echo
        log_info "Application URLs:"
        echo "  - Application: http://localhost:5000"
        echo "  - Health Check: http://localhost:5000/health"
        echo "  - Prometheus: http://localhost:9090"
        echo "  - Grafana: http://localhost:3000"
        echo
    else
        log_error "Failed to start services with Docker Compose"
        exit 1
    fi
}

show_help() {
    echo "BankSec Enterprise Startup Script"
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --dev           Start in development mode (default)"
    echo "  --prod          Start in production mode"
    echo "  --docker        Start with Docker Compose"
    echo "  --init          Initialize database with sample data"
    echo "  --reset         Reset database (WARNING: destroys all data)"
    echo "  --check         Check environment and dependencies only"
    echo "  --help          Show this help message"
    echo
    echo "Examples:"
    echo "  $0              # Start in development mode"
    echo "  $0 --prod       # Start in production mode"
    echo "  $0 --docker     # Start with Docker Compose"
    echo "  $0 --init       # Initialize database"
}

# Main execution
main() {
    local mode="dev"
    local init_db=false
    local reset_db=false
    local check_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                mode="dev"
                shift
                ;;
            --prod)
                mode="prod"
                shift
                ;;
            --docker)
                mode="docker"
                shift
                ;;
            --init)
                init_db=true
                shift
                ;;
            --reset)
                reset_db=true
                shift
                ;;
            --check)
                check_only=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Banner
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    BankSec Enterprise                        ║"
    echo "║              Cybersecurity Training Platform                 ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    
    # Check environment
    check_environment
    
    if [ "$mode" = "docker" ]; then
        start_with_docker_compose
        exit 0
    fi
    
    # Check dependencies
    check_dependencies
    
    # Install dependencies
    install_dependencies
    
    # Database operations
    if [ "$reset_db" = true ]; then
        log_warning "Resetting database (all data will be lost)..."
        reset_database
        init_db=true
    fi
    
    if [ "$init_db" = true ]; then
        # Check database connection
        check_database
        
        # Run migrations
        run_migrations
        
        # Initialize database
        initialize_database
        
        exit 0
    fi
    
    # Check services
    check_database
    check_redis
    
    # Run migrations if needed
    if [ "$mode" = "prod" ]; then
        run_migrations
    fi
    
    if [ "$check_only" = true ]; then
        log_success "Environment check completed successfully"
        exit 0
    fi
    
    # Start application
    start_application
}

# Run main function
main "$@"