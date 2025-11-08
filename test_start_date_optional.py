"""
Test script to verify that start_date and end_date are properly saved
even when user doesn't provide start_date in initial message
"""
import sys
sys.path.insert(0, 'backend')

from agents.ai_agent import TravelAgent
from config import Config

# Test cases
test_cases = [
    {
        "message": "Tôi muốn đi Vũng Tàu 2 ngày ngân sách 4.3 triệu, thích ăn hải sản",
        "expected": {
            "has_plan": True,
            "destination": "Vũng Tàu",
            "duration_days": 2,
            "budget": 4300000,
            "should_have_dates": True  # Should auto-generate dates
        }
    },
    {
        "message": "Đi Đà Lạt 3 ngày, ngày 25/12/2025, budget 5 triệu",
        "expected": {
            "has_plan": True,
            "destination": "Đà Lạt",
            "duration_days": 3,
            "budget": 5000000,
            "start_date": "2025-12-25",
            "should_have_dates": True
        }
    }
]

def test_plan_with_dates():
    """Test that plans always have start_date and end_date"""
    print("="*80)
    print("TESTING START_DATE AND END_DATE LOGIC")
    print("="*80)
    
    # Initialize agent
    agent = TravelAgent(api_key=Config.GEMINI_API_KEY)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}")
        print(f"{'='*80}")
        print(f"Message: {test_case['message']}")
        print(f"Expected: {test_case['expected']}")
        
        # Process message
        response = agent.chat(test_case['message'])
        
        print(f"\nResponse:")
        print(f"  has_plan: {response.get('has_plan')}")
        print(f"  mode: {response.get('mode')}")
        
        if response.get('has_plan') and response.get('plan_data'):
            plan = response['plan_data']
            print(f"\nPlan Data:")
            print(f"  destination: {plan.get('destination')}")
            print(f"  duration_days: {plan.get('duration_days')}")
            print(f"  budget: {plan.get('budget')}")
            print(f"  start_date: {plan.get('start_date')}")
            print(f"  end_date: {plan.get('end_date')}")
            
            # Verify
            expected = test_case['expected']
            
            # Check basic fields
            assert plan.get('destination') == expected['destination'], f"Destination mismatch"
            assert plan.get('duration_days') == expected['duration_days'], f"Duration mismatch"
            assert plan.get('budget') == expected['budget'], f"Budget mismatch"
            
            # Check dates
            if expected['should_have_dates']:
                assert plan.get('start_date') is not None, "❌ start_date is missing!"
                assert plan.get('end_date') is not None, "❌ end_date is missing!"
                print(f"\n✅ TEST CASE {i} PASSED - Dates are present")
                
                # If expected has specific start_date, verify it
                if 'start_date' in expected:
                    assert plan.get('start_date') == expected['start_date'], f"Start date mismatch"
                    print(f"✅ Start date matches expected: {expected['start_date']}")
            else:
                print(f"\n✅ TEST CASE {i} PASSED")
        else:
            print(f"\n❌ TEST CASE {i} FAILED - No plan generated")
            print(f"Response: {response.get('message')}")

if __name__ == "__main__":
    test_plan_with_dates()
    print(f"\n{'='*80}")
    print("ALL TESTS COMPLETED")
    print(f"{'='*80}")
