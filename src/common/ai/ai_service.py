from langchain_core.prompts import ChatPromptTemplate
import os
import json
from dotenv import load_dotenv
from common.config_loader import load_config
from common.encdec.encdec import EncDecUtil
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

load_dotenv()
config = load_config()

encdec_util = EncDecUtil(os.getenv("enc.secret"))

# Load config-driven values
ai_provider = config['ai'].get('provider', 'openai')  # 'openai' or 'ollama'
default_ai_model = config['ai'].get('model', 'gpt-4')  # openai or ollama model
log_file_path = config['log']['file_path']


# Predefined model routing logic (can be expanded as needed)
def choose_model_by_log_content(log_line):
    lower = log_line.lower()
    if "failed" in lower or "error" in lower or "warn" in lower:
        return "mistral"
    elif "exception" in lower or "traceback" in lower:
        return "wizardcoder"
    elif "function" in lower or "line" in lower:
        return "codellama"

    return "llama3"


# 🧠 System role: who the AI is
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an intelligent log analyzer. Analyse every log statement and create a JSON response to describe it."
    "ONLY return a valid JSON array — no explanation, no markdown."
)

# 👤 User role: logs and instruction
user_prompt = HumanMessagePromptTemplate.from_template("""
Here is a list of log statements. DO NOT MISS any ERROR log statements.
For example, If there are 20 log statements, JSON response must contain 20 objects.

{log_buffer}

Respond strictly in this format:
[
  {{
    "log_type": "...",
    "ai_tag": "...",
    "description": "...",
    "details": {{
      "module": "...",
      "state": "..."
    }}
  }}
]
""")

# 🧱 Combine into full chat prompt template
prompt_template = ChatPromptTemplate.from_messages([system_prompt, user_prompt])

# # Base prompt
# prompt_template = ChatPromptTemplate.from_template("""
# You are an intelligent log analyzer. Here is a list of Error or Warning Log statements.
# ONLY return a valid JSON array — no explanation, no markdown.
#
# Logs:
# {log_buffer}
#
# Respond strictly in this format:
# [
#   {{
#     "log_type": "...",
#     "ai_tag": "...",
#     "description": "...",
#     "details": {{
#       "module": "...",
#       "state": "..."
#     }}
#   }}
# ]
# """)

# def perform_ai_analysis(log_buffer, context_model=None):
#     try:
#         # Dynamically select model for Ollama
#         model_name = context_model or default_ai_model
#         if ai_provider == "ollama":
#             current_llm = ChatOllama(model=model_name, temperature=0.2)
#         else:
#             openai_api_key = config['ai']['openai_api_key']
#             current_llm = ChatOpenAI(openai_api_key=encdec_util.decrypt(openai_api_key), temperature=0.2, model=model_name)
#
#         messages = prompt_template.format_messages(log_buffer=log_buffer)
#         print(f">>>>>>>>>>>>\n AI Model: {model_name}\n <<<<<<<<<<<< ")
#         print(f"\n>>>>>>>>>>>>\n AI Prompt: {messages}\n <<<<<<<<<<<< \n")
#         response = current_llm.invoke(messages)
#         # Diagnose the actual returned object
#         # print(f">>>>>>>>>>>>\n 🔍 type(response) = {type(response)}\n <<<<<<<<<<<< ")
#         # print(f">>>>>>>>>>>>\n 🔍 Response = {response}\n <<<<<<<<<<<< ")
#
#         # print(f">>>>>>>>>>>> AI Response: {response.content} <<<<<<<<<<<< ")
#         ai_response = json.loads(response.content)
#         print(f">>>>>>>>>>>> \n{json.dumps(ai_response, indent=2)}\n <<<<<<<<<<<< ")
#         return ai_response
#     except Exception as e:
#         print(f"❌ AI analysis failed: {e}", e)
#         return None

def perform_ai_analysis(log_lines, context_model=None):
    try:
        model_name = context_model or default_ai_model
        if ai_provider == "ollama":
            current_llm = ChatOllama(model=model_name, temperature=0.2)
        else:
            openai_api_key = config['ai']['openai_api_key']
            current_llm = ChatOpenAI(openai_api_key=encdec_util.decrypt(openai_api_key), temperature=0.2, model=model_name)

        messages = prompt_template.format_messages(log_buffer="\n".join(log_lines))
        print(f"\n\n============================== AI SESSION [{model_name}] ==============================")
        print(">>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> AI Model:")
        print("\n".join(log_lines))
        print("<<<<<<<<<<< <<<<<<<<<<<<< <<<<<<<<<<<< <<<<<<<<<<<<\n")

        print(">>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> AI Model:")
        print(model_name)
        print("<<<<<<<<<<< <<<<<<<<<<<<< <<<<<<<<<<<< <<<<<<<<<<<<\n")

        # print(">>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> AI Prompt:")
        # print(messages)
        # print("<<<<<<<<<<< <<<<<<<<<<<<< <<<<<<<<<<<< <<<<<<<<<<<<\n")

        response = current_llm.invoke(messages)

        raw_content = response.content.strip() if hasattr(response, 'content') else str(response).strip()

        if raw_content.startswith("```json"):
            raw_content = raw_content.replace("```json", "").replace("```", "").strip()

        # print(f">>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> AI Response:")
        # print(raw_content)
        # print(f"<<<<<<<<<<< <<<<<<<<<<<<< <<<<<<<<<<<< <<<<<<<<<<<<\n")

        # ai_response = json.loads(raw_content)
        ai_response = json.loads(raw_content)
        if isinstance(ai_response, list):
            print(f">>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> AI Response contains {len(ai_response)} elements")
            print(json.dumps(ai_response, indent=2))
            print(f"<<<<<<<<<<< <<<<<<<<<<<<< <<<<<<<<<<<< <<<<<<<<<<<<\n")
            print(f"============================== END OF AI SESSION [{model_name}] ==============================\n\n")
            return ai_response
        else:
            # If AI gave a single object instead of array, wrap it
            print(f">>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> >>>>>>>>>>>> AI Response contains {1} elements")
            print(json.dumps(ai_response, indent=2))
            print(f"<<<<<<<<<<< <<<<<<<<<<<<< <<<<<<<<<<<< <<<<<<<<<<<<\n")
            print(f"============================== END OF AI SESSION [{model_name}] ==============================\n\n")
            return [ai_response]
    except Exception as e:
        print(f"❌ AI analysis failed: {e}", e)
        return None


def read_log_file(file_path):
    with open(file_path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            yield line.strip()


if __name__ == "__main__":
    index = 0
    batch_size = 20
    log_buffer = []

    for line in read_log_file(log_file_path):
        log_buffer.append(line)
        index += 1

        if len(log_buffer) >= batch_size:
            ai_model_choice = choose_model_by_log_content("\n".join(log_buffer)) if ai_provider == "ollama" else default_ai_model
            ai_response = perform_ai_analysis(log_buffer, context_model=ai_model_choice)
            log_buffer.clear()

        if index >= 50:  # For test runs, limit to 2 batches
            break

    # Handle any remaining logs in buffer
    if log_buffer:
        ai_model_choice = choose_model_by_log_content("\n".join(log_buffer)) if ai_provider == "ollama" else default_ai_model
        ai_response = perform_ai_analysis(log_buffer, context_model=ai_model_choice)
        log_buffer.clear()
