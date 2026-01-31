# LangGraph Comprehensive Tutorial Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Tutorial Walkthrough](#tutorial-walkthrough)
4. [Examples Explained](#examples-explained)
5. [Best Practices](#best-practices)

---

## Introduction

This guide accompanies the `langgraph_tutorial.ipynb` notebook and provides detailed explanations of LangGraph concepts and patterns.

### What is LangGraph?

LangGraph is a framework for building **stateful, multi-actor applications** with Large Language Models (LLMs). It enables you to create complex agentic workflows where:
- LLMs make decisions about which tools to use
- State persists across multiple interactions
- Workflows can have cycles and conditional routing

### When to Use LangGraph

✅ **Good Use Cases**:
- Multi-step workflows requiring tool calls
- Agents that need to make decisions
- Applications requiring conversation history
- Complex routing logic based on LLM outputs

❌ **Not Ideal For**:
- Simple single LLM calls
- Static, predetermined workflows
- Applications without tool use

---

## Core Concepts

### 1. State Management

**What is State?**

State is a typed dictionary that flows through your graph, containing all the data nodes need to process.

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
```

**Key Points**:
- `TypedDict`: Provides type hints for better development experience
- `Annotated`: Defines how state updates are merged
- `operator.add`: Appends new messages instead of replacing

**Why This Matters**:
- Enables conversation history
- Supports multi-turn interactions
- Allows context-aware responses

### 2. Nodes

**What are Nodes?**

Nodes are functions that process state. Each node:
1. Receives current state as input
2. Performs some operation (LLM call, tool execution, etc.)
3. Returns updates to merge into state

**Example Node**:
```python
def call_llm(state: AgentState) -> dict:
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}  # Merged with operator.add
```

**Node Types in Our Tutorial**:
- **Agent Node**: Calls the LLM with conversation history
- **Tool Node**: Executes tools requested by the LLM
- **Router Node**: Decides next step based on state

### 3. Edges

**What are Edges?**

Edges define connections between nodes, creating the workflow.

**Types of Edges**:

1. **Normal Edges**: Fixed connections
   ```python
   workflow.add_edge(START, "agent")
   workflow.add_edge("tools", "agent")
   ```

2. **Conditional Edges**: Dynamic routing based on function output
   ```python
   workflow.add_conditional_edges(
       "agent",
       should_continue,  # Router function
       {
           "tools": "tools",  # If "tools" returned
           "end": END,        # If "end" returned
       }
   )
   ```

### 4. Tools

**What are Tools?**

Tools are functions the LLM can call to perform specific tasks.

**Tool Anatomy**:
```python
@tool
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    \"\"\"
    Convert currency from one type to another.
    
    Args:
        amount: The amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
    
    Returns:
        A string with the conversion result
    \"\"\"
    # Implementation
    return result
```

**Key Elements**:
- `@tool` decorator: Marks function as a tool
- **Type annotations**: Required for LLM to understand parameters
- **Docstring**: Helps LLM decide when to use the tool
- **Return string**: LLM consumes the result

### 5. Graph Compilation

**Creating the Workflow**:

```python
# 1. Create graph with state schema
workflow = StateGraph(AgentState)

# 2. Add nodes
workflow.add_node("agent", call_llm)
workflow.add_node("tools", tool_node)

# 3. Add edges
workflow.add_edge(START, "agent")
workflow.add_edge("tools", "agent")

# 4. Add conditional edges
workflow.add_conditional_edges("agent", should_continue, {...})

# 5. Compile
app = workflow.compile()
```

---

## Tutorial Walkthrough

### Part 1: Tool Definition (Cells 1-5)

**Purpose**: Create reusable functions for the agent

**Tools Created**:
1. **Currency Converter**: Converts between USD, EUR, GBP, INR, JPY
2. **EMI Calculator**: Calculates loan monthly payments

**Learning Points**:
- Tool docstrings guide LLM decision-making
- Type annotations define expected inputs
- Return strings for LLM consumption

### Part 2: Environment Setup (Cells 6-11)

**Purpose**: Configure authentication and import libraries

**Key Change**: Using `ChatGoogleGenerativeAI` instead of deprecated `ChatVertexAI`

**Requirements**:
- `GOOGLE_API_KEY` environment variable
- Get key from https://aistudio.google.com/apikey

### Part 3: State Definition (Cell 18)

**Purpose**: Define data structure for the graph

**AgentState Components**:
- `messages`: Conversation history
- `Annotated[..., operator.add]`: Append don't replace

### Part 4: LLM Initialization (Cell 19)

**Purpose**: Set up the language model with tools

**Configuration**:
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0  # Deterministic
)
llm_with_tools = llm.bind_tools(tools)
```

### Part 5: Node Functions (Cells 20-21)

**Agent Node**: Calls LLM with conversation history
**Router Node**: Decides if tools are needed or workflow is complete

### Part 6: Graph Construction (Cell 22)

**Graph Architecture**:
```
START → agent → should_continue
                     ↓
                ┌────┴────┐
                │         │
             tools       END
                │
                └→ agent
```

**Key Features**:
- **Cycle**: tools → agent enables multi-step workflows
- **Conditional routing**: Dynamic path selection
- **Entry point**: START → agent

---

## Examples Explained

### Example 1: Simple Currency Conversion

**Query**: "Convert 1000 USD to EUR"

**Flow**:
1. START → agent (LLM receives query)
2. agent → tools (calls currency_converter)
3. tools → agent (receives result)
4. agent → END (responds to user)

**Total Steps**: 4
**Tool Calls**: 1

**Key Learning**: Single tool use case

---

### Example 2: EMI Calculation

**Query**: "Calculate EMI for 500,000 rupees at 8.5% for 5 years"

**What to Observe**:
- LLM extracts parameters from natural language
- Converts "5 years" → "60 months"
- Formats response with details

**Key Learning**: Parameter extraction from natural language

---

### Example 3: Multi-Step Sequential Workflow ⛓️

**Query**: "Convert 100,000 INR to USD and then calculate EMI for that amount"

**Task Dependency**: Second task DEPENDS on first task's result

**Flow**:
1. agent → tools (currency_converter)
2. tools → agent (receives 1,203.08 USD)
3. agent → tools (emi_calculator with 1,203.08)
4. tools → agent (receives EMI calculation)
5. agent → END

**Total Steps**: 5
**Tool Calls**: 2 (sequential)

**Why Sequential**: The EMI calculation needs the conversion result

**Key Learning**: Dependent tasks must execute in order

---

### Example 4: Conversational Context 💬

**Query 1**: "Convert 5000 GBP to INR"
**Query 2**: "Now calculate EMI for that INR amount at 9% for 2 years"

**What's Special**:
- Query 2 references "that INR amount" from Query 1
- State persists between invocations
- Agent maintains context

**Flow**:
```python
# Turn 1
state = {"messages": [HumanMessage(...)]}
result = app.invoke(state)

# Turn 2 - reuse state
result["messages"].append(HumanMessage(...))
result = app.invoke(result)  # Has full history
```

**Key Learning**: State management enables context-aware conversations

---

### Example 5: Parallel Tool Execution ⚡

**Query**: "Convert INR 500,000 to USD and also compute EMI at 8.5% for 24 months on 500,000"

**Task Independence**: Both tasks are INDEPENDENT

**Flow**:
1. agent → tools (calls BOTH tools simultaneously)
   - currency_converter
   - emi_calculator
2. tools → agent (receives both results)
3. agent → END

**Total Steps**: 3
**Tool Calls**: 2 (parallel)

**Why Parallel**: Tasks don't depend on each other

**LLM Intelligence**:
```python
# Single LLM response with multiple tool_calls
{
  "tool_calls": [
    {"name": "currency_converter", "args": {...}},
    {"name": "emi_calculator", "args": {...}}
  ]
}
```

**Key Learning**: LLM automatically decides parallel vs sequential based on dependencies

---

## Comparison: Sequential vs Parallel

| Aspect | Sequential (Example 3) | Parallel (Example 5) |
|--------|------------------------|----------------------|
| **Query** | "Convert THEN calculate for THAT amount" | "Convert AND ALSO calculate" |
| **Dependency** | Second depends on first | Independent tasks |
| **Agent Calls** | Multiple (≥2) | Single |
| **Tool Calls** | Multiple rounds | Single round |
| **Efficiency** | Slower | Faster |
| **Use Case** | Dependent workflows | Independent tasks |

**How LLM Decides**:
- Analyzes query for dependency keywords ("then", "for that")
- Checks if task parameters depend on previous results
- Makes intelligent decision automatically

---

## Best Practices

### 1. Tool Design

✅ **Do**:
- Write clear, descriptive docstrings
- Use type annotations
- Return strings for LLM consumption
- Handle errors gracefully
- Validate inputs

❌ **Don't**:
- Assume LLM will call correctly
- Return complex objects
- Have side effects without documentation
- Create tools that are too general

### 2. State Management

✅ **Do**:
- Use `operator.add` for lists
- Keep state minimal
- Use TypedDict for type safety

❌ **Don't**:
- Store large objects in state
- Mutate state directly
- Include unnecessary data

### 3. Graph Design

✅ **Do**:
- Add cycles for multi-step workflows
- Use conditional routing for flexibility
- Visualize your graph
- Test edge cases

❌ **Don't**:
- Create infinite loops
- Over-complicate routing
- Forget entry/exit points

### 4. Prompt Engineering

✅ **Do**:
- Be clear about task dependencies
- Use "and also" for parallel tasks
- Use "then" or "for that" for sequential
- Provide all necessary parameters

❌ **Don't**:
- Be ambiguous about dependencies
- Mix dependent and independent phrasing
- Assume LLM knows context without state

---

## Advanced Topics

### 1. Error Handling

Add error handling in tools:
```python
@tool
def safe_tool(param: str) -> str:
    try:
        # Tool logic
        return result
    except Exception as e:
        return f"Error: {str(e)}"
```

### 2. Limiting Iterations

Prevent infinite loops:
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    iteration_count: int

def should_continue(state: AgentState) -> str:
    if state["iteration_count"] > 10:
        return "end"
    # ... rest of logic
```

### 3. Human-in-the-Loop

Add approval steps:
```python
def human_approval(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls"):
        # Present to human for approval
        approved = get_human_approval(last_message.tool_calls)
        if not approved:
            return {"messages": [HumanMessage("Request denied")]}
    return {}
```

### 4. Persistence

Save conversation history:
```python
import pickle

# Save state
with open("conversation.pkl", "wb") as f:
    pickle.dump(result, f)

# Load state
with open("conversation.pkl", "rb") as f:
    state = pickle.load(f)
    result = app.invoke(state)
```

---

## Troubleshooting

### Issue: LLM doesn't call tools

**Possible Causes**:
- Tool docstring unclear
- Query too vague
- Temperature too high (use 0 for deterministic)

**Solution**:
- Improve tool descriptions
- Be specific in queries
- Lower temperature

### Issue: Infinite loop

**Possible Causes**:
- Router always returns "tools"
- Tool output doesn't satisfy LLM

**Solution**:
- Add iteration limit
- Check tool return formats
- Verify router logic

### Issue: Wrong tool called

**Possible Causes**:
- Similar tool descriptions
- Ambiguous query

**Solution**:
- Make tool descriptions distinct
- Clarify query phrasing
- Add examples in docstrings

---

## Next Steps

1. **Experiment**: Try different query phrasings
2. **Add Tools**: Create tools for your domain
3. **Customize State**: Add fields for your use case
4. **Add Routing**: Implement custom routing logic
5. **Deploy**: Turn into API or chat interface

---

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/)
- [Google AI Studio](https://aistudio.google.com/)
- [Original Notebook](./langgraph_tutorial.ipynb)

---

## Summary

**Key Takeaways**:

1. **LangGraph** enables complex agentic workflows with state management
2. **Tools** are functions the LLM can call, defined with `@tool` decorator
3. **State** persists across nodes, enabling conversation history
4. **Nodes** are processing functions, **Edges** define workflow
5. **Parallel vs Sequential**: LLM intelligently decides based on task dependencies
6. **Conditional Routing**: Dynamic path selection based on LLM outputs
7. **Cycles**: Enable multi-step workflows that loop back

**Pattern Recognition**:
- "Convert X THEN use THAT" → Sequential
- "Convert X AND ALSO calculate Y" → Parallel
- "that amount", "for that" → References previous context

Happy building! 🚀

