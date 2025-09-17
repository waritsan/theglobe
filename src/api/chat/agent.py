import os
import json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

# Load environment variables from local.settings.json if not already set
if not os.environ.get('AZURE_AI_ENDPOINT') or not os.environ.get('AZURE_AGENT_ID'):
    settings_path = os.path.join(os.path.dirname(__file__), '..', 'local.settings.json')
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            settings = json.load(f)
            values = settings.get('Values', {})
            if 'AZURE_AI_ENDPOINT' in values and not os.environ.get('AZURE_AI_ENDPOINT'):
                os.environ['AZURE_AI_ENDPOINT'] = values['AZURE_AI_ENDPOINT']
            if 'AZURE_AGENT_ID' in values and not os.environ.get('AZURE_AGENT_ID'):
                os.environ['AZURE_AGENT_ID'] = values['AZURE_AGENT_ID']

endpoint = os.environ.get('AZURE_AI_ENDPOINT')
if not endpoint:
    raise ValueError("AZURE_AI_ENDPOINT environment variable is not set")

agent_id = os.environ.get('AZURE_AGENT_ID')
if not agent_id:
    raise ValueError("AZURE_AGENT_ID environment variable is not set")

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=endpoint)

agent = project.agents.get_agent(agent_id)

thread = project.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

message = project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="คุณเป็นใคร"
)

run = project.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id)

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

    for message in messages:
        if message.text_messages:
            print(f"{message.role}: {message.text_messages[-1].text.value}")