"""Chat agent helper that talks to Azure AI Projects (Assistants) and persists the created
agent id into Key Vault. This module is safe to import (no top-level network calls).

It exposes a single async function: chat_with_agent(user_message, conversation_history=None, conversation_id=None)
which will create/ensure an agent, create or reuse a thread, run the agent, and return the assistant's reply
and the conversation/thread id.
"""

from __future__ import annotations

import os
import asyncio
from typing import List, Dict, Optional

from dotenv import load_dotenv
import logging

try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.keyvault.secrets import SecretClient
except Exception:  # pragma: no cover - allow import-time failures in environments without Azure SDK
    AIProjectClient = None
    DefaultAzureCredential = None
    ClientSecretCredential = None
    SecretClient = None


# Load local .env for development if present
load_dotenv()

# Module logger
logger = logging.getLogger("theglobe.chat")
if not logger.handlers:
    # configure a simple handler if the app hasn't configured logging yet
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s [theglobe.chat] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
# Default to DEBUG locally so we can see message previews; override with THEGLOBE_CHAT_LOG_LEVEL env var
level_name = os.getenv("THEGLOBE_CHAT_LOG_LEVEL", "DEBUG")
try:
    logger.setLevel(level_name)
except Exception:
    logger.setLevel("DEBUG")
# Also add a file handler (helpful for reading logs from this environment)
log_path = os.getenv("THEGLOBE_CHAT_LOG_PATH", "/tmp/theglobe_chat.log")
try:
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception:
    # best effort — don't fail import if file handler can't be created
    logger.debug("Unable to create file handler for %s", log_path)


def _build_credential():
    """Build a credential: prefer client secret if provided, otherwise DefaultAzureCredential."""
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    if client_id and client_secret and tenant_id and ClientSecretCredential is not None:
        return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    if DefaultAzureCredential is not None:
        return DefaultAzureCredential()
    raise RuntimeError("No Azure credential available (azure.identity not installed)")


def _get_kv_client() -> Optional["SecretClient"]:
    kv_endpoint = os.getenv("AZURE_KEY_VAULT_ENDPOINT")
    if not kv_endpoint or SecretClient is None:
        return None
    try:
        return SecretClient(vault_url=kv_endpoint, credential=_build_credential())
    except Exception:
        return None


def _persist_agent_id_to_kv(agent_id: str) -> None:
    kv = _get_kv_client()
    if not kv:
        return
    try:
        kv.set_secret("azure-agent-id", agent_id)
    except Exception:
        # best-effort persistence
        return


def _load_agent_id_from_kv() -> Optional[str]:
    kv = _get_kv_client()
    if not kv:
        return None
    try:
        sec = kv.get_secret("azure-agent-id")
        return sec.value
    except Exception:
        return None


def _create_project_client() -> "AIProjectClient":
    if AIProjectClient is None:
        raise RuntimeError("azure.ai.projects is not available in the environment")

    endpoint = os.getenv("AZURE_AI_ENDPOINT") or os.getenv("PROJECT_ENDPOINT")
    if not endpoint:
        raise RuntimeError("AZURE_AI_ENDPOINT or PROJECT_ENDPOINT must be set")

    # Accept multiple env names for subscription/resource group/project
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID") or os.getenv("SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP_NAME") or os.getenv("RESOURCE_GROUP")
    project_name = os.getenv("AZURE_AI_PROJECT_NAME") or os.getenv("PROJECT_NAME")

    cred = _build_credential()
    logger.debug("Creating AIProjectClient; endpoint=%s project=%s", endpoint, project_name)

    try:
        # Preferred constructor when endpoint already includes projects route
        return AIProjectClient(credential=cred, endpoint=endpoint)
    except TypeError:
        # Older/newer SDK variants sometimes require subscription/resource group/project params
        base_endpoint = endpoint.split("/api/projects/")[0] if "/api/projects/" in endpoint else endpoint
        if not (subscription_id and resource_group and project_name):
            raise RuntimeError(
                "AZURE_SUBSCRIPTION_ID/SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP_NAME/RESOURCE_GROUP, and AZURE_AI_PROJECT_NAME/PROJECT_NAME must be set for AIProjectClient"
            )
        return AIProjectClient(
            credential=cred,
            endpoint=base_endpoint,
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            project_name=project_name,
        )


def _ensure_agent(project: "AIProjectClient") -> str:
    """Return an existing agent id (env or KV) or create a new agent in the project.

    Creating an agent requires AZURE_MODEL to be set (model deployment name).
    """
    agent_id = os.getenv("AZURE_AGENT_ID") or _load_agent_id_from_kv()
    if agent_id:
        try:
            project.agents.get_agent(agent_id)
            logger.info("Using existing agent id from env/KV: %s", agent_id)
            return agent_id
        except Exception:
            # fall through and create
            pass

    model_name = os.getenv("AZURE_MODEL")
    if not model_name:
        raise RuntimeError("AZURE_MODEL (deployment name) is required to create an agent")

    logger.info("Creating new agent using model=%s", model_name)
    agent = project.agents.create_agent(model=model_name, name="The Globe Assistant", instructions="You are The Globe's helpful assistant.")
    _persist_agent_id_to_kv(agent.id)
    logger.info("Created agent id=%s", agent.id)
    return agent.id


