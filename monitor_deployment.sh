#!/bin/bash

# SAIA Wazen Monitoring and Maintenance Script
# This script provides monitoring and maintenance commands for the deployed application

NAMESPACE="saia-wazen"
DOMAIN="your-domain.com"  # Update with your actual domain

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check deployment status
check_deployment_status() {
    print_header "DEPLOYMENT STATUS"
    
    echo "Checking namespace: $NAMESPACE"
    kubectl get namespace $NAMESPACE 2>/dev/null || {
        print_error "Namespace $NAMESPACE not found!"
        return 1
    }
    
    echo ""
    print_status "Pods Status:"
    kubectl get pods -n $NAMESPACE -o wide
    
    echo ""
    print_status "Services Status:"
    kubectl get services -n $NAMESPACE
    
    echo ""
    print_status "Ingress Status:"
    kubectl get ingress -n $NAMESPACE
    
    echo ""
    print_status "Persistent Volume Claims:"
    kubectl get pvc -n $NAMESPACE
}

# Function to check application health
check_application_health() {
    print_header "APPLICATION HEALTH CHECK"
    
    # Check if pods are ready
    READY_PODS=$(kubectl get pods -n $NAMESPACE -l app=saia-app --no-headers | grep "Running" | grep "1/1" | wc -l)
    TOTAL_PODS=$(kubectl get pods -n $NAMESPACE -l app=saia-app --no-headers | wc -l)
    
    echo "Ready Pods: $READY_PODS/$TOTAL_PODS"
    
    if [ "$READY_PODS" -eq "$TOTAL_PODS" ] && [ "$TOTAL_PODS" -gt 0 ]; then
        print_status "All application pods are healthy"
    else
        print_warning "Some application pods are not ready"
    fi
    
    # Test widget API endpoint
    echo ""
    print_status "Testing Widget API endpoint..."
    if curl -s -f "https://$DOMAIN/api/widget/config/wazen/" > /dev/null; then
        print_status "Widget API is responding"
    else
        print_error "Widget API is not responding"
    fi
    
    # Check database connectivity
    echo ""
    print_status "Testing database connectivity..."
    kubectl exec -n $NAMESPACE deployment/saia-app -- python manage.py check --database default 2>/dev/null && {
        print_status "PostgreSQL database connection OK"
    } || {
        print_error "PostgreSQL database connection failed"
    }
    
    kubectl exec -n $NAMESPACE deployment/saia-app -- python manage.py check --database client_db 2>/dev/null && {
        print_status "MySQL database connection OK"
    } || {
        print_error "MySQL database connection failed"
    }
}

# Function to show resource usage
show_resource_usage() {
    print_header "RESOURCE USAGE"
    
    echo "Pod Resource Usage:"
    kubectl top pods -n $NAMESPACE 2>/dev/null || {
        print_warning "Metrics server not available. Install metrics-server to see resource usage."
        return 1
    }
    
    echo ""
    echo "Node Resource Usage:"
    kubectl top nodes
}

# Function to show recent logs
show_logs() {
    print_header "RECENT LOGS"
    
    echo "Application Logs (last 50 lines):"
    kubectl logs -n $NAMESPACE deployment/saia-app --tail=50
    
    echo ""
    echo "Database Logs (PostgreSQL - last 20 lines):"
    kubectl logs -n $NAMESPACE deployment/saia-postgres --tail=20
    
    echo ""
    echo "Redis Logs (last 20 lines):"
    kubectl logs -n $NAMESPACE deployment/saia-redis --tail=20
}

# Function to restart services
restart_services() {
    print_header "RESTARTING SERVICES"
    
    print_warning "This will restart all application pods. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        kubectl rollout restart deployment/saia-app -n $NAMESPACE
        print_status "Application restart initiated"
        
        echo "Waiting for rollout to complete..."
        kubectl rollout status deployment/saia-app -n $NAMESPACE
        print_status "Application restart completed"
    else
        print_status "Restart cancelled"
    fi
}

