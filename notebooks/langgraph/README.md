# LangGraph Tutorial Materials

Welcome to the comprehensive LangGraph tutorial! This directory contains all the materials you need to learn how to build intelligent agentic workflows.

## 📚 Materials Overview

### 1. **langgraph_tutorial.ipynb** - Main Tutorial Notebook
   - **Purpose**: Hands-on, executable tutorial
   - **Content**: Complete working examples with code and outputs
   - **Best For**: Learning by running code
   - **Status**: ✅ Complete with 5 examples

### 2. **LANGGRAPH_TUTORIAL_GUIDE.md** - Comprehensive Guide
   - **Purpose**: Detailed explanations and reference
   - **Content**: Concept deep-dives, best practices, troubleshooting
   - **Best For**: Understanding the "why" behind the code
   - **Status**: ✅ Complete documentation

### 3. **langgraph_comprehensive_tutorial.ipynb** - Extended Tutorial (In Progress)
   - **Purpose**: Even more detailed walkthrough with markdown explanations
   - **Content**: Combines code with extensive documentation
   - **Best For**: Self-paced learning with detailed context
   - **Status**: 🚧 Under development

## 🚀 Quick Start

### Prerequisites

1. **Python Environment**:
   ```bash
   python -m venv cbag-venv
   source cbag-venv/bin/activate  # On Windows: cbag-venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r ../../requirements.txt
   ```