def _create_thread_and_post(
    project: "AIProjectClient",
    agent_id: str,
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]],
    conversation_id: Optional[str],
) -> Dict[str, str]:
    # Create or reuse a thread
    logger.info("Posting message to agent_id=%s conversation_id=%s", agent_id, conversation_id)
    if conversation_id:
        try:
            # probe to see if thread exists
            project.agents.messages.create(thread_id=conversation_id, role="user", content="[probe]")
            thread_id = conversation_id
        except Exception:
            thread = project.agents.threads.create()
            thread_id = thread.id
    else:
        thread = project.agents.threads.create()
        thread_id = thread.id
    logger.info("Using thread_id=%s", thread_id)

    # replay recent history (bounded)
    if conversation_history:
        for msg in conversation_history[-10:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if content:
                project.agents.messages.create(thread_id=thread_id, role=role, content=content)

    # post current message
    project.agents.messages.create(thread_id=thread_id, role="user", content=user_message)
    logger.debug("Posted user message to thread %s: %s", thread_id, user_message)

    # create and process run
    run = project.agents.runs.create_and_process(thread_id=thread_id, agent_id=agent_id)
    logger.info("Run created: id=%s status=%s", getattr(run, 'id', None), getattr(run, 'status', None))
    if getattr(run, "status", None) == "failed":
        logger.error("Agent run failed: %s", getattr(run, 'last_error', None))
        raise RuntimeError(f"Agent run failed: {getattr(run, 'last_error', None)}")

    # read messages and return last assistant text (collect into list first)
    messages_iter = project.agents.messages.list(thread_id=thread_id)
    messages = list(messages_iter)

    # Log previews for debugging
    for m in messages:
        try:
            role = getattr(m, "role", "")
            preview = None
            if getattr(m, "text_messages", None):
                preview = m.text_messages[-1].text.value
            elif getattr(m, "content", None):
                preview = m.content
            preview_short = (preview[:200] + "...") if (preview and len(preview) > 200) else preview
            logger.debug("Message role=%s preview=%s", role, preview_short)
        except Exception:
            logger.debug("Failed to preview a message")

    # Find the latest assistant/agent message robustly.
    # Roles may be strings like 'assistant', 'MessageRole.AGENT', etc., so check for substrings.
    def _get_msg_ts(obj) -> Optional[str]:
        # Try common timestamp-like attributes; return string if found for lexicographic compare
        for attr in ("created_on", "created_at", "created", "timestamp", "time", "createdDate", "create_time"):
            val = getattr(obj, attr, None)
            if val is not None:
                try:
                    return str(val)
                except Exception:
                    return None
        return None

    assistant_msgs = []
    for m in messages:
        try:
            role_val = str(getattr(m, "role", "")).lower()
            if ("assistant" in role_val) or ("agent" in role_val):
                assistant_msgs.append(m)
        except Exception:
            continue

    last_text = None
    selection_reason = None
    if assistant_msgs:
        # Prefer timestamp-based selection if timestamps are available
        ts_values = [(m, _get_msg_ts(m)) for m in assistant_msgs]
        if any(ts for (_, ts) in ts_values):
            # pick the message with the max timestamp string (ISO8601 sorts correctly)
            chosen = max(ts_values, key=lambda t: t[1] or "")[0]
            selection_reason = "timestamp"
        else:
            # No timestamps available; try to detect list ordering. Observed SDKs sometimes return
            # newest-first. If the first message appears to be newer (heuristic: compare reprs),
            # prefer the first assistant message; otherwise prefer the last.
            first_role = str(getattr(messages[0], "role", "")).lower() if messages else ""
            if "agent" in first_role or "assistant" in first_role:
                # assume newest-first
                chosen = next((m for m in messages if (("assistant" in str(getattr(m, "role", "")).lower()) or ("agent" in str(getattr(m, "role", "")).lower()))), assistant_msgs[-1])
                selection_reason = "heuristic_newest_first"
            else:
                chosen = assistant_msgs[-1]
                selection_reason = "heuristic_oldest_first"

        # extract text from chosen
        try:
            if getattr(chosen, "text_messages", None):
                last_text = chosen.text_messages[-1].text.value
            elif getattr(chosen, "content", None):
                last_text = chosen.content
        except Exception:
            last_text = None

    logger.info("Fetched %d messages from thread %s", len(messages), thread_id)
    logger.info("Assistant last_text: %s", (last_text or '(no assistant response)'))
    logger.debug("assistant_msgs_count=%d selection_reason=%s", len(assistant_msgs), selection_reason)

    # log conversation_history size
    try:
        hist_len = len(conversation_history) if conversation_history is not None else 0
        logger.debug("conversation_history length=%d", hist_len)
    except Exception:
        logger.debug("conversation_history not iterable")

    return {"response": last_text or "(no assistant response)", "conversation_id": thread_id}


async def chat_with_agent(
    user_message: str, conversation_history: Optional[List[Dict[str, str]]] = None, conversation_id: Optional[str] = None
) -> Dict[str, str]:
    """Async wrapper that runs blocking SDK calls off the event loop."""
    project = _create_project_client()

    def blocking():
        agent_id = _ensure_agent(project)
        return _create_thread_and_post(project, agent_id, user_message, conversation_history, conversation_id)

    return await asyncio.to_thread(blocking)
