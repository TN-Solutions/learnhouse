#!/bin/bash

# LearnHouse Health Check Script
# This script performs comprehensive health checks for LearnHouse services

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
LOG_FILE="/var/log/learnhouse-health.log"
WEBHOOK_URL="${HEALTH_WEBHOOK_URL:-}"

# Health check endpoints
API_HEALTH_URL="http://localhost:9000/health"
WEB_HEALTH_URL="http://localhost:3000/api/health"

# Thresholds
MAX_RESPONSE_TIME=5  # seconds
MAX_CPU_USAGE=80     # percentage
MAX_MEMORY_USAGE=85  # percentage
MAX_DISK_USAGE=90    # percentage

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

# Send notification
send_notification() {
    local status="$1"
    local message="$2"
    
    if [[ -n "$WEBHOOK_URL" ]]; then
        curl -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"status\": \"$status\", \"message\": \"$message\", \"timestamp\": \"$(date -Iseconds)\"}" \
            2>/dev/null || true
    fi
}

# Check HTTP endpoint
check_http_endpoint() {
    local url="$1"
    local service_name="$2"
    
    print_status "Checking $service_name health endpoint..."
    
    # Measure response time
    start_time=$(date +%s.%N)
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    end_time=$(date +%s.%N)
    response_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    
    if [[ "$http_code" == "200" ]]; then
        if (( $(echo "$response_time <= $MAX_RESPONSE_TIME" | bc -l 2>/dev/null || echo "1") )); then
            print_success "$service_name is healthy (${response_time}s)"
            log "$service_name health check passed (${response_time}s)"
            return 0
        else
            print_warning "$service_name response time is high: ${response_time}s"
            log "$service_name response time warning: ${response_time}s"
            return 1
        fi
    else
        print_error "$service_name health check failed (HTTP $http_code)"
        log "$service_name health check failed (HTTP $http_code)"
        return 1
    fi
}

# Check Docker containers
check_containers() {
    print_status "Checking Docker containers..."
    
    cd "$PROJECT_DIR"
    
    local failed_containers=()
    
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            local container_name=$(echo "$line" | awk '{print $1}')
            local status=$(echo "$line" | awk '{print $2}')
            
            if [[ "$status" != "Up" ]]; then
                failed_containers+=("$container_name")
                print_error "Container $container_name is not running (status: $status)"
            else
                print_success "Container $container_name is running"
            fi
        fi
    done < <(docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Name}}\t{{.Status}}" | tail -n +2)
    
    if [[ ${#failed_containers[@]} -eq 0 ]]; then
        print_success "All containers are running"
        log "All containers are running"
        return 0
    else
        log "Failed containers: ${failed_containers[*]}"
        return 1
    fi
}

# Check system resources
check_system_resources() {
    print_status "Checking system resources..."
    
    local issues=0
    
    # Check CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//' 2>/dev/null || echo "0")
    if (( $(echo "$cpu_usage > $MAX_CPU_USAGE" | bc -l 2>/dev/null || echo "0") )); then
        print_warning "High CPU usage: ${cpu_usage}%"
        log "High CPU usage: ${cpu_usage}%"
        ((issues++))
    else
        print_success "CPU usage is normal: ${cpu_usage}%"
    fi
    
    # Check memory usage
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}' 2>/dev/null || echo "0")
    if (( $(echo "$memory_usage > $MAX_MEMORY_USAGE" | bc -l 2>/dev/null || echo "0") )); then
        print_warning "High memory usage: ${memory_usage}%"
        log "High memory usage: ${memory_usage}%"
        ((issues++))
    else
        print_success "Memory usage is normal: ${memory_usage}%"
    fi
    
    # Check disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//' 2>/dev/null || echo "0")
    if [[ "$disk_usage" -gt "$MAX_DISK_USAGE" ]]; then
        print_warning "High disk usage: ${disk_usage}%"
        log "High disk usage: ${disk_usage}%"
        ((issues++))
    else
        print_success "Disk usage is normal: ${disk_usage}%"
    fi
    
    if [[ "$issues" -eq 0 ]]; then
        print_success "System resources are within normal limits"
        log "System resources check passed"
        return 0
    else
        log "System resource issues detected: $issues"
        return 1
    fi
}

# Check database connectivity
check_database() {
    print_status "Checking database connectivity..."
    
    cd "$PROJECT_DIR"
    
    # Check if API container can connect to database
    if docker-compose -f "$COMPOSE_FILE" exec -T api python -c "
import os
import psycopg2
from urllib.parse import urlparse

try:
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        print('DATABASE_URL not set')
        exit(1)
    
    parsed = urlparse(db_url)
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path[1:],
        user=parsed.username,
        password=parsed.password,
        connect_timeout=5
    )
    conn.close()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
        print_success "Database connectivity is working"
        log "Database connectivity check passed"
        return 0
    else
        print_error "Database connectivity failed"
        log "Database connectivity check failed"
        return 1
    fi
}

