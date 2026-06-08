import os
from dotenv import load_dotenv

# Load local .env file
load_dotenv()

apikey = os.environ.get('WATSONX_APIKEY', '')
project_id = os.environ.get('WATSONX_PROJECT_ID', '')
url = os.environ.get('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')

print("=== Watsonx Configuration ===")
print(f"URL: {url}")
print(f"API Key: {'Configured' if apikey else 'Not Found'}")
print(f"Project ID: {'Configured' if project_id else 'Not Found'}")
print("=============================\n")

if not apikey or not project_id:
    print("Error: Missing credentials in your .env file.")
    print("Please create a .env file with WATSONX_APIKEY, WATSONX_PROJECT_ID, and WATSONX_URL.")
    exit(1)

try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    
    print("Initializing ModelInference...")
    credentials = Credentials(url=url, api_key=apikey)
    model = ModelInference(
        model_id="meta-llama/llama-3-3-70b-instruct",
        credentials=credentials,
        project_id=project_id
    )
    
    print("Sending test query to ibm/granite-3-8b-instruct...")
    response = model.chat(messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Say 'Watsonx integration is successful!'"}
    ])
    
    reply = response['choices'][0]['message']['content']
    print("\n=== Response ===")
    print(reply.strip())
    print("================")
    print("\nTest passed successfully!")
except ImportError:
    print("Error: ibm-watsonx-ai SDK is not installed.")
    print("Please run: pip install -r requirements.txt")
except Exception as e:
    print(f"\nError: {e}")
    exit(1)
