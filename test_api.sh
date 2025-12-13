#!/bin/bash

echo "================================================================================"
echo "🧪 TESTING FIXED ALGORITHM v2.0"
echo "================================================================================"
echo ""
echo "📤 Sending request to generate timetable..."
echo ""

curl -X POST http://127.0.0.1:8000/api/generate-timetable/ \
  -H "Content-Type: application/json" \
  -d '{
    "use_user_driven": true,
    "target_years": ["SE", "TE"],
    "config_data": {
      "college_start_time": "09:00",
      "college_end_time": "17:45",
      "recess_start": "13:00",
      "recess_end": "13:45"
    }
  }' \
  -w "\n\n📊 Response Status: %{http_code}\n" \
  | python3 -m json.tool 2>/dev/null || cat

echo ""
echo "================================================================================"
echo "✅ Test complete!"
echo ""
echo "💡 Look for:"
echo "   1. 'algorithm': 'User-Driven Timetable Algorithm (FIXED v2.0)'"
echo "   2. 'success_metrics' section with success_rate"
echo "   3. 'fitness_score' in each division result"
echo ""
echo "📖 For detailed testing, see: TESTING_GUIDE.md"
echo "================================================================================"
