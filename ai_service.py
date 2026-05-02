from dotenv import load_dotenv
load_dotenv()
import os

from typing import List, Dict, Any, Optional, AsyncGenerator
import json
from pydantic_ai import Agent, RunContext, ModelRetry
from langfuse import observe, propagate_attributes



from pydantic_ai.messages import ModelMessage, ModelResponse, ModelRequest, TextPart, UserPromptPart

from tools import (
    get_spending_by_category, get_largest_expenses, semantic_search_transactions,
    get_monthly_summary, compare_periods, get_income_by_source,
    detect_anomalies, get_transaction_frequency, get_category_trend,
    get_transactions_by_date_range, get_spending_velocity, get_running_balance,
    get_total_credit_debit, get_spending_by_description, get_recipients,
    get_day_of_week_analysis, get_time_of_month_analysis, get_largest_expense_categories,
    find_similar_transactions, get_merchant_spending, get_top_merchants,
    get_merchant_comparison, detect_recurring_transactions, get_subscription_summary,
    get_upcoming_payments
)

# Enable Langfuse Instrumentation (OTel-based)
Agent.instrument_all()

# Diagnostic check for Langfuse connection
from langfuse import get_client
langfuse_diagnostic = get_client()
if langfuse_diagnostic.auth_check():
    print("DEBUG: Langfuse successfully authenticated!")
else:
    print(f"CRITICAL: Langfuse authentication failed! Check your credentials and HOST: {os.environ.get('LANGFUSE_HOST')}")



# System Prompt
SYSTEM_PROMPT = (
    "You are a helpful personal finance AI assistant. You have access to tools that can query the user's "
    "uploaded bank statements and transactions. If a user asks a question about their spending, use the "
    "provided tools to fetch the data before answering. The currency is Naira (₦). Pay strict attention "
    "to the date requested by the user. If they ask for '2025 and 2026', pass date_prefixes as ['2025', '2026']. "
    "Do not assume or hallucinate a specific month (like '-07') unless the user explicitly asks for it. "
    "IMPORTANT: When searching for 'sender' or 'receiver', note that the transaction descriptions usually "
    "contain phrases like 'FROM [Name]' or 'TO [Name]'. Do not search for the literal word 'sender'; "
    "instead, search for specific names or use 'FROM' / 'TO' keywords in your query to find relevant entries."
)

# Initialize Agent with native OpenRouter support
# Pydantic AI now supports OpenRouter natively. 
# We pass the model directly without needing the openai library.
agent = Agent(
    'openrouter:mistralai/mistral-nemo',
    system_prompt=SYSTEM_PROMPT,
    deps_type=str,
    instrument=True
)


# Register Tools
agent.tool(get_spending_by_category)
agent.tool(get_largest_expenses)
agent.tool(semantic_search_transactions)
agent.tool(get_monthly_summary)
agent.tool(compare_periods)
agent.tool(get_income_by_source)
agent.tool(detect_anomalies)
agent.tool(get_transaction_frequency)
agent.tool(get_category_trend)
agent.tool(get_transactions_by_date_range)
agent.tool(get_spending_velocity)
agent.tool(get_running_balance)
agent.tool(get_total_credit_debit)
agent.tool(get_spending_by_description)
agent.tool(get_recipients)
agent.tool(get_day_of_week_analysis)
agent.tool(get_time_of_month_analysis)
agent.tool(get_largest_expense_categories)
agent.tool(find_similar_transactions)
agent.tool(get_merchant_spending)
agent.tool(get_top_merchants)
agent.tool(get_merchant_comparison)
agent.tool(detect_recurring_transactions)
agent.tool(get_subscription_summary)
agent.tool(get_upcoming_payments)

def _convert_history_to_pydantic_ai(history: List[Dict[str, Any]]) -> List[ModelMessage]:
    """
    Very basic conversion of generic message history to Pydantic AI ModelMessages.
    """
    pydantic_history = []
    
    for msg in history:
        role = msg.get("role")
        content = msg.get("content", "")
        
        if role == "user":
            pydantic_history.append(ModelRequest(parts=[UserPromptPart(content=content)]))
        elif role == "assistant":
            pydantic_history.append(ModelResponse(parts=[TextPart(content=content)]))
            
    return pydantic_history

@observe()
async def chat_with_ai_stream(messages: List[Dict[str, Any]], user_id: str, session_id: Optional[str] = None) -> AsyncGenerator[str, None]:
    """
    Handles a conversation using Pydantic AI and OpenRouter with streaming.
    Yields JSON chunks and finally the updated history.
    """
    if not messages:
        yield json.dumps({"type": "chunk", "content": "No message received."}) + "\n"
        yield json.dumps({"type": "history", "content": messages}) + "\n"
        return
        
    last_message = messages[-1]
    if last_message.get("role") != "user":
         yield json.dumps({"type": "chunk", "content": "Please send a user message."}) + "\n"
         yield json.dumps({"type": "history", "content": messages}) + "\n"
         return
         
    user_prompt = last_message.get("content", "")
    history_messages = messages[:-1]
    
    try:
        msg_history = _convert_history_to_pydantic_ai(history_messages)
        prompt = user_prompt
        
        while True:
            async with agent.run_stream(
                prompt, 
                message_history=msg_history,
                deps=user_id
            ) as result:
                text_streamed = False
                async for chunk in result.stream_text(delta=True):
                    if chunk:
                        yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
                        text_streamed = True
                
                msg_history = result.all_messages()
                
                last_msg = msg_history[-1]
                has_text = False
                if isinstance(last_msg, ModelResponse):
                    for part in last_msg.parts:
                        if hasattr(part, 'content') and isinstance(part, TextPart) and part.content:
                            has_text = True
                            break
                            
                if text_streamed or has_text:
                    break
                prompt = None
            
        # Build back JSON history format
        new_history = []
        for msg in msg_history:
            if isinstance(msg, ModelRequest):
                for part in msg.parts:
                    if hasattr(part, 'content') and isinstance(part, UserPromptPart):
                        new_history.append({"role": "user", "content": part.content})
            elif isinstance(msg, ModelResponse):
                for part in msg.parts:
                    if hasattr(part, 'content') and isinstance(part, TextPart):
                         new_history.append({"role": "assistant", "content": part.content})

        yield json.dumps({"type": "history", "content": new_history}) + "\n"

    except Exception as e:
        yield json.dumps({"type": "chunk", "content": f"Error: {str(e)}"}) + "\n"
        yield json.dumps({"type": "history", "content": messages}) + "\n"


# Backward compatibility
chat_with_granite = chat_with_ai_stream
