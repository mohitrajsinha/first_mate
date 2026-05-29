# agent.py — Gemini-powered First Mate agent

import os
from tools import TOOL_DEFINITIONS, SYSTEM_PROMPT, execute_tool
from dotenv import load_dotenv
load_dotenv()

MODELS = {
    "gemini":     "gemini-2.5-flash",
    "gemini-pro": "gemini-3.5-flash",
}

def run_agent(user_message: str, model: str = "gemini"):
    from google import genai
    from google.genai import types

    model_id = MODELS.get(model)
    if not model_id:
        print(f"❌ Unknown model '{model}'. Choose: {', '.join(MODELS.keys())}")
        return

    print(f"\n🤖 First Mate ({model} / {model_id})\n")

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
            if response.text:
                print(response.text)
            break

        # Append model turn
        model_parts = []
        for fn in fn_calls:
            model_parts.append({"function_call": {"name": fn.name, "args": dict(fn.args or {})}})
        contents.append({"role": "model", "parts": model_parts})

        # Execute tools and append results
        result_parts = []
        for fn in fn_calls:
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