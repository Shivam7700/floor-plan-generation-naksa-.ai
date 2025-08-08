from .jsonFormatting import convert_json_string
from .extractInformation import extract_information
from .extractInformation import update_floor_plan_with_new_description
from .extractInformation import client
import os
from datetime import datetime
from .vastu_rag_engine import get_vastu_context
import json



def save_string_to_file(string, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"{timestamp}.txt"
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(string)

# def prompt2json(prompt, client=client, model="llama3:instruct"):

#     # Call the functions to process the input and convert it into a JSON-formatted string
#     structured_data = extract_information(prompt, client=client, model=model)

#     # save_string_to_file(structured_data, 'IntermediateRes')

#     json_string = convert_json_string(structured_data)

#     return json_string, structured_data

# def prompt2json(prompt: str, client, model="llama3:instruct") -> (str, str):
#     """
#     Converts a user's house description prompt into a Vastu-compliant JSON.
    
#     This function now performs Retrieval-Augmented Generation (RAG):
#     1. Retrieves relevant Vastu rules.
#     2. Injects them into a system prompt for the LLM.
#     3. Calls the LLM to get a Vastu-compliant JSON.
#     """
    
#     # Step 1: Retrieve relevant Vastu rules using the RAG engine.
#     print(f"Fetching Vastu context for prompt: '{prompt}'")
#     vastu_rules_context = get_vastu_context(prompt)
#     print("--- Retrieved Vastu Context ---\n" + vastu_rules_context + "\n-----------------------------")
    
#     # systemPrompt = """
#     # You are an AI that converts house descriptions into a structured JSON format. Given a description of a house or apartment, return a JSON object with a 'rooms' array. Each room must have:
#     # - 'name': A string describing the room (e.g., 'Living Room', 'Bedroom 1').
#     # - 'type': A string indicating the room type, strictly one of 'LivingRoom', 'Bedroom', 'Kitchen', 'Office', 'Bathroom', or 'CommonRoom'. Do NOT use a nested object for 'type'.
#     # - 'description': A string describing the room.
#     # - 'link': An array of strings for connected rooms (use an empty array [] if none).
#     # - 'location': A string like 'center', 'corner', or 'side'.
#     # - 'size': A string like 'S', 'M', or 'L'.
#     # For vague descriptions like '3 bedroom apartment', include a living room, kitchen, and the specified number of bedrooms unless otherwise stated. Ensure 'type' is always a string, never a nested object. Example:
#     # {
#     #   "rooms": [
#     #     {
#     #       "name": "Living Room",
#     #       "type": "LivingRoom",
#     #       "description": "A cozy living room",
#     #       "link": [],
#     #       "location": "center",
#     #       "size": "M"
#     #     },
#     #     {
#     #       "name": "Bedroom 1",
#     #       "type": "Bedroom",
#     #       "description": "A spacious bedroom",
#     #       "link": [],
#     #       "location": "corner",
#     #       "size": "L"
#     #     }
#     #   ]
#     # }
#     # """
#     # systemPrompt = f"""
#     #   You are an AI architectural assistant specializing in Vastu Shastra. Your task is to convert a house description into a structured JSON that strictly adheres to the provided Vastu principles.

#     #   [CRITICAL VASTU SHASTRA RULES - YOU MUST FOLLOW THESE]:
#     #   {vastu_rules_context}

#     #   [INSTRUCTIONS]:
#     #   1. Analyze the user's request below.
#     #   2. Strictly apply the Vastu Shastra rules from the context above. These rules are your highest priority. If the user asks for a room location that violates a Vastu rule, you MUST place it in the correct Vastu location.
#     #   3. Your output MUST be ONLY a JSON object. Do not include any other text, explanations, or markdown formatting like ```json.
#     #   4. The JSON must have a 'rooms' array. Each room object must have:
#     #       - 'name': A string for the room's name (e.g., 'Living Room', 'Master Bedroom').
#     #       - 'type': A string, strictly one of 'LivingRoom', 'Bedroom', 'Kitchen', 'Office', 'Bathroom', or 'CommonRoom'.
#     #       - 'description': A brief string describing the room.
#     #       - 'link': An array of strings for connected rooms (e.g., ["Living Room"]). Use an empty array [] if none.
#     #       - 'location': A string indicating the location (e.g., 'southeast', 'southwest', 'north').
#     #       - 'size': A string indicating size (e.g., 'S', 'M', 'L', 'XL').
#     #   5. If the user gives a vague request like 'a 2 bedroom apartment', infer a standard layout (e.g., add a living room and kitchen) but ensure all rooms follow the Vastu rules.
#     #   """

#     systemPrompt = f"""
#         You are an AI architectural assistant specializing in Vastu Shastra. Your task is to perform two actions:
#         1. Convert a house description into a structured JSON that strictly follows Vastu principles.
#         2. Provide a brief, user-friendly explanation of the main Vastu rules you applied.

#         [CRITICAL VASTU SHASTRA RULES - YOU MUST FOLLOW THESE]:
#         {vastu_rules_context}

#         [ALLOWED ROOM TYPES]:
#         You MUST use ONLY the following strings for the 'type' field: "LivingRoom", "Bedroom", "Kitchen", "Bathroom", "DiningRoom", "Storage", "CommonRoom", "Balcony".

#         [INSTRUCTIONS]:
#         - Analyze the user's request and apply the Vastu rules from the context.
#         - If the user asks for an unsupported room type (e.g., 'Office'), you MUST use the type "CommonRoom" and set the 'name' field to what the user requested.
#         - **Your entire output MUST be a single JSON object.**
#         - This JSON object must contain two top-level keys: "floor_plan" and "explanation".
#         - The "floor_plan" key will contain the room layout JSON object as before.
#         - The "explanation" key will contain a short, 2-3 line string summarizing the key Vastu rules used.

#         [EXAMPLE OUTPUT FORMAT]:
#         {{
#         "floor_plan": {{
#             "rooms": [
#             {{
#                 "name": "Kitchen",
#                 "type": "Kitchen",
#                 "description": "The kitchen area",
#                 "link": [],
#                 "location": "southeast",
#                 "size": "M"
#             }}
#             ]
#         }},
#         "explanation": "This design follows key Vastu principles by placing the Kitchen in the Southeast, the direction of Agni (fire), to promote health and energy."
#         }}
# """

#     structured_data = client.chat.completions.create(
#         model=model,
#         messages=[
#             {"role": "system", "content": systemPrompt},
#             {"role": "user", "content": prompt}
#         ],
#         response_format={"type": "json_object"}
#     ).choices[0].message.content
#     json_string = convert_json_string(structured_data)
#     return json_string, structured_data


def extract_json_block(text: str) -> str:
    """
    Surgically extracts a JSON object from a string that might contain other text.
    It finds the first opening curly brace '{' and the last closing curly brace '}'
    and returns everything in between.
    """
    try:
        # Find the index of the first '{'
        start_index = text.find('{')
        # Find the index of the last '}'
        end_index = text.rfind('}')

        if start_index == -1 or end_index == -1 or end_index < start_index:
            # If '{' or '}' is not found, or they are in the wrong order, return an empty JSON
            print("Warning: Could not find a valid JSON block ('{...}') in the LLM response.")
            return "{}"
        
        # Slice the string to get just the JSON block
        json_str = text[start_index : end_index + 1]
        return json_str
    except Exception as e:
        print(f"Error during JSON extraction: {e}")
        return "{}"

def get_explanation_from_plan(floor_plan_json: str, client, model: str) -> str:
    """
    Makes a second, separate API call to generate an explanation.
    This version now reliably expects a JSON response to avoid model confusion.
    """
    print("\n--- Generating explanation for the created floor plan... ---")
    
    # NEW PROMPT: We now ask for a JSON object with a single key.
    explanation_prompt = f"""
    You are a Vastu Shastra expert. Based on the following floor plan JSON, provide a short, user-friendly, 2-3 line explanation of the key Vastu principles that were followed.

    [FLOOR PLAN JSON]:
    {floor_plan_json}

    [INSTRUCTIONS]:
    - Your output MUST be a single, valid JSON object.
    - The JSON object must have one key: "explanation".
    - The value of the "explanation" key should be the text of the explanation.

    [EXAMPLE OUTPUT]:
    {{
        "explanation": "This design follows key Vastu principles by placing the Kitchen in the Southeast to honor the fire element and the Master Bedroom in the Southwest for stability."
    }}
    """
    
    try:
        # We explicitly tell the API to expect a JSON object.
        response_str = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": explanation_prompt}
            ],
            response_format={"type": "json_object"}
        ).choices[0].message.content
        
        # Parse the simple JSON response
        response_data = json.loads(response_str)
        
        # Extract the explanation text from the JSON
        explanation = response_data.get("explanation", "Explanation could not be retrieved from AI response.")
        
        return explanation.strip()

    except Exception as e:
        print(f"Error during explanation generation: {e}")
        return "Could not generate Vastu explanation."


