from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import json
from dotenv import load_dotenv
from common.config_loader import load_config
from common.encdec.encdec import EncDecUtil

load_dotenv()
encdec_util = EncDecUtil(os.getenv("enc.secret"))

# parser = argparse.ArgumentParser(description="AI-based Test Case Evaluation")
# parser.add_argument("--secret", required=True, help="Secret key for SecureEncryptor")
# args = parser.parse_args()
#
# secure = SecureEncryptor(args.secret)
# openai_api_key = os.getenv("OPENAI_API_KEY") or "your-key"  # fallback from config
config = load_config()
openai_api_key = config['ai']['openai_api_key']
log_file_path = config['log']['file_path']

llm = ChatOpenAI(openai_api_key=encdec_util.decrypt(openai_api_key), temperature=0.2, model="gpt-4")

prompt_template = ChatPromptTemplate.from_template("""
You are an intelligent log analyzer. I'm giving you a list of Log statements for your analysis.
For each log statement, classify its type (INFO, WARN, ERROR, SUCCESS),
Also generate a tag, a summary, and key-value details (like module name, error state, etc).

Log: {log_line}

Respond strictly in JSON format (JSON array). For each log statement, prepare the below JSON and append them to the JSON array. 
No other description or analysis is required which causes unwanted API cost on us.
{{
    "log_type": "...",
    "ai_tag": "...",
    "description": "...",
    "details": {{
        "module": "...",
        "state": "..."
    }}
}}
""")

def perform_openai_analysis(log_line):
    try:
        messages = prompt_template.format_messages(log_line=log_line)
        response = llm.invoke(messages)
        return json.loads(response.content)
    except Exception as e:
        print(f"AI analysis failed: {e}")
        return None


def read_log_file(file_path):
    """Generator that reads a log file line by line."""
    with open(file_path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            yield line.strip()


if __name__ == "__main__":

    index = 0;
    for line in read_log_file(log_file_path):
        print(f" ============================== STARTING OPEN-AI SESSION [{index + 1}]============================== ")
        print(f"Sending Log statement to OpenAI: {line}")
        ai_respone = perform_openai_analysis(line)
        print("OpenAI Log analysis Response:")
        print(json.dumps(ai_respone, indent=2))
        print(f" ============================== END OF OPEN-AI SESSION [{index + 1}] ============================== \n\n")
        index += 1
        if index >= 10:
            break

    # ai_respone = perform_openai_analysis("[Sun Dec 04 04:47:44 2005] [error] mod_jk child workerEnv in error state 6");
    # print("OpenAI Log analysis Response:")
    # print(json.dumps(ai_respone, indent=2))
    # print(f"OpenAI Log analysis Response: {ai_respone}")
