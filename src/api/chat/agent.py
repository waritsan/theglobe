import os
from dotenv import load_dotenv
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import CodeInterpreterTool
# Load environment variables from .env file
load_dotenv()

# Create an AIProjectClient from an endpoint, copied from your Azure AI Foundry project.
# You need to login to Azure subscription via Azure CLI and set the environment variables
project_endpoint = os.environ["PROJECT_ENDPOINT"]  # Ensure the PROJECT_ENDPOINT environment variable is set

# Create an AIProjectClient instance
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),  # Use Azure Default Credential for authentication
    resource_group_name=os.environ,  # Replace with your resource group name
    project_name=os.environ["PROJECT_NAME"],  # Replace with your project name,
    subscription_id=os.environ["SUBSCRIPTION_ID"]  # Replace with your subscription ID
)

code_interpreter = CodeInterpreterTool()
with project_client:
    # Create an agent with the Code Interpreter tool
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],  # Model deployment name
        name="theglobe-agent",  # Name of the agent
        instructions="You politely help with math questions. Use the Code Interpreter tool when asked to visualize numbers.",  # Instructions for the agent
        tools=code_interpreter.definitions,  # Attach the tool
    )
    print(f"Created agent, ID: {agent.id}")

    # Create a thread for communication
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Add a message to the thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",  # Role of the message sender
        content="Hi, Agent!",  # Message content
    )
    print(f"Created message, ID: {message['id']}")

    # Create and process an agent run
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
        additional_instructions="Please address the user as Jane Doe. The user has a premium account",
    )
    print(f"Run finished with status: {run.status}")

    # Check if the run failed
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Fetch and log all messages
    messages = project_client.agents.messages.list(thread_id=thread.id)
    for message in messages:
        print(f"Role: {message.role}, Content: {message.content}")

    # Uncomment these lines to delete the agent when done
    # project_client.agents.delete_agent(agent.id)
    # print("Deleted agent")