# 🎬 Recording Script: LangGraph Tutorial - Notebook 1
## Setup & Validation

**Total Duration:** ~6-7 minutes  
**Notebook File:** `01_langgraph_setup_and_validation.ipynb`

---

## 📋 PRE-RECORDING CHECKLIST

- [ ] Jupyter Notebook open and kernel restarted
- [ ] All previous outputs cleared
- [ ] .env file configured with valid credentials
- [ ] This markdown script on Screen 1 (reference)
- [ ] Jupyter Notebook on Screen 2 (recording)
- [ ] Microphone tested
- [ ] Screen recording software ready

---

## 🎬 SECTION 1: INTRODUCTION (0:00 - 0:30)

### 📺 SCREEN ACTION
- Show notebook title and introduction cells

### 🎙️ NARRATION
"Welcome to the LangGraph series! I'm excited to guide you through building an intelligent financial assistant agent. In this first notebook, we'll set up our development environment and validate our connection to Google's Gemini AI. By the end of this video, you'll have a working foundation ready to build powerful AI agents. Let's get started!"

### ⏸️ PAUSE
Scroll down slowly to show the notebook structure

---

## 📝 SECTION 2: ENVIRONMENT VARIABLES (0:30 - 1:45)

### 📺 SCREEN ACTION
- Show the "Required Environment Variables" markdown cell

### 🎙️ NARRATION
PASTE THIS TO MARKDOWN CELL IN THE NOTEBOOK.
```env
# Gemini AI Configuration
GOOGLE_API_KEY=<api key from aistudio.google.com>

# LangSmith Observability (Optional)
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=langgraph-tutorial
LANGCHAIN_TRACING_V2=true
```
"Before we write any code, let's understand what configuration we need. You'll need to create a dot-env file in your project directory.

First, for Gemini AI, you need only API Key. Login into https://aistudio.google.com and then generate API Key.

Optionally, you can configure LangSmith for observability. This is great for debugging and monitoring your agents in production, but it's completely optional for this tutorial.

For package installation, run this pip install command to get langchain, langchain-google-genai, langgraph, and python-dotenv.

MAKE SURE TO ACTIVATE PYTHON VIRTUAL ENVIRONMENT AND RUN `pip install` COMMAND.

```
pip install langchain langchain-google-genai langgraph python-dotenv
```

Make sure you have your dot-env file ready before we continue. I'll give you a moment to pause the video if you need to set that up."

### ⏸️ PAUSE
Point to each section in the markdown cell with your cursor

### 💡 TIP
Remind viewers: "You can find the template for the .env file in the video description."

---

## 💻 SECTION 3: IMPORT DEPENDENCIES (1:45 - 2:30)

### 📺 SCREEN ACTION
- Scroll to "Import Dependencies" section
- Create new code cell or show existing empty cell

### 🎙️ NARRATION
"Now let's import our dependencies. We're importing ChatGoogleGenerativeAI - this is our interface to Google's Gemini models. We also need os and dotenv to handle environment variables.

Let me type this out."

### 💻 CODE TO COPY-PASTE
```python
# LLM Provider
from langchain_google_genai import ChatGoogleGenerativeAI

# Environment management
import os
from dotenv import load_dotenv

print("✅ All imports successful")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)
3. Wait for output

### ✅ EXPECTED OUTPUT
```
✅ All imports successful
```

### 🎙️ NARRATION (After Output)
"Perfect! All our imports are successful. If you see any import errors, make sure you've installed the required packages using pip."

---

## 🔐 SECTION 4: LOAD ENVIRONMENT (2:30 - 3:45)

### 📺 SCREEN ACTION
- Scroll to "Load Environment Variables" section
- Show the next code cell

### 🎙️ NARRATION
"Now we'll load our environment variables from the dot-env file. Notice I'm using a relative path here - adjust this based on where your dot-env file is located. In my case, it's two directories up, so I use dot-dot-slash-dot-env.

Let me paste this code."

### 💻 CODE TO COPY-PASTE (Cell 1)
```python
# Load environment variables from .env file
load_dotenv("../../.env")  # Adjust path to your .env location
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)
3. Wait for output

### ✅ EXPECTED OUTPUT
```
True
```

### 🎙️ NARRATION (After Output)
"Good! The True output means our dot-env file was found and loaded successfully. Now let's verify what variables were loaded."

### 📺 SCREEN ACTION
- Move to next code cell

### 🎙️ NARRATION
"Let me paste some code to display our configuration."

### 💻 CODE TO COPY-PASTE (Cell 2)
```python
print("✅ Environment loaded successfully")
print(f"   Project: {os.getenv('GOOGLE_PROJECT_ID')}")
print(f"   Region: {os.getenv('GOOGLE_REGION')}")
print(f"   LangSmith Tracing: {'Enabled' if os.getenv('LANGCHAIN_TRACING_V2') else 'Disabled'}")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)
3. Wait for output

### ✅ EXPECTED OUTPUT
```
✅ Environment loaded successfully
   Project: your-project-id
   Region: us-central1
   LangSmith Tracing: Disabled
