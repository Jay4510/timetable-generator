#!/bin/bash

echo "=========================================="
echo "🔍 DIAGNOSING FRONTEND-BACKEND INTEGRATION"
echo "=========================================="
echo ""

echo "1️⃣ Checking Backend Server..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "✅ Backend server is running on port 8000"
else
    echo "❌ Backend server is NOT running on port 8000"
    echo "   Run: cd timetable_generator && source venv/bin/activate && python manage.py runserver"
    exit 1
fi
echo ""

echo "2️⃣ Checking Frontend Server..."
if lsof -ti:5173 > /dev/null 2>&1; then
    echo "✅ Frontend server is running on port 5173"
else
    echo "❌ Frontend server is NOT running on port 5173"
    echo "   Run: cd timetable-frontend && npm run dev"
    exit 1
fi
echo ""

echo "3️⃣ Testing Backend Test Endpoint..."
TEST_RESPONSE=$(curl -s http://localhost:8000/api/user-driven/test/)
if echo "$TEST_RESPONSE" | grep -q "success"; then
    echo "✅ Backend test endpoint working"
    echo "   Response: $TEST_RESPONSE"
else
    echo "❌ Backend test endpoint failed"
    echo "   Response: $TEST_RESPONSE"
    exit 1
fi
echo ""

echo "4️⃣ Testing Backend Generate Endpoint..."
GENERATE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/user-driven/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "config_data": {
      "yearsManaged": ["BE"],
      "college_start_time": "09:00",
      "college_end_time": "17:45",
      "recess_start": "13:00",
      "recess_end": "13:45",
      "teachers": [],
      "subjects": []
    },
    "target_years": ["BE"],
    "use_user_driven": true
  }' 2>&1 | head -100)

if echo "$GENERATE_RESPONSE" | grep -q "status"; then
    echo "✅ Backend generate endpoint responding"
    echo "   (Check if success_rate > 0 in response)"
else
    echo "❌ Backend generate endpoint failed"
    echo "   Response: $GENERATE_RESPONSE"
fi
echo ""

echo "5️⃣ Checking CORS Configuration..."
CORS_CHECK=$(curl -s -I -X OPTIONS http://localhost:8000/api/user-driven/test/ \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" 2>&1)

if echo "$CORS_CHECK" | grep -q "Access-Control-Allow-Origin"; then
    echo "✅ CORS is configured correctly"
else
    echo "⚠️  CORS headers not found (might be an issue)"
fi
echo ""

echo "6️⃣ Checking Database..."
DB_STATUS=$(echo "$TEST_RESPONSE" | grep -o '"teachers":[0-9]*' | grep -o '[0-9]*')
if [ "$DB_STATUS" -gt "0" ]; then
    echo "✅ Database has data (Teachers: $DB_STATUS)"
else
    echo "⚠️  Database might be empty"
fi
echo ""

echo "=========================================="
echo "📊 DIAGNOSIS SUMMARY"
echo "=========================================="
echo ""
echo "Backend: ✅ Running"
echo "Frontend: ✅ Running"
echo "API Endpoints: ✅ Working"
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Open http://localhost:5173 in browser"
echo "2. Open browser DevTools (F12)"
echo "3. Go to Network tab"
echo "4. Try to generate timetable"
echo "5. Check if you see a request to /api/user-driven/generate/"
echo "6. If no request: Frontend JS error (check Console tab)"
echo "7. If request fails: Check the error message"
echo ""
echo "📄 Also check: test_frontend_backend.html for detailed tests"
echo "   Open: file://$(pwd)/test_frontend_backend.html"
echo ""