# Function to scale application
scale_application() {
    print_header "SCALE APPLICATION"
    
    CURRENT_REPLICAS=$(kubectl get deployment saia-app -n $NAMESPACE -o jsonpath='{.spec.replicas}')
    echo "Current replicas: $CURRENT_REPLICAS"
    
    echo "Enter new replica count (1-10):"
    read -r new_replicas
    
    if [[ "$new_replicas" =~ ^[1-9]$|^10$ ]]; then
        kubectl scale deployment saia-app -n $NAMESPACE --replicas=$new_replicas
        print_status "Scaling to $new_replicas replicas"
        
        echo "Waiting for scaling to complete..."
        kubectl rollout status deployment/saia-app -n $NAMESPACE
        print_status "Scaling completed"
    else
        print_error "Invalid replica count. Must be between 1 and 10."
    fi
}

# Function to backup database
backup_database() {
    print_header "DATABASE BACKUP"
    
    BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
    
    print_status "Creating PostgreSQL backup..."
    kubectl exec -n $NAMESPACE deployment/saia-postgres -- pg_dump -U saia_user saia_db > "backup_postgres_$BACKUP_DATE.sql"
    
    print_status "Creating MySQL backup..."
    kubectl exec -n $NAMESPACE deployment/wazen-mysql -- mysqldump -u wazen_user -p wazen_db > "backup_mysql_$BACKUP_DATE.sql"
    
    print_status "Backups created:"
    echo "  - backup_postgres_$BACKUP_DATE.sql"
    echo "  - backup_mysql_$BACKUP_DATE.sql"
}

# Function to update application
update_application() {
    print_header "UPDATE APPLICATION"
    
    print_warning "This will pull the latest image and restart the application. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        # Force pull latest image
        kubectl patch deployment saia-app -n $NAMESPACE -p '{"spec":{"template":{"metadata":{"annotations":{"kubectl.kubernetes.io/restartedAt":"'$(date +%Y-%m-%dT%H:%M:%S%z)'"}}}}}'
        
        print_status "Update initiated"
        
        echo "Waiting for update to complete..."
        kubectl rollout status deployment/saia-app -n $NAMESPACE
        print_status "Update completed"
    else
        print_status "Update cancelled"
    fi
}

# Main menu
show_menu() {
    echo ""
    print_header "SAIA WAZEN MONITORING & MAINTENANCE"
    echo "1. Check Deployment Status"
    echo "2. Check Application Health"
    echo "3. Show Resource Usage"
    echo "4. Show Recent Logs"
    echo "5. Restart Services"
    echo "6. Scale Application"
    echo "7. Backup Database"
    echo "8. Update Application"
    echo "9. Exit"
    echo ""
    echo -n "Select an option (1-9): "
}

# Main script logic
if [ $# -eq 0 ]; then
    # Interactive mode
    while true; do
        show_menu
        read -r choice
        case $choice in
            1) check_deployment_status ;;
            2) check_application_health ;;
            3) show_resource_usage ;;
            4) show_logs ;;
            5) restart_services ;;
            6) scale_application ;;
            7) backup_database ;;
            8) update_application ;;
            9) echo "Goodbye!"; exit 0 ;;
            *) print_error "Invalid option. Please select 1-9." ;;
        esac
        echo ""
        echo "Press Enter to continue..."
        read -r
    done
else
    # Command line mode
    case $1 in
        status) check_deployment_status ;;
        health) check_application_health ;;
        resources) show_resource_usage ;;
        logs) show_logs ;;
        restart) restart_services ;;
        scale) scale_application ;;
        backup) backup_database ;;
        update) update_application ;;
        *) 
            echo "Usage: $0 [status|health|resources|logs|restart|scale|backup|update]"
            echo "Or run without arguments for interactive mode"
            exit 1
            ;;
    esac
fi
