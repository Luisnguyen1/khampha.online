"""
Test script to verify start_date and end_date are saved to database
"""
import requests
import json

# Test message
test_message = "Tôi muốn lên kế hoạch đi Hà Nội, 3 ngày 2 đêm vào ngày 15/11/2025, tôi muốn đi ăn nhiều món ngon, chi phí khoảng 8 triệu"

print("="*80)
print("TESTING PLAN SAVE WITH DATES")
print("="*80)
print(f"\nSending message: {test_message}")

# Send chat request
response = requests.post(
    'http://localhost:5002/api/chat',  # Changed to port 5002
    json={
        'message': test_message,
        'session_id': 'test_session_dates_123'
    },
    headers={'Content-Type': 'application/json'}
)

print(f"\n{'='*80}")
print("CHAT API RESPONSE")
print(f"{'='*80}")

if response.status_code == 200:
    data = response.json()
    print(f"Success: {data.get('success')}")
    print(f"Has plan: {data.get('has_plan')}")
    print(f"Plan ID: {data.get('plan_id')}")
    
    if data.get('plan_id'):
        plan_id = data['plan_id']
        
        # Get plan details
        print(f"\n{'='*80}")
        print(f"RETRIEVING PLAN {plan_id} FROM DATABASE")
        print(f"{'='*80}")
        
        plan_response = requests.get(f'http://localhost:5002/api/plans/{plan_id}')  # Changed to port 5002
        
        if plan_response.status_code == 200:
            plan_data = plan_response.json()
            
            if plan_data.get('success'):
                plan = plan_data['plan']
                print(f"\n✅ Plan retrieved successfully:")
                print(f"   ID: {plan.get('id')}")
                print(f"   Name: {plan.get('plan_name')}")
                print(f"   Destination: {plan.get('destination')}")
                print(f"   Duration: {plan.get('duration_days')} days")
                print(f"   Budget: {plan.get('budget')}")
                print(f"   Preferences: {plan.get('preferences')}")
                print(f"   ⭐ START DATE: {plan.get('start_date')}")
                print(f"   ⭐ END DATE: {plan.get('end_date')}")
                print(f"   Status: {plan.get('status')}")
                
                if plan.get('start_date') and plan.get('end_date'):
                    print(f"\n{'='*80}")
                    print("✅✅✅ SUCCESS! Dates are saved correctly!")
                    print(f"{'='*80}")
                else:
                    print(f"\n{'='*80}")
                    print("❌❌❌ FAILURE! Dates are NULL in database!")
                    print(f"{'='*80}")
            else:
                print(f"❌ Failed to get plan: {plan_data.get('error')}")
        else:
            print(f"❌ API error: {plan_response.status_code}")
    else:
        print("\n❌ No plan_id returned - plan was not created")
        print(f"Response: {data.get('response')}")
else:
    print(f"❌ Chat request failed: {response.status_code}")
    print(f"Response: {response.text}")

print(f"\n{'='*80}")
print("TEST COMPLETED")
print(f"{'='*80}")