3. **Google API Key**:
   - Get your key from [Google AI Studio](https://aistudio.google.com/apikey)
   - Set environment variable:
     ```bash
     export GOOGLE_API_KEY='your-api-key'
     ```
   - Or add to `.env` file in project root:
     ```
     GOOGLE_API_KEY=your-api-key
     ```

### Running the Tutorial

1. **Start Jupyter**:
   ```bash
   jupyter notebook langgraph_tutorial.ipynb
   ```

2. **Execute Cells**: Run cells sequentially (Shift+Enter)

3. **Observe Outputs**: Watch how the agent makes decisions

## 📖 Learning Path

### Beginner Path (1-2 hours)
1. Read "What is LangGraph?" in the guide
2. Run **Example 1** (Currency Conversion)
3. Run **Example 2** (EMI Calculation)
4. Read "Core Concepts" in the guide

### Intermediate Path (2-3 hours)
1. Complete Beginner Path
2. Run **Example 3** (Sequential Workflow)
3. Run **Example 5** (Parallel Execution)
4. Read "Examples Explained" in the guide
5. Understand the difference between parallel and sequential

### Advanced Path (3-4 hours)
1. Complete Intermediate Path
2. Run **Example 4** (Conversational Context)
3. Read "Advanced Topics" in the guide
4. Try the exercises
5. Create your own tools

## 🎯 Key Concepts You'll Learn

### 1. State Management
- How conversation history is maintained
- Using `TypedDict` and `Annotated` types
- State merging with `operator.add`

### 2. Tool Definition
- Creating functions the LLM can call
- Writing effective docstrings
- Parameter validation

### 3. Graph Construction
- Nodes: Processing units
- Edges: Workflow connections
- Conditional routing

### 4. Execution Patterns
- **Sequential**: Dependent tasks (Example 3)
- **Parallel**: Independent tasks (Example 5)
- **Conversational**: Multi-turn interactions (Example 4)

## 📊 Tutorial Examples

| Example | Query Type | Tools Used | Pattern | Complexity |
|---------|-----------|------------|---------|------------|
| 1 | Single tool | Currency Converter | Simple | ⭐ |
| 2 | Single tool | EMI Calculator | Simple | ⭐ |
| 3 | Multi-step | Both | Sequential | ⭐⭐ |
| 4 | Multi-turn | Both | Conversational | ⭐⭐ |
| 5 | Parallel | Both | Parallel | ⭐⭐⭐ |

## 🔍 Understanding Examples

### Example 3 vs Example 5: The Key Difference

**Example 3** (Sequential):
```
Query: "Convert 100k INR to USD THEN calculate EMI for THAT amount"
Flow:  agent → currency → agent → EMI → agent → END
Steps: 5
Why:   EMI needs the conversion result (dependency)
```

**Example 5** (Parallel):
```
Query: "Convert 500k INR to USD AND ALSO compute EMI for 500k"
Flow:  agent → [currency + EMI in parallel] → agent → END
Steps: 3
Why:   Tasks are independent (no dependency)
```

**The LLM decides automatically** based on task dependencies!

## 💡 Common Use Cases

LangGraph is perfect for:

1. **Customer Support Bots**
   - Check order status
   - Process refunds
   - Update customer info

2. **Data Analysis Agents**
   - Query databases
   - Generate reports
   - Create visualizations

3. **Research Assistants**
   - Search multiple sources
   - Summarize findings
   - Generate citations

4. **Financial Tools**
   - Calculate investments
   - Compare options
   - Generate recommendations

## 🛠️ Tools in This Tutorial

### 1. Currency Converter
- **Purpose**: Convert between currencies
- **Supported**: USD, EUR, GBP, INR, JPY
- **Use Case**: International transactions

### 2. EMI Calculator
- **Purpose**: Calculate loan monthly payments
- **Formula**: EMI = P × r × (1 + r)^n / [(1 + r)^n - 1]
- **Use Case**: Loan planning

## 📝 Exercises

Try these to deepen your understanding:

### Exercise 1: Add a Tool (Beginner)
Create a **compound interest calculator** tool:
```python
@tool
def compound_interest(principal, rate, years, compounds_per_year=12):
    # Your implementation
    pass
```

### Exercise 2: Custom State (Intermediate)
Add a user preferences field to `AgentState`:
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_preferences: dict  # Add this
```

### Exercise 3: Smart Routing (Advanced)
Create a router that limits iterations:
```python
def should_continue(state: AgentState) -> str:
    # Add iteration limit logic
    pass
```

## 🐛 Troubleshooting

### LLM Not Calling Tools?
- Check tool docstrings are clear
- Make query more specific
- Verify temperature is low (0)

### Infinite Loop?
- Add iteration counter to state
- Check router logic
- Verify tool outputs are useful

### Wrong Tool Called?
- Make tool descriptions more distinct
- Clarify your query
- Add parameter examples in docstring

## 📚 Additional Resources

### Documentation
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools Guide](https://python.langchain.com/docs/modules/agents/tools/)
- [Google Generative AI](https://ai.google.dev/)

### Video Tutorials
- [LangChain YouTube Channel](https://www.youtube.com/@LangChain)

### Community
- [LangChain Discord](https://discord.gg/langchain)
- [GitHub Discussions](https://github.com/langchain-ai/langgraph/discussions)

## 🔄 Updates

### January 2026
- ✅ Migrated from deprecated `ChatVertexAI` to `ChatGoogleGenerativeAI`
- ✅ Added Example 5 (Parallel Tool Execution)
- ✅ Created comprehensive guide
- ✅ Added detailed explanations for each example

### Future Additions
- 🚧 Human-in-the-loop examples
- 🚧 Persistence and memory management
- 🚧 Error handling patterns
- 🚧 Deployment guide

## 🤝 Contributing

Found an issue or have a suggestion? Please:
1. Check existing examples
2. Try troubleshooting steps
3. Refer to the comprehensive guide
4. Ask your instructor or create an issue

## 📄 License

This tutorial is part of the AI Cohort educational materials.

---

## Quick Command Reference

```bash
# Activate environment
source cbag-venv/bin/activate

# Set API key
export GOOGLE_API_KEY='your-key'

# Start Jupyter
jupyter notebook

# Run specific example (in notebook)
# Just execute the corresponding cell

# Visualize graph (in notebook)
display(Image(app.get_graph().draw_mermaid_png()))
```

---

**Happy Learning!** 🎓✨

If you have questions, refer to:
1. **LANGGRAPH_TUTORIAL_GUIDE.md** for detailed explanations
2. **langgraph_tutorial.ipynb** for working code examples
3. Your instructor or study group
