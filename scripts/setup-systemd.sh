#!/bin/bash

# LearnHouse Systemd Service Setup Script
# This script sets up systemd service for LearnHouse

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="learnhouse"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
PROJECT_DIR="/opt/learnhouse"
DEPLOYMENT_SCRIPT="/opt/learnhouse/scripts/deploy.sh"

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
    
    # Check if deployment script exists
    if [[ ! -f "$DEPLOYMENT_SCRIPT" ]]; then
        print_error "Deployment script $DEPLOYMENT_SCRIPT does not exist"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create systemd service
create_service() {
    print_status "Creating systemd service..."
    
    # Copy service file
    cp "$(dirname "$0")/learnhouse.service" "$SERVICE_FILE"
    
    # Replace placeholders if needed
    sed -i "s|/opt/learnhouse|$PROJECT_DIR|g" "$SERVICE_FILE"
    
    # Set proper permissions
    chmod 644 "$SERVICE_FILE"
    
    print_success "Systemd service created at $SERVICE_FILE"
}

# Enable and start service
enable_service() {
    print_status "Enabling and starting systemd service..."
    
    # Reload systemd daemon
    systemctl daemon-reload
    
    # Enable service to start on boot
    systemctl enable "$SERVICE_NAME"
    
    # Start service
    systemctl start "$SERVICE_NAME"
    
    print_success "Service enabled and started"
}

# Show service status
show_status() {
    print_status "Service status:"
    systemctl status "$SERVICE_NAME" --no-pager
}

# Test service
test_service() {
    print_status "Testing service..."
    
    # Check if service is running
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Service is running"
    else
        print_error "Service is not running"
        return 1
    fi
    
    # Check if containers are running
    if docker-compose -f "$PROJECT_DIR/docker-compose.production.yml" ps | grep -q "Up"; then
        print_success "Containers are running"
    else
        print_warning "Some containers may not be running"
    fi
}

# Show usage
usage() {
    echo "Usage: $0 {install|status|test|enable|disable|start|stop|restart}"
    echo ""
    echo "Commands:"
    echo "  install  - Install and enable the systemd service"
    echo "  status   - Show service status"
    echo "  test     - Test service functionality"
    echo "  enable   - Enable service to start on boot"
    echo "  disable  - Disable service from starting on boot"
    echo "  start    - Start the service"
    echo "  stop     - Stop the service"
    echo "  restart  - Restart the service"
}

# Install service
install_service() {
    check_root
    check_prerequisites
    create_service
    enable_service
    test_service
    print_success "🚀 LearnHouse systemd service installed successfully!"
}

# Disable service
disable_service() {
    check_root
    print_status "Disabling systemd service..."
    systemctl disable "$SERVICE_NAME"
    print_success "Service disabled"
}

# Start service
start_service() {
    check_root
    print_status "Starting systemd service..."
    systemctl start "$SERVICE_NAME"
    print_success "Service started"
}

# Stop service
stop_service() {
    check_root
    print_status "Stopping systemd service..."
    systemctl stop "$SERVICE_NAME"
    print_success "Service stopped"
}

# Restart service
restart_service() {
    check_root
    print_status "Restarting systemd service..."
    systemctl restart "$SERVICE_NAME"
    print_success "Service restarted"
}

# Main script logic
case "${1:-install}" in
    install)
        install_service
        ;;
    status)
        show_status
        ;;
    test)
        test_service
        ;;
    enable)
        enable_service
        ;;
    disable)
        disable_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    *)
        usage
        exit 1
        ;;
esac