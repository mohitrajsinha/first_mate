# agent.py — Gemini-powered First Mate agent

import os
from tools import TOOL_DEFINITIONS, SYSTEM_PROMPT, execute_tool
from dotenv import load_dotenv
load_dotenv()

MODELS = {
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-3.5-flash": "gemini-3.5-flash",
}


def run_agent(user_message: str, model: str = "gemini-2.5-flash") -> str:
    from google import genai
    from google.genai import types

    model_id = MODELS.get(model)
    if not model_id:
        # Return the error as a string so Streamlit can display it
        return f"❌ Unknown model '{model}'. Choose: {', '.join(MODELS.keys())}"

    # We removed the print(f"\n🤖 First Mate...") here because the Streamlit UI 
    # already has its own headers and we don't want terminal text leaking out.

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    tool_declarations = [
        types.FunctionDeclaration(
            name=t["name"],
            description=t["description"],
            parameters=t["parameters"],
        )
        for t in TOOL_DEFINITIONS
    ]

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[types.Tool(function_declarations=tool_declarations)],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    contents = [{"role": "user", "parts": [{"text": user_message}]}]

    while True:
        response = client.models.generate_content(
            model=model_id,
            contents=contents,  # type: ignore
            config=config,
        )

        fn_calls = response.function_calls

        if not fn_calls:
            # THE CRITICAL CHANGE: Return the text instead of printing it
            if response.text:
                return response.text
            return "No response generated."

        # Append model turn
        model_parts = []
        for fn in fn_calls:
            model_parts.append({"function_call": {"name": fn.name, "args": dict(fn.args or {})}})
        contents.append({"role": "model", "parts": model_parts})

        # Execute tools and append results
        result_parts = []
        for fn in fn_calls:
            # You can leave this print here; it will log to the terminal running Streamlit 
            # for your own debugging, but won't show up in the web UI.
            print(f"  ⚓ [{fn.name}] querying Coral...") 
            result = execute_tool(fn.name, dict(fn.args or {}))
            result_parts.append({
                "function_response": {
                    "id": fn.id,
                    "name": fn.name,
                    "response": {"result": result},
                }
            })
        contents.append({"role": "user", "parts": result_parts})  # type: ignore