# 🎬 Recording Script: LangGraph Tutorial - Notebook 4
## Single Tool Execution

**Total Duration:** ~18-22 minutes  
**Notebook File:** `04_langgraph_single_tool_execution.ipynb`

---

## 📋 PRE-RECORDING CHECKLIST

- [ ] Jupyter Notebook open with fresh kernel
- [ ] All previous outputs cleared
- [ ] Completed Notebooks 1-3 (for context)
- [ ] This markdown script on Screen 1 (reference)
- [ ] Jupyter Notebook on Screen 2 (recording)
- [ ] Microphone tested and ready
- [ ] Screen recording software running
- [ ] .env file configured properly
- [ ] **Extra time allocated** - This is a detailed, educational deep-dive

---

## 🎬 SECTION 1: INTRODUCTION (0:00 - 1:00)

### 📺 SCREEN ACTION
- Show notebook title and objective cells

### 🎙️ NARRATION
"Welcome to Notebook 4 - this is where we open the hood and see exactly how the agent works under the surface.

In Notebook 3, we built a working agentic workflow. We saw it execute successfully. But what actually happened during that execution? How did the agent decide to use a tool? How did state evolve? What messages were created at each step?

Today, we're going to trace through a complete execution flow in microscopic detail. We'll see every message, every state transition, every routing decision. By the end of this video, you'll understand the complete lifecycle of an agent-tool interaction.

This is like watching The Matrix - you're about to see the code behind the intelligence.

We'll start with a simple currency conversion query. Then we'll execute it. And then - here's the exciting part - we'll rewind and walk through every single step that happened behind the scenes. Every API call to Gemini. Every state update. Every routing decision.

This deep understanding is crucial for debugging agents, optimizing performance, and building more sophisticated workflows.

Let's dive in!"

### ⏸️ PAUSE
2 seconds

---

## 🔧 SECTION 2: SETUP - REBUILD GRAPH (1:00 - 3:00)

### 📺 SCREEN ACTION
- Scroll to Setup section

### 🎙️ NARRATION
"First, we need to rebuild our graph from Notebook 3. I'll run through this quickly since we've already covered it in detail.

Let me start with imports and environment setup."