```

### 🎙️ NARRATION (After Output)
"Excellent! You can see our Google Cloud Project ID, the region we're using, and whether LangSmith tracing is enabled. In my case, it's disabled since we're not using it for this tutorial. Your project ID will be different - that's perfectly normal."

---

## 🤖 SECTION 5: INITIALIZE LLM (3:45 - 4:45)

### 📺 SCREEN ACTION
- Scroll to "Initialize LLM" section
- Show the next code cell

### 🎙️ NARRATION
"Now for the most important part - initializing our Large Language Model connection. We're using Gemini 2.5 Pro, which is Google's most capable model for complex reasoning and agentic workflows.

Let me explain the key parameters:
- Model is gemini-2.5-pro
- Temperature is 0.3 - this keeps responses consistent and factual, which is important for financial calculations
- Max tokens is 1024 - this limits response length
- We pass the project ID and region from our environment variables

Let me paste this initialization code."

### 💻 CODE TO COPY-PASTE
```python
# Create the base LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0.3,  # Lower temperature for consistent, factual responses
    max_tokens=1024,
    project=os.getenv("GOOGLE_PROJECT_ID"),
    location=os.getenv("GOOGLE_REGION")
)

print("✅ LLM initialized successfully")
print(f"   Model: gemini-2.5-pro")
print(f"   Temperature: 0.3")
print(f"   Max Tokens: 1024")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)
3. Wait for output (may take 2-3 seconds)

### ✅ EXPECTED OUTPUT
```
✅ LLM initialized successfully
   Model: gemini-2.5-pro
   Temperature: 0.3
   Max Tokens: 1024
```

### 🎙️ NARRATION (After Output)
"Perfect! Our LLM is initialized. This creates the connection to Gemini but doesn't send any requests yet. Let's verify the connection actually works."

---

## ✅ SECTION 6: TEST CONNECTIVITY (4:45 - 5:45)

### 📺 SCREEN ACTION
- Scroll to "Test LLM Connectivity" section
- Show the next code cell

### 🎙️ NARRATION
"Before we proceed, we need to verify our LLM connection is working properly. We'll send a simple test message asking Gemini to respond with 'Hello from LangGraph' if it can read our message.

This validation is critical - if this fails, we'd need to check our Google Cloud credentials, verify the API is enabled, or check our network connection.

Let me paste the test code."

### 💻 CODE TO COPY-PASTE
```python
# Simple test to verify LLM is working
test_response = llm.invoke("Say 'Hello from LangGraph!' if you can read this.")

print("🧪 LLM Test:")
print(f"   Response: {test_response.content}")
print("\n✅ LLM connectivity verified!")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)
3. Wait for response (may take 3-5 seconds for API call)

### ✅ EXPECTED OUTPUT
```
🧪 LLM Test:
   Response: Hello from LangGraph!

✅ LLM connectivity verified!
```

### 🎙️ NARRATION (After Output)
"Excellent! We got the expected response from Gemini. This confirms three things: our Google Cloud credentials are valid, the Gemini API is accessible, and our configuration is correct. We're now ready to build our agent!"

### ⏸️ PAUSE
Take a brief pause (2 seconds) to let the success sink in

---

## 🎯 SECTION 7: WRAP-UP (5:45 - 6:30)

### 📺 SCREEN ACTION
- Scroll to the final "Setup Complete!" section
- Show the checklist

### 🎙️ NARRATION
"Let's recap what we've accomplished in this setup notebook.

First, we loaded and validated our environment variables - our Google Cloud configuration is working.

Second, we successfully imported all required dependencies - langchain, langgraph, and the Gemini interface.

Third, we initialized our LLM connection to Gemini 2.5 Pro with appropriate temperature and token settings.

And finally, we verified connectivity with a successful test message.

We now have a solid, tested foundation for building our financial assistant agent.

In the next notebook, we'll create custom tools - specifically a currency converter and an EMI calculator. These tools will extend the LLM's capabilities with precise financial calculations. You see, while Gemini is excellent at understanding language and reasoning, it can't perform exact mathematical calculations reliably. That's where tools come in - they give the LLM superpowers!

Thanks for following along! Make sure to save this notebook, and I'll see you in the next video where we build some powerful financial tools."

### ⌨️ ACTION
- Save notebook (Ctrl+S or Cmd+S)
- Show the save confirmation

---

## 📊 RECORDING SUMMARY

### Total Sections: 7
### Total Duration: ~6-7 minutes
### Code Cells Created: 5

### Key Checkpoints:
- ✅ All imports successful
- ✅ Environment loaded (True)
- ✅ Configuration displayed correctly
- ✅ LLM initialized
- ✅ Test message successful

---

## 🎬 POST-RECORDING CHECKLIST

- [ ] All code cells executed successfully
- [ ] All outputs are visible and correct
- [ ] Audio is clear throughout
- [ ] No long awkward pauses
- [ ] Cursor highlights used effectively
- [ ] Notebook saved at the end
- [ ] Ready to export/edit video

---

## 💡 RECORDING TIPS

### Pacing:
- Speak at 140-160 words per minute
- Pause 2-3 seconds after running each cell
- Give viewers time to see outputs

### Tone:
- Enthusiastic but professional
- Explain WHY, not just WHAT
- Assume viewers are intelligent but new to LangGraph

### Common Mistakes to Avoid:
- ❌ Don't say "um" or "uh" - pause instead
- ❌ Don't apologize for the interface
- ❌ Don't rush through outputs
- ✅ DO explain what success looks like
- ✅ DO mention common errors viewers might see
- ✅ DO encourage viewers to pause if needed

### If Something Goes Wrong:
- Stay calm and explain what happened
- Show how to debug/fix it
- This makes the tutorial more valuable!

---

## 📝 NOTES SECTION

Use this space for any personal notes or adjustments:

---

**Good luck with your recording! 🎥**