def prompt2json(prompt: str, client, model="llama3:instruct") -> (str, dict, str):
    """
    Converts a user's prompt into a Vastu-compliant JSON and then generates an explanation.
    This uses a reliable two-step process with correct API handling.
    """
    print(f"Fetching Vastu context for prompt: '{prompt}'")
    vastu_rules_context = get_vastu_context(prompt)

    # --- STEP 1: Generate the Floor Plan ---
    
    systemPrompt = f"""
        You are an AI architectural assistant specializing in Vastu Shastra. Your task is to convert a house description into a structured JSON that strictly follows Vastu principles.

        [CRITICAL VASTU SHASTRA RULES - YOU MUST FOLLOW THESE]:
        {vastu_rules_context}

        [ALLOWED ROOM TYPES]:
        You MUST use ONLY the following strings for the 'type' field: "LivingRoom", "Bedroom", "Kitchen", "Bathroom", "DiningRoom", "Storage", "CommonRoom", "Balcony".

        [INSTRUCTIONS]:
        - Your output MUST be ONLY a valid JSON object with a single root key "rooms".
        - Strictly apply the Vastu rules from the context. They are your highest priority.
        - If the user asks for an unsupported room type (e.g., 'Office'), use the type "CommonRoom" and set the 'name' field to what the user requested.
        - Do not include any other text, explanations, or markdown.
        
        [EXAMPLE OUTPUT FORMAT]:
        {{
            "rooms": [
                {{
                    "name": "Kitchen",
                    "type": "Kitchen",
                    "description": "The kitchen area",
                    "link": [],
                    "location": "southeast",
                    "size": "M"
                }}
            ]
        }}
    """
    
    print("\n--- Generating Floor Plan JSON... ---")
    try:
        structured_data_str = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        ).choices[0].message.content
        
        structured_data = json.loads(structured_data_str)
        
        if not structured_data or "rooms" not in structured_data:
            raise ValueError("LLM response is missing the 'rooms' key.")

    except (json.JSONDecodeError, ValueError, AttributeError) as e:
        print(f"\n\nFATAL ERROR: Could not get a valid floor plan from the LLM. Error: {e}")
        return "{}", {}, "Failed to generate floor plan. Please check the prompt or model."

    # --- If Step 1 was successful, proceed to Step 2 ---
    explanation = get_explanation_from_plan(json.dumps(structured_data, indent=2), client, model)

    json_string = convert_json_string(json.dumps(structured_data))
    
    return json_string, structured_data, explanation

def updatePrompt(original_json_str, new_description, client=client, model="llama3:instruct"):
    # Call the function to update the JSON with the new description
    updated_json = update_floor_plan_with_new_description(original_json_str, new_description, client=client, model=model)

    json_string = convert_json_string(updated_json)

    return json_string, updated_json