### 💻 CODE TO COPY-PASTE (Cell 1)
```python
# Core imports
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI

import os
from dotenv import load_dotenv
from typing import Literal

load_dotenv("../.env")
print("✅ Environment loaded")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### ✅ EXPECTED OUTPUT
```
✅ Environment loaded
```

### 🎙️ NARRATION (After Output)
"Good! Now let me define our two tools quickly."

### 💻 CODE TO COPY-PASTE (Cell 2)
```python
# Define tools
@tool
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert currency from one type to another.
    
    Args:
        amount: The amount to convert
        from_currency: Source currency code (USD, EUR, GBP, INR, JPY)
        to_currency: Target currency code (USD, EUR, GBP, INR, JPY)
    """
    exchange_rates = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.12, "JPY": 149.50}
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if from_currency not in exchange_rates or to_currency not in exchange_rates:
        return f"Error: Unsupported currency"
    
    amount_in_usd = amount / exchange_rates[from_currency]
    converted_amount = amount_in_usd * exchange_rates[to_currency]
    effective_rate = exchange_rates[to_currency] / exchange_rates[from_currency]
    
    return (
        f"Conversion Result:\n"
        f"  {amount:,.2f} {from_currency} = {converted_amount:,.2f} {to_currency}\n"
        f"  Exchange Rate: 1 {from_currency} = {effective_rate:.4f} {to_currency}"
    )

@tool
def emi_calculator(principal: float, annual_interest_rate: float, tenure_months: int, currency: str) -> str:
    """
    Calculate the EMI (Equated Monthly Installment) for a loan.
    
    Args:
        principal: The loan amount
        annual_interest_rate: Annual interest rate as percentage
        tenure_months: Loan tenure in months
        currency: Currency code for display
    """
    if principal <= 0 or annual_interest_rate < 0 or tenure_months <= 0:
        return "Error: Invalid input parameters"
    
    monthly_interest_rate = annual_interest_rate / 12 / 100
    
    if monthly_interest_rate == 0:
        emi = principal / tenure_months
        total_payment = principal
        total_interest = 0
    else:
        emi = principal * monthly_interest_rate * \
              pow(1 + monthly_interest_rate, tenure_months) / \
              (pow(1 + monthly_interest_rate, tenure_months) - 1)
        total_payment = emi * tenure_months
        total_interest = total_payment - principal
    
    return (
        f"EMI Calculation Result:\n"
        f"  Loan Amount: {principal:,.2f} {currency}\n"
        f"  Interest Rate: {annual_interest_rate}% per annum\n"
        f"  Tenure: {tenure_months} months\n"
        f"  Monthly EMI: {emi:,.2f} {currency}\n"
        f"  Total Payment: {total_payment:,.2f} {currency}\n"
        f"  Total Interest: {total_interest:,.2f} {currency}"
    )

print("✅ Tools defined")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### ✅ EXPECTED OUTPUT
```
✅ Tools defined
```

### 🎙️ NARRATION
"Tools ready. Now let me initialize the LLM and build the graph."

### 💻 CODE TO COPY-PASTE (Cell 3)
```python
# Initialize LLM with tools
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0.3,
    max_tokens=1024,
    project=os.getenv("GOOGLE_PROJECT_ID"),
    location=os.getenv("GOOGLE_REGION")
)

tools = [currency_converter, emi_calculator]
llm_with_tools = llm.bind_tools(tools)

print("✅ LLM initialized with tools")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### ✅ EXPECTED OUTPUT
```
✅ LLM initialized with tools
```

### 🎙️ NARRATION
"And finally, the graph."

### 💻 CODE TO COPY-PASTE (Cell 4)
```python
# Build graph
def call_llm(state: MessagesState):
    """Agent node that invokes the LLM"""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: MessagesState) -> Literal["tools", END]:
    """Router that decides next step"""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_llm)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

app = workflow.compile()
print("✅ Graph compiled")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### ✅ EXPECTED OUTPUT
```
✅ Graph compiled
```

### 🎙️ NARRATION (After Output)
"Perfect! We have our complete graph ready. Same structure we built in Notebook 3. Now let's execute it and then examine what happens."

---

## 🚀 SECTION 3: EXECUTE SINGLE TOOL CALL (3:00 - 5:00)

### 📺 SCREEN ACTION
- Scroll to "Example: Single Tool Call" section

### 🎙️ NARRATION
"Now we're going to execute a simple query: 'What is 1000 USD in EUR?'

This is a straightforward currency conversion. The agent should use the currency_converter tool and give us an answer.

Let me create the initial state."

### 💻 CODE TO COPY-PASTE (Cell 1)
```python
# Create initial state
state = {"messages": [HumanMessage(content="What is 1000 USD in EUR?")]}

print("Query: What is 1000 USD in EUR?")
print("=" * 70)
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### ✅ EXPECTED OUTPUT
```
Query: What is 1000 USD in EUR?
======================================================================
```

### 🎙️ NARRATION
"Now let's execute the graph. Watch what happens."

### 💻 CODE TO COPY-PASTE (Cell 2)
```python
# Execute the graph
result = app.invoke(state)

print("\n✅ Execution complete")
print(f"Total messages in conversation: {len(result['messages'])}")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)
3. Wait for execution (3-5 seconds)

### ✅ EXPECTED OUTPUT
```
✅ Execution complete
Total messages in conversation: 4
```

### 🎙️ NARRATION (After Output)
"Interesting! We started with 1 message - the user's question. Now we have 4 messages total.

That means 3 new messages were created during execution. What are they? Let's inspect the message flow to find out."

---

## 🔍 SECTION 4: INSPECT MESSAGE FLOW (5:00 - 7:30)

### 📺 SCREEN ACTION
- Scroll to "Inspect Message Flow" section

### 🎙️ NARRATION
"Let's look at each message to understand what happened."

### 💻 CODE TO COPY-PASTE
```python
print("CONVERSATION FLOW:")
print("=" * 70)

for i, msg in enumerate(result["messages"], 1):
    if isinstance(msg, HumanMessage):
        print(f"\n[{i}] 👤 USER:")
        print(f"    {msg.content}")
        
    elif isinstance(msg, AIMessage):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"\n[{i}] 🤖 AGENT (calling tools):")
            for tc in msg.tool_calls:
                print(f"    → Tool: {tc['name']}")
                print(f"      Args: {tc['args']}")
        else:
            print(f"\n[{i}] 🤖 AGENT (final response):")
            print(f"    {msg.content}")
            
    elif isinstance(msg, ToolMessage):
        print(f"\n[{i}] 🔧 TOOL RESULT:")
        print(f"    {msg.content}")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### ✅ EXPECTED OUTPUT
```
CONVERSATION FLOW:
======================================================================

[1] 👤 USER:
    What is 1000 USD in EUR?

[2] 🤖 AGENT (calling tools):
    → Tool: currency_converter
      Args: {'amount': 1000, 'from_currency': 'USD', 'to_currency': 'EUR'}

[3] 🔧 TOOL RESULT:
    Conversion Result:
      1,000.00 USD = 920.00 EUR
      Exchange Rate: 1 USD = 0.9200 EUR

[4] 🤖 AGENT (final response):
    1000 USD is equal to 920 EUR.
```

### 🎙️ NARRATION (After Output)
"Excellent! Now we can see the complete conversation flow:

Message 1: The user's question - our HumanMessage.

Message 2: The agent's first decision - an AIMessage that says 'call the currency_converter tool with these arguments'. Notice it has the tool name and extracted parameters.

Message 3: The tool's result - a ToolMessage containing the conversion calculation.

Message 4: The agent's final response - another AIMessage, but this time with natural language content instead of tool calls.

This is the basic pattern: User question, Agent tool decision, Tool result, Agent final answer.

Let me show you the message types more clearly."

---

## 📊 SECTION 5: MESSAGE TYPE ANALYSIS (7:30 - 8:30)

### 📺 SCREEN ACTION
- Scroll to "Message Type Analysis" section

### 💻 CODE TO COPY-PASTE
```python
print("MESSAGE TYPES:")
print("=" * 70)

for i, msg in enumerate(result["messages"], 1):
    msg_type = type(msg).__name__
    print(f"[{i}] {msg_type}")

print("\n" + "=" * 70)
print("PATTERN OBSERVED:")
print("=" * 70)
print("1. HumanMessage    → User's question")
print("2. AIMessage       → Agent decides to call tool")
print("3. ToolMessage     → Tool execution result")
print("4. AIMessage       → Agent's final response")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### ✅ EXPECTED OUTPUT
```
MESSAGE TYPES:
======================================================================
[1] HumanMessage
[2] AIMessage
[3] ToolMessage
[4] AIMessage

======================================================================
PATTERN OBSERVED:
======================================================================
1. HumanMessage    → User's question
2. AIMessage       → Agent decides to call tool
3. ToolMessage     → Tool execution result
4. AIMessage       → Agent's final response
```

### 🎙️ NARRATION (After Output)
"Notice the pattern: HumanMessage, AIMessage, ToolMessage, AIMessage.

This is the signature of single tool execution. And notice there are TWO AIMessages - one for the tool decision, and one for the final response. That means the LLM was called twice during this execution.

Let me extract the final response to show you what the user actually sees."

---

## 💬 SECTION 6: EXTRACT FINAL RESPONSE (8:30 - 9:00)

### 📺 SCREEN ACTION
- Scroll to "Extract Final Response" section

### 💻 CODE TO COPY-PASTE
```python
final_response = result["messages"][-1].content

print("FINAL RESPONSE TO USER:")
print("=" * 70)
print(final_response)
print("=" * 70)
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### ✅ EXPECTED OUTPUT
```
FINAL RESPONSE TO USER:
======================================================================
1000 USD is equal to 920 EUR.
======================================================================
```

### 🎙️ NARRATION (After Output)
"Clean, natural, user-friendly. The agent took the tool result and synthesized it into a natural language response.

Now let me test the other tool quickly with an EMI calculation."

---

## 🧮 SECTION 7: TEST EMI CALCULATOR (9:00 - 10:00)

### 📺 SCREEN ACTION
- Scroll to "Test Another Single Tool Call" section

### 🎙️ NARRATION
"Let me run a second test to verify the pattern holds for the EMI calculator as well."

### 💻 CODE TO COPY-PASTE (Cell 1)
```python
# Create new state
state2 = {
    "messages": [
        HumanMessage(content="Calculate EMI for a 50000 USD loan at 7.5% for 36 months")
    ]
}

print("Query: Calculate EMI for a 50000 USD loan at 7.5% for 36 months")
print("=" * 70)
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### 💻 CODE TO COPY-PASTE (Cell 2)
```python
# Execute
result2 = app.invoke(state2)

# Display flow
print("\nCONVERSATION FLOW:")
print("=" * 70)

for i, msg in enumerate(result2["messages"], 1):
    if isinstance(msg, HumanMessage):
        print(f"\n[{i}] 👤 USER: {msg.content}")
    elif isinstance(msg, AIMessage):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"\n[{i}] 🤖 AGENT: Calling {msg.tool_calls[0]['name']}")
        else:
            print(f"\n[{i}] 🤖 AGENT: {msg.content}")
    elif isinstance(msg, ToolMessage):
        print(f"\n[{i}] 🔧 TOOL: Executed successfully")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)
3. Wait for execution

### ✅ EXPECTED OUTPUT (approximate)
```
CONVERSATION FLOW:
======================================================================

[1] 👤 USER: Calculate EMI for a 50000 USD loan at 7.5% for 36 months

[2] 🤖 AGENT: Calling emi_calculator

[3] 🔧 TOOL: Executed successfully

[4] 🤖 AGENT: (EMI calculation response)
```

### 🎙️ NARRATION (After Output)
"Perfect! Same pattern - 4 messages total. The agent correctly identified it needed the EMI calculator, executed it, and returned a natural response.

Now - here's where it gets really interesting. We've seen what happened on the surface. But what happened behind the scenes? How did these 4 messages get created? What exactly occurred at each step?

Let's rewind and trace through the complete execution flow in detail."

### ⏸️ PAUSE
3 seconds for dramatic effect

---

## 🎯 SECTION 8: DEEP DIVE INTRODUCTION (10:00 - 10:30)

### 📺 SCREEN ACTION
- Scroll to "Deep Dive: What Actually Happened?" section

### 🎙️ NARRATION
"This is the most important part of the entire tutorial series so far. We're going to trace through every single step of execution.

I'm going to walk you through 13 steps - from the moment we call app.invoke to the moment execution completes.

You'll see exactly what gets sent to Gemini, what Gemini returns, how state evolves, how routing decisions are made, everything.

This level of understanding is what separates someone who can use LangGraph from someone who can master it.

Let's begin. We're starting from this point."

### 📺 SCREEN ACTION
- Show the "Execution Timeline" markdown cell

### 🎙️ NARRATION (Reading from screen)
"Our starting point: state equals a dictionary with one message - a HumanMessage with the content 'What is 1000 USD in EUR?'

Then we call app.invoke with that state.

What happens next? Step 1."

---

## 🔬 SECTION 9: DEEP DIVE - STEPS 1-3 (10:30 - 12:00)

### 📺 SCREEN ACTION
- Scroll to "Step 1-2: Graph Starts → Agent Node" section

### 🎙️ NARRATION
"Step 1 and 2: Graph Starts and routes to Agent Node.

When we call app.invoke, LangGraph begins execution at the START node. The graph has a static edge from START to the agent node, so it automatically routes there and calls our call_llm function.

Inside call_llm, here's what happens - look at this code carefully."

### 📺 SCREEN ACTION
- Highlight the code block showing the call_llm function

### 🎙️ NARRATION (Reading from screen)
"response equals llm_with_tools.invoke with state['messages']. This line - this single line - sends an API request to Gemini.

What gets sent? Two things: The messages - which right now is just our one HumanMessage. And the tool schemas - the complete JSON schemas for currency_converter and emi_calculator that were bound to the LLM.

Gemini receives this information and needs to decide what to do.

Let's see what Gemini does in Step 3."

### 📺 SCREEN ACTION
- Scroll to "Step 3: Gemini Analyzes and Responds" section

### 🎙️ NARRATION
"Step 3: Gemini's analysis.

Gemini's thought process - I'm anthropomorphizing here but this is essentially what the model is doing:

One: The user wants currency conversion.
Two: I have a currency_converter tool available.
Three: I need to extract parameters - the amount is 1000, from_currency is USD, to_currency is EUR.
Four: Decision - call this tool.

And here's what Gemini returns - an AIMessage object."

### 📺 SCREEN ACTION
- Show the AIMessage structure in the markdown

### 🎙️ NARRATION (Reading from screen)
"Notice: The content field is empty. Gemini hasn't generated any text yet.

But the tool_calls field has one entry - the tool name is currency_converter, and the args are amount 1000, from_currency USD, to_currency EUR.

This is crucial to understand: The LLM did NOT execute the tool. It just returned instructions for what tool to execute and with what parameters.

The actual tool execution happens next, in the ToolNode. But first, state gets updated and the router makes a decision."

---

## 🔄 SECTION 10: DEEP DIVE - STEPS 4-7 (12:00 - 14:00)

### 📺 SCREEN ACTION
- Scroll to "Step 4-5: State Update → Router Decision" section

### 🎙️ NARRATION
"Steps 4 and 5: State Update and Router Decision.

LangGraph takes the AIMessage that Gemini returned and appends it to state. Now state has two messages: the original HumanMessage and this new AIMessage with tool_calls.

Then the router function executes. Remember our router - should_continue?"

### 📺 SCREEN ACTION
- Show the router code in the markdown

### 🎙️ NARRATION (Reading from screen)
"It gets the last message from state - which is the AIMessage we just added. It checks: does this message have tool_calls? Yes it does! So return 'tools'.

This return value tells LangGraph to route to the tools node.

Now we're at Steps 6 and 7: Tools Node Executes."

### 📺 SCREEN ACTION
- Scroll to "Step 6-7: Tools Node Executes" section

### 🎙️ NARRATION
"The ToolNode - this is LangGraph's built-in component - automatically does two things:

First, it reads the tool_calls from the AIMessage. It sees we need to call currency_converter with these specific arguments.

Second, it actually executes the Python function. It calls currency_converter.invoke with the amount, from_currency, and to_currency.

Our currency_converter function runs, does the calculation, and returns this string."

### 📺 SCREEN ACTION
- Show the conversion result in the markdown

### 🎙️ NARRATION
"'Conversion Result: 1,000 USD equals 920 EUR. Exchange Rate: 1 USD equals 0.92 EUR.'

The ToolNode wraps this result in a ToolMessage object. The ToolMessage has the result content and a tool_call_id that links it back to the AIMessage that requested the tool.

This ToolMessage gets appended to state. Now we have three messages: HumanMessage, AIMessage, ToolMessage.

And here's the key - after the ToolNode executes, there's a static edge back to the agent node. So we loop back."

---

## 🔁 SECTION 11: DEEP DIVE - STEPS 8-11 (14:00 - 16:00)

### 📺 SCREEN ACTION
- Scroll to "Step 8-9: State Update → Loop Back to Agent" section

### 🎙️ NARRATION
"Steps 8 and 9: State Update and Loop Back to Agent.

The graph follows the static edge from tools to agent. We're back at the agent node, which means call_llm executes again.

This is the second LLM call. But this time, Gemini receives a different input."

### 📺 SCREEN ACTION
- Scroll to "Step 10-11: Agent Node (Second Call)" section

### 🎙️ NARRATION
"Step 10 and 11: Agent Node, Second Call.

The agent calls llm_with_tools.invoke again, but now state has three messages: the HumanMessage, the AIMessage with tool_calls, and the ToolMessage with the tool result.

Gemini sees all of this context. Its thought process this time:"

### 📺 SCREEN ACTION
- Show Gemini's thinking in the markdown

### 🎙️ NARRATION (Reading from screen)
"One: The user asked about USD to EUR.
Two: I decided to call currency_converter.
Three: The tool returned the answer - 1000 USD equals 920 EUR.
Four: I have everything I need. Generate a final response for the user.

And Gemini returns a different AIMessage this time."

### 📺 SCREEN ACTION
- Show the second AIMessage structure

### 🎙️ NARRATION (Reading from screen)
"This AIMessage has content: '1000 USD is equal to 920 EUR.'

And critically - tool_calls is empty. No more tools needed.

This AIMessage gets appended to state. We now have four messages total."

---

## 🏁 SECTION 12: DEEP DIVE - STEPS 12-13 (16:00 - 17:00)

### 📺 SCREEN ACTION
- Scroll to "Step 12-13: Final State → Router → END" section

### 🎙️ NARRATION
"Steps 12 and 13: Final State, Router, and END.

The router executes again. It checks the last message - the second AIMessage. Does it have tool_calls? No, tool_calls is an empty list.

So the router returns END.

This tells LangGraph to terminate execution and return the final state.

And that final state is exactly what we saw earlier - four messages: HumanMessage, AIMessage with tool_calls, ToolMessage, AIMessage with content.

This is the complete execution flow. Let me show you this visually."

---

## 📊 SECTION 13: VISUAL EXECUTION FLOW (17:00 - 18:00)

### 📺 SCREEN ACTION
- Scroll to "Visual Execution Flow" section

### 💻 CODE TO COPY-PASTE
```python
print("""
START
  ↓
