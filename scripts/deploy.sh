#!/bin/bash

# LearnHouse Deployment Script
# This script handles deployment of LearnHouse applications

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/learnhouse"
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env.production"
BACKUP_DIR="/opt/learnhouse/backups"
LOG_FILE="/var/log/learnhouse-deploy.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if project directory exists
    if [[ ! -d "$PROJECT_DIR" ]]; then
        print_error "Project directory $PROJECT_DIR does not exist"
        exit 1
    fi
    
    # Check if environment file exists
    if [[ ! -f "$PROJECT_DIR/$ENV_FILE" ]]; then
        print_error "Environment file $PROJECT_DIR/$ENV_FILE does not exist"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create backup
create_backup() {
    print_status "Creating backup..."
    
    BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/backup_$BACKUP_DATE"
    
    mkdir -p "$BACKUP_PATH"
    
    # Backup docker-compose file
    cp "$PROJECT_DIR/$COMPOSE_FILE" "$BACKUP_PATH/"
    
    # Backup environment file
    cp "$PROJECT_DIR/$ENV_FILE" "$BACKUP_PATH/"
    
    # Backup database if PostgreSQL is running
    if docker ps | grep -q postgres; then
        docker exec learnhouse-api pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_PATH/database.sql" 2>/dev/null || print_warning "Could not backup database"
    fi
    
    print_success "Backup created at $BACKUP_PATH"
}

# Pull latest images
pull_images() {
    print_status "Pulling latest images..."
    
    cd "$PROJECT_DIR"
    
    # Pull images for all services
    docker-compose -f "$COMPOSE_FILE" pull
    
    print_success "Images pulled successfully"
}

# Deploy services
deploy_services() {
    print_status "Deploying services..."
    
    cd "$PROJECT_DIR"
    
    # Stop services gracefully
    docker-compose -f "$COMPOSE_FILE" down
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    print_success "Services deployed successfully"
}

# Health check
health_check() {
    print_status "Performing health checks..."
    
    # Wait for services to start
    sleep 30
    
    # Check API health
    API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/health || echo "000")
    if [[ "$API_HEALTH" == "200" ]]; then
        print_success "API health check passed"
    else
        print_error "API health check failed (HTTP $API_HEALTH)"
        return 1
    fi
    
    # Check Web health
    WEB_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health || echo "000")
    if [[ "$WEB_HEALTH" == "200" ]]; then
        print_success "Web health check passed"
    else
        print_error "Web health check failed (HTTP $WEB_HEALTH)"
        return 1
    fi
    
    print_success "All health checks passed"
}

# Cleanup old images
cleanup() {
    print_status "Cleaning up old images..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove old backups (keep last 5)
    find "$BACKUP_DIR" -type d -name "backup_*" | sort -r | tail -n +6 | xargs rm -rf 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Rollback function
rollback() {
    print_warning "Initiating rollback..."
    
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR" | head -1)
    
    if [[ -z "$LATEST_BACKUP" ]]; then
        print_error "No backup found for rollback"
        exit 1
    fi
    
    BACKUP_PATH="$BACKUP_DIR/$LATEST_BACKUP"
    
    print_status "Rolling back to backup: $LATEST_BACKUP"
    
    # Restore docker-compose file
    cp "$BACKUP_PATH/$COMPOSE_FILE" "$PROJECT_DIR/"
    
    # Restore environment file
    cp "$BACKUP_PATH/$ENV_FILE" "$PROJECT_DIR/"
    
    # Restore database if backup exists
    if [[ -f "$BACKUP_PATH/database.sql" ]]; then
        docker exec -i learnhouse-api psql -U "$POSTGRES_USER" "$POSTGRES_DB" < "$BACKUP_PATH/database.sql" || print_warning "Could not restore database"
    fi
    
    # Deploy services
    deploy_services
    
    # Health check
    if health_check; then
        print_success "Rollback completed successfully"
    else
        print_error "Rollback failed"
        exit 1
    fi
}

# Show logs
show_logs() {
    print_status "Showing logs..."
    cd "$PROJECT_DIR"
    docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
}

# Main deployment function
deploy() {
    log "Starting deployment..."
    
    check_prerequisites
    create_backup
    pull_images
    deploy_services
    
    if health_check; then
        cleanup
        print_success "🚀 Deployment completed successfully!"
        log "Deployment completed successfully"
    else
        print_error "❌ Deployment failed!"
        log "Deployment failed"
        
        # Ask for rollback
        read -p "Do you want to rollback? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rollback
        else
            exit 1
        fi
    fi
}

# Show usage
usage() {
    echo "Usage: $0 {deploy|rollback|logs|status}"
    echo ""
    echo "Commands:"
    echo "  deploy   - Deploy the application"
    echo "  rollback - Rollback to previous version"
    echo "  logs     - Show application logs"
    echo "  status   - Show service status"
}

# Show service status
show_status() {
    print_status "Service status:"
    cd "$PROJECT_DIR"
    docker-compose -f "$COMPOSE_FILE" ps
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        check_root
        deploy
        ;;
    rollback)
        check_root
        rollback
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    *)
        usage
        exit 1
        ;;
esac