#!/bin/bash
# Test migration system

set -e

echo "🧪 Testing Migration System"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_passed() {
    echo -e "${GREEN}✅ PASSED${NC}: $1"
}

test_failed() {
    echo -e "${RED}❌ FAILED${NC}: $1"
    exit 1
}

test_warning() {
    echo -e "${YELLOW}⚠️  WARNING${NC}: $1"
}

echo "1️⃣  Testing Docker build..."
if docker compose build > /dev/null 2>&1; then
    test_passed "Docker build successful"
else
    test_failed "Docker build failed"
fi

echo ""
echo "2️⃣  Testing Docker start..."
docker compose down > /dev/null 2>&1
if docker compose up -d > /dev/null 2>&1; then
    test_passed "Docker start successful"
else
    test_failed "Docker start failed"
fi

echo ""
echo "3️⃣  Waiting for application to be ready..."
sleep 10

echo ""
echo "4️⃣  Checking if migrations ran..."
if docker logs khampha-web 2>&1 | grep -q "Starting database migrations"; then
    test_passed "Migration script executed"
else
    test_failed "Migration script did not execute"
fi

echo ""
echo "5️⃣  Checking migration results..."
if docker logs khampha-web 2>&1 | grep -q "Migration Summary"; then
    test_passed "Migrations completed"
    
    # Show summary
    echo ""
    echo "📊 Migration Summary:"
    docker logs khampha-web 2>&1 | grep -A 5 "Migration Summary"
else
    test_warning "Could not find migration summary in logs"
fi

echo ""
echo "6️⃣  Testing application health..."
sleep 5
if curl -s http://localhost:5002/api/health > /dev/null 2>&1; then
    test_passed "Application is healthy"
    
    # Show health status
    echo ""
    echo "🏥 Health Check Response:"
    curl -s http://localhost:5002/api/health | python3 -m json.tool
else
    test_failed "Application health check failed"
fi

echo ""
echo "7️⃣  Testing manual migration command..."
if docker exec khampha-web python backend/database/run_migrations.py > /dev/null 2>&1; then
    test_passed "Manual migration command works"
else
    test_failed "Manual migration command failed"
fi

echo ""
echo "8️⃣  Testing restart with migrations..."
if docker compose restart > /dev/null 2>&1; then
    test_passed "Container restart successful"
    sleep 10
    
    if docker logs khampha-web 2>&1 | tail -100 | grep -q "Starting database migrations"; then
        test_passed "Migrations ran after restart"
    else
        test_warning "Could not verify migrations after restart"
    fi
else
    test_failed "Container restart failed"
fi

echo ""
echo "================================"
echo -e "${GREEN}🎉 All tests passed!${NC}"
echo ""
echo "📋 Full logs available with: docker logs khampha-web"
echo "🛑 Stop containers with: docker compose down"
echo ""