┌─────────────────────────────────────┐
│ AGENT NODE (First Call)             │
│ • Input: [HumanMessage]             │
│ • LLM decides: Call currency tool   │
│ • Output: AIMessage(tool_calls)     │
└─────────────────────────────────────┘
  ↓
[Router: Has tool_calls? YES → "tools"]
  ↓
┌─────────────────────────────────────┐
│ TOOLS NODE                           │
│ • Executes: currency_converter()    │
│ • Returns: ToolMessage with result  │
└─────────────────────────────────────┘
  ↓
[Edge: tools → agent (loop back)]
  ↓
┌─────────────────────────────────────┐
│ AGENT NODE (Second Call)             │
│ • Input: [Human, AI, Tool]          │
│ • LLM decides: I have the answer    │
│ • Output: AIMessage(content)        │
└─────────────────────────────────────┘
  ↓
[Router: Has tool_calls? NO → END]
  ↓
END
""")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### 🎙️ NARRATION (After Output)
"This is the complete flow visually. Notice the cycle - we start at START, go to agent, then to tools, then loop back to agent, then to END.

Two agent invocations. One tool execution. One routing decision after each agent call.

Let me show you how state evolved through this process."

---

## 📈 SECTION 14: STATE EVOLUTION (18:00 - 19:00)

### 📺 SCREEN ACTION
- Scroll to "State Evolution" section

### 💻 CODE TO COPY-PASTE
```python
print("MESSAGE COUNT TIMELINE:")
print("=" * 70)
print("After Step              | Count | Latest Message")
print("-" * 70)
print("Initial state           |   1   | HumanMessage(query)")
print("Agent #1 (tool decision)|   2   | AIMessage(tool_calls=[...])")
print("Tools execution         |   3   | ToolMessage(result)")
print("Agent #2 (final answer) |   4   | AIMessage(content=answer)")
print("END                     |   4   | (no change)")
print("=" * 70)
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### 🎙️ NARRATION (After Output)
"Look at this timeline. State starts with 1 message. After the first agent call, we have 2. After tools execute, we have 3. After the second agent call, we have 4.

And notice - state never shrinks. Messages only get added, never removed. This is important - the full conversation history is always available to the agent.

This accumulation of messages is what enables context-aware behavior in multi-turn conversations, which we'll see in later notebooks.

Now let me summarize the key observations."

---

## 💡 SECTION 15: KEY OBSERVATIONS (19:00 - 20:30)

### 📺 SCREEN ACTION
- Scroll to "Key Observations" section

### 🎙️ NARRATION
"Let me highlight the critical insights from this deep dive.

First: Two LLM Calls.

The agent calls Gemini twice. First call: decide to use a tool - returns AIMessage with tool_calls. Second call: generate final response - returns AIMessage with content.

This is fundamental to understand. The LLM doesn't execute tools. It just decides what tools to use and extracts parameters.

Second: State Grows, Never Shrinks.

Each node appends messages. The full history is preserved. The final state has 4 messages. This growing state is how we maintain conversation context.

Third: Router Controls Flow.

After the first agent call, tool_calls are present, so we route to tools. After the second agent call, no tool_calls, so we route to END. The router is simple conditional logic.

Fourth: LLM's Autonomy.

The LLM autonomously:
- Identified the correct tool from its docstring
- Extracted parameters from natural language
- Decided when to stop - it knew after seeing the tool result that no more tools were needed
- Generated a natural language response

Fifth: No Hardcoded Logic.

We defined the tools and the graph structure. But the LLM orchestrated the execution. We didn't write any logic that said 'if the query mentions currency, use currency_converter.' The LLM figured that out.

This is the power of agentic AI. The model has agency."

### ⏸️ PAUSE
2 seconds

---

## 🎯 SECTION 16: WRAP-UP (20:30 - 22:00)

### 📺 SCREEN ACTION
- Scroll to the final "Single Tool Execution Complete!" section

### 🎙️ NARRATION
"Let's recap what we learned in this deep dive.

We learned the complete execution flow: START to Agent to Tools to Agent to END. A cycle with two agent invocations.

We learned about the two LLM calls: one to decide on tools, one to generate the final response.

We learned the message types and their sequence: HumanMessage, then AIMessage with tool_calls, then ToolMessage, then AIMessage with content.

We learned how state evolves: starting with 1 message, growing to 4 messages, with each node appending to state.

We learned the router logic: checking for tool_calls to determine whether to route to tools or END.

And most importantly, we learned about LLM autonomy: the model selects tools, extracts parameters, and decides when it's done, all without hardcoded logic.

Let me emphasize the critical insights one more time.

When you call llm_with_tools.invoke, you're sending the messages AND the tool schemas to Gemini. Gemini analyzes and decides.

The LLM returns an AIMessage with tool_calls - it's not executing anything, just providing instructions.

The ToolNode is what actually executes your Python function.

The second LLM call receives the tool result and synthesizes the final response.

There's no hardcoded logic determining tool usage. The LLM orchestrates everything based on the tools schemas and the conversation context.

This understanding is crucial because:

When you're debugging - you'll know which of the two LLM calls is causing issues.

When you're optimizing - you'll understand why you see two API calls for a single user query.

When you're building complex agents - you'll understand how to structure tools so the LLM can reason about them effectively.

In the next notebook, we're going to build on this understanding. We'll look at parallel execution - when the agent calls multiple tools simultaneously. And sequential execution - when one tool's output feeds into another tool.

But the fundamental pattern we learned today - the agent-tool-agent cycle - that stays the same. It just gets more sophisticated.

Make sure you understand this notebook thoroughly before moving forward. Rewatch the deep dive section if needed. This is foundational knowledge.

Thanks for following along through this detailed analysis. See you in the next video where we explore multi-tool orchestration!"

### ⌨️ ACTION
- Save notebook (Ctrl+S or Cmd+S)

---

## 📊 RECORDING SUMMARY

### Total Sections: 16
### Total Duration: ~18-22 minutes
### Code Cells Created: ~12

### Key Checkpoints:
- ✅ Graph rebuilt from Notebook 3
- ✅ Single tool execution completed
- ✅ Message flow inspected (4 messages)
- ✅ Message types identified
- ✅ Second tool test (EMI) verified
- ✅ Deep dive through all 13 steps
- ✅ Visual execution flow displayed
- ✅ State evolution timeline shown
- ✅ Key observations summarized

---

## 🎬 POST-RECORDING CHECKLIST

- [ ] All code cells executed successfully
- [ ] Deep dive section explained clearly
- [ ] Visual diagrams shown and explained
- [ ] Two LLM calls concept emphasized
- [ ] State evolution clearly demonstrated
- [ ] Audio is clear throughout
- [ ] Pacing is appropriate for detail level
- [ ] Notebook saved at the end

---

## 💡 RECORDING TIPS

### Pacing:
- **SLOW DOWN for the deep dive section** - this is complex
- Pause 4-5 seconds after showing state at each step
- Take your time reading the code snippets
- Don't rush through Gemini's "thinking" sections
- Allow processing time after showing the visual flow

### Emphasis Points:
- **CRITICAL**: Two LLM calls, not one
- **CRITICAL**: LLM returns tool_calls, doesn't execute
- **CRITICAL**: ToolNode does the actual execution
- **CRITICAL**: State accumulates, never shrinks
- **HIGHLIGHT**: The agent-tool-agent cycle
- **HIGHLIGHT**: Router checks tool_calls each time
- **HIGHLIGHT**: No hardcoded logic for tool selection

### Voice Modulation:
- Use a "revealing secrets" tone for the deep dive intro
- Slow, methodical pace for step-by-step sections
- Emphasize the "this is key" moments
- Build excitement when showing the visual flow
- Confident, summary tone for key observations

### Common Pitfalls:
- ❌ Don't rush the deep dive - it's the core value
- ❌ Don't skip explaining why there are 2 LLM calls
- ❌ Don't assume viewers understand state mutation
- ✅ DO pause after each step in the deep dive
- ✅ DO explain what Gemini "sees" at each call
- ✅ DO connect back to the 4-message pattern

### Making It Engaging:
- Use "detective" metaphors: "Let's trace through..."
- Create anticipation: "But what happened behind the scenes?"
- Use reveals: "And here's what Gemini returns..."
- Connect steps: "This is why we saw 4 messages earlier..."
- Celebrate understanding: "Now you see how it works!"

### If Something Goes Wrong:
- Execution takes too long: Mention "This API call may take a few seconds"
- Different number of messages: Explain variations in LLM behavior
- Unexpected tool call: Use it as a teaching moment about LLM decision-making
- Error during execution: Show how to debug using message inspection

---

## 📝 KEY CONCEPTS TO EMPHASIZE

### 1. Two LLM Calls Pattern
```
Call 1: User Question → LLM decides → AIMessage(tool_calls)
        ↓
        ToolNode executes
        ↓
Call 2: Tool Result → LLM synthesizes → AIMessage(content)
```

### 2. Message Accumulation
- State: [HumanMessage] → 1 message
- State: [HumanMessage, AIMessage] → 2 messages
- State: [HumanMessage, AIMessage, ToolMessage] → 3 messages
- State: [HumanMessage, AIMessage, ToolMessage, AIMessage] → 4 messages

### 3. What Gets Sent to Gemini

**First Call:**
- Messages: [HumanMessage("What is 1000 USD in EUR?")]
- Tool Schemas: [currency_converter schema, emi_calculator schema]

**Second Call:**
- Messages: [HumanMessage, AIMessage(tool_calls), ToolMessage(result)]
- Tool Schemas: [currency_converter schema, emi_calculator schema]

### 4. Router Decision Logic
```python
if last_message.tool_calls:  # Check if empty list or not
    return "tools"  # → Go to ToolNode
else:
    return END  # → Terminate
```

---

## 🎯 SUCCESS CRITERIA

Your recording is successful if viewers can:
- [ ] Explain why there are TWO LLM calls
- [ ] Describe what happens at each of the 13 steps
- [ ] Understand the difference between AIMessage types (with/without tool_calls)
- [ ] Explain how state evolves from 1 to 4 messages
- [ ] Understand why the LLM doesn't execute tools
- [ ] Recognize the agent-tool-agent cycle pattern
- [ ] Feel confident about debugging agent execution
- [ ] Be excited to learn about parallel/sequential execution

---

## 🔗 TRANSITION TO NEXT NOTEBOOK

**Final statement should set up Notebook 5:**

"Now you understand single tool execution. But what happens when the agent needs to use multiple tools? Can it call them at the same time, or does it need to call them one after another? In the next notebook, we'll explore parallel and sequential execution patterns. You'll see how the agent orchestrates multiple tools to solve complex tasks. That's where things get really powerful!"

---

**Good luck with your recording! This is the most detailed notebook yet. Take your time! 🎥**