# Check Redis connectivity
check_redis() {
    print_status "Checking Redis connectivity..."
    
    cd "$PROJECT_DIR"
    
    # Check if API container can connect to Redis
    if docker-compose -f "$COMPOSE_FILE" exec -T api python -c "
import os
import redis
from urllib.parse import urlparse

try:
    redis_url = os.environ.get('REDIS_URL', '')
    if not redis_url:
        print('REDIS_URL not set')
        exit(1)
    
    parsed = urlparse(redis_url)
    r = redis.Redis(
        host=parsed.hostname,
        port=parsed.port or 6379,
        password=parsed.password,
        socket_connect_timeout=5
    )
    r.ping()
    print('Redis connection successful')
except Exception as e:
    print(f'Redis connection failed: {e}')
    exit(1)
" 2>/dev/null; then
        print_success "Redis connectivity is working"
        log "Redis connectivity check passed"
        return 0
    else
        print_error "Redis connectivity failed"
        log "Redis connectivity check failed"
        return 1
    fi
}

# Generate health report
generate_report() {
    local overall_status="$1"
    local failed_checks="$2"
    
    print_status "Generating health report..."
    
    local report_file="/tmp/learnhouse-health-report-$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "overall_status": "$overall_status",
    "checks": {
        "api_health": $(check_http_endpoint "$API_HEALTH_URL" "API" && echo "true" || echo "false"),
        "web_health": $(check_http_endpoint "$WEB_HEALTH_URL" "Web" && echo "true" || echo "false"),
        "containers": $(check_containers && echo "true" || echo "false"),
        "system_resources": $(check_system_resources && echo "true" || echo "false"),
        "database": $(check_database && echo "true" || echo "false"),
        "redis": $(check_redis && echo "true" || echo "false")
    },
    "failed_checks": [$failed_checks],
    "system_info": {
        "hostname": "$(hostname)",
        "uptime": "$(uptime -p 2>/dev/null || echo 'Unknown')",
        "kernel": "$(uname -r)",
        "docker_version": "$(docker --version 2>/dev/null || echo 'Unknown')"
    }
}
EOF
    
    print_success "Health report generated: $report_file"
    log "Health report generated: $report_file"
}

# Main health check function
run_health_checks() {
    print_status "Starting comprehensive health checks..."
    log "Starting health checks"
    
    local failed_checks=""
    local overall_status="healthy"
    
    # Run individual checks
    if ! check_http_endpoint "$API_HEALTH_URL" "API"; then
        failed_checks+="\"api_health\","
        overall_status="unhealthy"
    fi
    
    if ! check_http_endpoint "$WEB_HEALTH_URL" "Web"; then
        failed_checks+="\"web_health\","
        overall_status="unhealthy"
    fi
    
    if ! check_containers; then
        failed_checks+="\"containers\","
        overall_status="degraded"
    fi
    
    if ! check_system_resources; then
        failed_checks+="\"system_resources\","
        overall_status="degraded"
    fi
    
    if ! check_database; then
        failed_checks+="\"database\","
        overall_status="unhealthy"
    fi
    
    if ! check_redis; then
        failed_checks+="\"redis\","
        overall_status="unhealthy"
    fi
    
    # Remove trailing comma
    failed_checks="${failed_checks%,}"
    
    # Generate report
    generate_report "$overall_status" "$failed_checks"
    
    # Send notification if needed
    if [[ "$overall_status" != "healthy" ]]; then
        send_notification "$overall_status" "LearnHouse health check failed: $failed_checks"
    fi
    
    # Print final status
    if [[ "$overall_status" == "healthy" ]]; then
        print_success "🟢 All health checks passed!"
        log "All health checks passed"
        return 0
    elif [[ "$overall_status" == "degraded" ]]; then
        print_warning "🟡 System is degraded (some warnings)"
        log "System is degraded"
        return 1
    else
        print_error "🔴 System is unhealthy (critical issues)"
        log "System is unhealthy"
        return 2
    fi
}

# Show usage
usage() {
    echo "Usage: $0 {check|api|web|containers|resources|database|redis}"
    echo ""
    echo "Commands:"
    echo "  check      - Run all health checks"
    echo "  api        - Check API health endpoint"
    echo "  web        - Check Web health endpoint"
    echo "  containers - Check Docker containers"
    echo "  resources  - Check system resources"
    echo "  database   - Check database connectivity"
    echo "  redis      - Check Redis connectivity"
}

# Main script logic
case "${1:-check}" in
    check)
        run_health_checks
        ;;
    api)
        check_http_endpoint "$API_HEALTH_URL" "API"
        ;;
    web)
        check_http_endpoint "$WEB_HEALTH_URL" "Web"
        ;;
    containers)
        check_containers
        ;;
    resources)
        check_system_resources
        ;;
    database)
        check_database
        ;;
    redis)
        check_redis
        ;;
    *)
        usage
        exit 1
        ;;
esac