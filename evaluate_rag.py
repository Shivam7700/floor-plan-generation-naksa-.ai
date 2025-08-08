# evaluate_rag.py

import json
from prompt2json import prompt2json
from openai import OpenAI

# --- Configuration ---
# Ensure your API info and client are set up correctly
try:
    with open("api_info.json") as f:
        api_info = json.load(f)
except FileNotFoundError:
    print("Error: api_info.json not found. This script requires it to run.")
    exit()

client = OpenAI(
    api_key=api_info.get("api_key"),
    base_url=api_info.get("base_url"),
)
MODEL_NAME = "llama3:instruct" # Or whatever model you are using

# --- The Evaluation Set ---
# This is where you define your tests. Add as many as you like.
# Each dictionary represents a single test case.
evaluation_set = [
    {
        "test_name": "Core: Kitchen Placement",
        "user_prompt": "A small house with just a kitchen.",
        "expected_room_type": "Kitchen",
        "expected_location": "southeast"
    },
    {
        "test_name": "Core: Master Bedroom Placement",
        "user_prompt": "I need a floor plan for a master bedroom.",
        "expected_room_type": "Bedroom", # Assuming it defaults to Bedroom type
        "expected_location": "southwest"
    },
    {
        "test_name": "Core: Pooja Room (Unsupported Type) Placement",
        "user_prompt": "A simple layout with a pooja room for worship.",
        "expected_room_type": "CommonRoom", # Check if it correctly maps to CommonRoom
        "expected_location": "northeast"
    },
    {
        "test_name": "Correction: User requests wrong Kitchen location",
        "user_prompt": "Design a house with the kitchen in the northeast corner.",
        "expected_room_type": "Kitchen",
        "expected_location": "southeast" # Check if it corrects the user
    },
    {
        "test_name": "Correction: User requests wrong Bedroom location",
        "user_prompt": "I want the master bedroom to be in the east for morning sun.",
        "expected_room_type": "Bedroom",

        "expected_location": "southwest" # Check if it corrects the user
    },
    {
        "test_name": "Combination: Kitchen and Bathroom",
        "user_prompt": "A layout with a kitchen and one bathroom.",
        "expected_room_type": "Bathroom",
        "expected_location": "northwest" # You can add a second check for the kitchen in a more advanced script
    },
    # --- Add more test cases here ---
    # Example:
    # {
    #     "test_name": "Combination: Dining Room Placement",
    #     "user_prompt": "A house with a dining room.",
    #     "expected_room_type": "DiningRoom",
    #     "expected_location": "west" # Or 'north'/'east' based on your Vastu PDF
    # },
]

def run_evaluation():
    """
    Iterates through the evaluation set, tests the RAG system,
    and prints a final performance report.
    """
    print("--- Starting RAG System Performance Evaluation ---")
    
    success_count = 0
    total_tests = len(evaluation_set)
    results = []

    for i, test in enumerate(evaluation_set):
        print(f"\n[Running Test {i+1}/{total_tests}: {test['test_name']}]")
        print(f"  > Prompt: '{test['user_prompt']}'")

        # Call your main function to get the generated data
        _, structured_data, _ = prompt2json(test['user_prompt'], client=client, model=MODEL_NAME)

        test_passed = False
        reason = "Test Failed"

        if structured_data and "rooms" in structured_data and structured_data["rooms"]:
            # Find the room we want to check in the generated list of rooms
            found_room = None
            for room in structured_data["rooms"]:
                # Check against 'type' or 'name' for flexibility (e.g., for Pooja Room)
                if room.get("type") == test["expected_room_type"] or room.get("name") == test.get("expected_name"):
                    found_room = room
                    break
            
            if found_room:
                actual_location = found_room.get("location")
                if actual_location == test["expected_location"]:
                    test_passed = True
                    reason = f"OK (Found '{test['expected_room_type']}' in correct location: '{actual_location}')"
                else:
                    reason = f"FAIL (Found '{test['expected_room_type']}' but in wrong location: '{actual_location}', expected '{test['expected_location']}')"
            else:
                reason = f"FAIL (Could not find room with type '{test['expected_room_type']}')"
        else:
            reason = "FAIL (Generated JSON was empty or malformed)"
        
        if test_passed:
            success_count += 1
            print(f"  > Result: ✅ PASSED - {reason}")
        else:
            print(f"  > Result: ❌ FAILED - {reason}")
        
        results.append({"test_name": test['test_name'], "passed": test_passed, "details": reason})

    # --- Final Report ---
    print("\n\n--- RAG System Evaluation Complete ---")
    print(f"Total Tests Run: {total_tests}")
    print(f"Successful Tests: {success_count}")
    print(f"Failed Tests: {total_tests - success_count}")
    
    accuracy = (success_count / total_tests) * 100 if total_tests > 0 else 0
    print(f"\nOverall Accuracy: {accuracy:.2f}%")
    
    print("\n--- Detailed Results ---")
    for res in results:
        status_icon = "✅" if res["passed"] else "❌"
        print(f"{status_icon} Test: {res['test_name']:<50} | Details: {res['details']}")

if __name__ == "__main__":
    run_evaluation()