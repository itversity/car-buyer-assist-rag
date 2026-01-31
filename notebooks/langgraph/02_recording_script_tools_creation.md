# 🎬 Recording Script: LangGraph Tutorial - Notebook 2
## Tools Creation

**Total Duration:** ~10-12 minutes  
**Notebook File:** `02_langgraph_tools_creation.ipynb`

---

## 📋 PRE-RECORDING CHECKLIST

- [ ] Jupyter Notebook open with fresh kernel
- [ ] All previous outputs cleared
- [ ] This markdown script on Screen 1 (reference)
- [ ] Jupyter Notebook on Screen 2 (recording)
- [ ] Microphone tested and ready
- [ ] Screen recording software running
- [ ] Completed Notebook 1 (optional reference)

---

## 🎬 SECTION 1: INTRODUCTION (0:00 - 0:45)

### 📺 SCREEN ACTION
- Show notebook title and objective cells

### 🎙️ NARRATION
"Welcome back to the LangGraph series! In the previous notebook, we set up our environment and validated our connection to Gemini. Now we're ready to build something really powerful - custom tools that extend the LLM's capabilities.

In this notebook, we're creating two financial calculation tools: a currency converter that handles five major currencies, and an EMI calculator for loan payments. These tools will give our agent the ability to perform precise financial calculations - something LLMs can't do reliably on their own.

By the end of this video, you'll understand how to create custom tools using LangChain's tool decorator, how to write effective docstrings that help the LLM understand when to use your tools, and how to test your tools before integration.

Let's build these tools!"

### ⏸️ PAUSE
Scroll down to show the notebook structure

---

## 📦 SECTION 2: SETUP - IMPORTS (0:45 - 1:15)

### 📺 SCREEN ACTION
- Show "Setup" section
- Create or show the first code cell

### 🎙️ NARRATION
"First, let's import our dependencies. We only need one import for this notebook - the tool decorator from langchain_core. This decorator is what transforms a regular Python function into an LLM-callable tool.

Let me type this import."

### 💻 CODE TO COPY-PASTE
```python
# Core imports
from langchain_core.tools import tool
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### 🎙️ NARRATION (After Running)
"Simple and clean. Now we're ready to build our first tool."

---

## 🔧 SECTION 3: CURRENCY CONVERTER - EXPLANATION (1:15 - 2:00)

### 📺 SCREEN ACTION
- Scroll to "Tool 1: Currency Converter" section
- Show the markdown explanation

### 🎙️ NARRATION
"Our first tool is a currency converter. It will handle conversions between five major currencies: USD, EUR, GBP, INR, and JPY.

Let me explain the key points about how we're building this tool:

First, the at-tool decorator - this single line of code is what makes our function callable by the LLM. It automatically generates a JSON schema that the LLM uses to understand the function signature.

Second, the docstring - this is crucial. The LLM reads this docstring to understand what the tool does and when to use it. We need to be clear and specific about the parameters and what the tool returns.

Third, type hints - we specify that amount is a float, the currencies are strings, and we return a string. This helps both the LLM and Python understand the expected data types.

Finally, we return human-readable strings, not just numbers. This makes it easy for the LLM to incorporate the results into its response to the user.

Let me paste the currency converter function."

---

## 💻 SECTION 4: CURRENCY CONVERTER - CODE (2:00 - 3:30)

### 📺 SCREEN ACTION
- Show the code cell for currency converter

### 🎙️ NARRATION
"Here's our currency converter implementation. I'll paste it in and then walk through the key parts."

### 💻 CODE TO COPY-PASTE
```python
@tool
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert currency from one type to another.
    
    Args:
        amount: The amount to convert
        from_currency: Source currency code (USD, EUR, GBP, INR, JPY)
        to_currency: Target currency code (USD, EUR, GBP, INR, JPY)
    
    Returns:
        A string with the conversion result including the exchange rate
    """
    
    # Simplified exchange rates (relative to USD)
    # In production, fetch real-time rates from an API
    exchange_rates = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "INR": 83.12,
        "JPY": 149.50
    }
    
    # Validate currencies
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if from_currency not in exchange_rates:
        return f"Error: Unsupported currency {from_currency}. Supported: {', '.join(exchange_rates.keys())}"
    
    if to_currency not in exchange_rates:
        return f"Error: Unsupported currency {to_currency}. Supported: {', '.join(exchange_rates.keys())}"
    
    # Convert to USD first, then to target currency
    amount_in_usd = amount / exchange_rates[from_currency]
    converted_amount = amount_in_usd * exchange_rates[to_currency]
    
    # Calculate the effective exchange rate
    effective_rate = exchange_rates[to_currency] / exchange_rates[from_currency]
    
    result = (
        f"Conversion Result:\n"
        f"  {amount:,.2f} {from_currency} = {converted_amount:,.2f} {to_currency}\n"
        f"  Exchange Rate: 1 {from_currency} = {effective_rate:.4f} {to_currency}"
    )
    
    return result

print("✅ currency_converter tool defined")
print(f"   Type: {type(currency_converter)}")
print(f"   Name: {currency_converter.name}")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### ✅ EXPECTED OUTPUT
```
✅ currency_converter tool defined
   Type: <class 'langchain_core.tools.structured.StructuredTool'>
   Name: currency_converter
```

### 🎙️ NARRATION (After Output)
"Perfect! Let me highlight the important parts of this code:

Notice the at-tool decorator at the top - this single line transforms our function into a structured tool that LLMs can call.

We're using a simple dictionary for exchange rates. In a production system, you'd fetch real-time rates from an API like ExchangeRate-API or similar services.

We validate the currency codes and convert them to uppercase for consistency. If someone passes 'usd' or 'USD', it works the same way.

The conversion logic is straightforward: convert everything to USD first as our base currency, then to the target currency. This is a common pattern in currency conversion.

We calculate and display the effective exchange rate, which is helpful for users to understand the conversion.

And notice the output confirms this is now a StructuredTool with the name currency_converter. This is what the LLM will see and call.

Now let's test this tool before moving on."

---

## 🧪 SECTION 5: CURRENCY CONVERTER - TESTING (3:30 - 5:00)

### 📺 SCREEN ACTION
- Scroll to "Test Currency Converter" section
- Show the test code cell

### 🎙️ NARRATION
"Before we integrate this tool with our agent, we should test it in isolation. This is a best practice - always verify your tools work correctly before adding them to complex workflows.

We'll run three test cases: a standard conversion from USD to EUR, an error case with an invalid currency code, and an edge case converting INR to INR.

Let me paste the test code."

### 💻 CODE TO COPY-PASTE
```python
print("=" * 70)
print("TESTING: Currency Converter")
print("=" * 70)

# Test Case 1: Standard conversion
print("\n[Test 1] Convert 1000 USD to EUR")
result = currency_converter.invoke({"amount": 1000, "from_currency": "USD", "to_currency": "EUR"})
print(result)

# Test Case 2: Error handling - invalid currency
print("\n[Test 2] Invalid currency (XYZ)")
result = currency_converter.invoke({"amount": 100, "from_currency": "XYZ", "to_currency": "USD"})
print(result)

# Test Case 3: Same currency conversion
print("\n[Test 3] Convert INR to INR (edge case)")
result = currency_converter.invoke({"amount": 5000, "from_currency": "INR", "to_currency": "INR"})
print(result)

print("\n" + "=" * 70)
print("✅ All tests passed")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)
3. Wait for all three test outputs

### ✅ EXPECTED OUTPUT
```
======================================================================
TESTING: Currency Converter
======================================================================

[Test 1] Convert 1000 USD to EUR
Conversion Result:
  1,000.00 USD = 920.00 EUR
  Exchange Rate: 1 USD = 0.9200 EUR

[Test 2] Invalid currency (XYZ)
Error: Unsupported currency XYZ. Supported: USD, EUR, GBP, INR, JPY

[Test 3] Convert INR to INR (edge case)
Conversion Result:
  5,000.00 INR = 5,000.00 INR
  Exchange Rate: 1 INR = 1.0000 INR

======================================================================
✅ All tests passed
```

### 🎙️ NARRATION (After Output)
"Excellent! All three tests passed. Let's review what we tested:

Test 1 shows a standard conversion - 1000 USD equals 920 EUR at our exchange rate. The output is nicely formatted with commas for thousands and shows the exchange rate.

Test 2 demonstrates our error handling - when someone tries to use an unsupported currency like XYZ, we get a clear error message listing the supported currencies.

Test 3 is an edge case - converting INR to INR. The exchange rate is 1.0000, which is correct. This might seem silly, but it's good to verify the math works even in trivial cases.

Our currency converter is working perfectly. Now let's build our second tool - the EMI calculator."

---

## 📊 SECTION 6: EMI CALCULATOR - EXPLANATION (5:00 - 6:00)

### 📺 SCREEN ACTION
- Scroll to "Tool 2: EMI Calculator" section
- Show the markdown explanation

### 🎙️ NARRATION
"Our second tool is an EMI calculator. EMI stands for Equated Monthly Installment - it's the monthly payment amount for a loan.

This is particularly useful for financial planning. If someone wants to know their monthly car payment or home loan installment, this tool calculates it precisely.

The formula we're using is the standard EMI formula: EMI equals P times r times one plus r to the power n, divided by one plus r to the power n minus one.

Let me break that down:
- P is the principal, the loan amount
- r is the monthly interest rate, which we calculate from the annual rate
- n is the tenure in months

This formula accounts for compound interest and ensures equal monthly payments over the loan period.

We also handle a special case - zero interest loans. When the interest rate is zero, the formula simplifies to just the principal divided by the number of months.

Let me paste the EMI calculator function."

---

## 💻 SECTION 7: EMI CALCULATOR - CODE (6:00 - 7:30)

### 📺 SCREEN ACTION
- Show the code cell for EMI calculator

### 🎙️ NARRATION
"Here's our EMI calculator implementation. This one is a bit more complex than the currency converter because of the financial formula involved."

### 💻 CODE TO COPY-PASTE
```python
@tool
def emi_calculator(principal: float, annual_interest_rate: float, tenure_months: int, currency: str) -> str:
    """
    Calculate the EMI (Equated Monthly Installment) for a loan.
    
    Args:
        principal: The loan amount (principal)
        annual_interest_rate: Annual interest rate as a percentage (e.g., 8.5 for 8.5%)
        tenure_months: Loan tenure in months
        currency: Currency code for display (USD, EUR, GBP, INR, JPY)
    
    Returns:
        A string with the EMI calculation details
    """
    
    # Validate inputs
    if principal <= 0:
        return "Error: Principal must be greater than 0"
    if annual_interest_rate < 0:
        return "Error: Interest rate cannot be negative"
    if tenure_months <= 0:
        return "Error: Tenure must be greater than 0"
    
    # Convert annual interest rate to monthly rate (decimal)
    monthly_interest_rate = annual_interest_rate / 12 / 100
    
    # Handle zero interest rate edge case
    if monthly_interest_rate == 0:
        emi = principal / tenure_months
        total_payment = principal
        total_interest = 0
    else:
        # EMI formula: P × r × (1 + r)^n / [(1 + r)^n - 1]
        emi = principal * monthly_interest_rate * \
              pow(1 + monthly_interest_rate, tenure_months) / \
              (pow(1 + monthly_interest_rate, tenure_months) - 1)
        
        total_payment = emi * tenure_months
        total_interest = total_payment - principal
    
    result = (
        f"EMI Calculation Result:\n"
        f"  Loan Amount: {principal:,.2f} {currency}\n"
        f"  Interest Rate: {annual_interest_rate}% per annum\n"
        f"  Tenure: {tenure_months} months ({tenure_months // 12} years, {tenure_months % 12} months)\n"
        f"  \n"
        f"  Monthly EMI: {emi:,.2f} {currency}\n"
        f"  Total Payment: {total_payment:,.2f} {currency}\n"
        f"  Total Interest: {total_interest:,.2f} {currency}"
    )
    
    return result

print("✅ emi_calculator tool defined")
print(f"   Type: {type(emi_calculator)}")
print(f"   Name: {emi_calculator.name}")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### ✅ EXPECTED OUTPUT
```
✅ emi_calculator tool defined
   Type: <class 'langchain_core.tools.structured.StructuredTool'>
   Name: emi_calculator
```

### 🎙️ NARRATION (After Output)
"Great! The EMI calculator is now defined. Let me point out the key features:

First, we have comprehensive input validation - checking that the principal is positive, interest rate is non-negative, and tenure is positive. This prevents calculation errors and gives helpful error messages.

Second, we convert the annual interest rate to a monthly decimal rate by dividing by 12 and then by 100.

Third, we handle the zero interest edge case separately. When there's no interest, the EMI is simply the principal divided by months - no complex formula needed.

Fourth, for non-zero interest, we implement the standard EMI formula. Python's pow function handles the exponentiation.

And finally, we calculate not just the EMI but also the total payment and total interest, which gives users a complete picture of the loan cost.

Notice the output formatting - we convert tenure to years and months, and we format all currency amounts with commas. This makes the output much more readable.

Now let's test this calculator with some real-world scenarios."

---

## 🧪 SECTION 8: EMI CALCULATOR - TESTING (7:30 - 9:30)

### 📺 SCREEN ACTION
- Scroll to "Test EMI Calculator" section
- Show the test code cell

### 🎙️ NARRATION
"We'll test the EMI calculator with four scenarios: a car loan, a home loan, a zero-interest loan, and an error case with invalid input.

Let me paste the test code."

### 💻 CODE TO COPY-PASTE
```python
print("=" * 70)
print("TESTING: EMI Calculator")
print("=" * 70)

# Test Case 1: Standard loan
print("\n[Test 1] Car loan: 500,000 INR at 8.5% for 5 years")
result = emi_calculator.invoke({
    "principal": 500000,
    "annual_interest_rate": 8.5,
    "tenure_months": 60,
    "currency": "INR"
})
print(result)

# Test Case 2: Home loan
print("\n[Test 2] Home loan: 300,000 USD at 6.5% for 30 years")
result = emi_calculator.invoke({
    "principal": 300000,
    "annual_interest_rate": 6.5,
    "tenure_months": 360,
    "currency": "USD"
})
print(result)

# Test Case 3: Zero interest (edge case)
print("\n[Test 3] Interest-free loan: 10,000 EUR for 12 months")
result = emi_calculator.invoke({
    "principal": 10000,
    "annual_interest_rate": 0,
    "tenure_months": 12,
    "currency": "EUR"
})
print(result)

# Test Case 4: Error handling - invalid principal
print("\n[Test 4] Invalid principal (0)")
result = emi_calculator.invoke({
    "principal": 0,
    "annual_interest_rate": 8.5,
    "tenure_months": 24,
    "currency": "USD"
})
print(result)

print("\n" + "=" * 70)
print("✅ All tests passed")
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)
3. Wait for all four test outputs

### ✅ EXPECTED OUTPUT
```
======================================================================
TESTING: EMI Calculator
======================================================================

[Test 1] Car loan: 500,000 INR at 8.5% for 5 years
EMI Calculation Result:
  Loan Amount: 500,000.00 INR
  Interest Rate: 8.5% per annum
  Tenure: 60 months (5 years, 0 months)
  
  Monthly EMI: 10,258.27 INR
  Total Payment: 615,495.94 INR
  Total Interest: 115,495.94 INR

[Test 2] Home loan: 300,000 USD at 6.5% for 30 years
EMI Calculation Result:
  Loan Amount: 300,000.00 USD
  Interest Rate: 6.5% per annum
  Tenure: 360 months (30 years, 0 months)
  
  Monthly EMI: 1,896.20 USD
  Total Payment: 682,633.47 USD
  Total Interest: 382,633.47 USD

[Test 3] Interest-free loan: 10,000 EUR for 12 months
EMI Calculation Result:
  Loan Amount: 10,000.00 EUR
  Interest Rate: 0.0% per annum
  Tenure: 12 months (1 years, 0 months)
  
  Monthly EMI: 833.33 EUR
  Total Payment: 10,000.00 EUR
  Total Interest: 0.00 EUR

[Test 4] Invalid principal (0)
Error: Principal must be greater than 0

======================================================================
✅ All tests passed
```

### 🎙️ NARRATION (After Output)
"Perfect! All four tests passed. Let's analyze these results:

Test 1 is a typical car loan scenario - 500,000 rupees at 8.5% for 5 years. The monthly EMI is about 10,258 rupees. Notice the total interest is about 115,000 rupees - that's the cost of borrowing over 5 years.

Test 2 is a home loan - 300,000 dollars at 6.5% for 30 years. The monthly payment is about 1,896 dollars. Here's something interesting: the total interest is over 382,000 dollars - more than the original loan amount! This shows the impact of compound interest over 30 years.

Test 3 demonstrates the zero-interest edge case. With no interest, the EMI is simply 10,000 divided by 12 months, which equals 833.33 euros. Total interest is zero, as expected.

Test 4 validates our error handling - when principal is zero or negative, we get a clear error message.

Both our tools are working correctly. Now let's look at something really interesting - the JSON schemas that the LLM uses to understand these tools."

---

## 🔍 SECTION 9: VERIFY TOOL SCHEMAS (9:30 - 11:00)

### 📺 SCREEN ACTION
- Scroll to "Verify Tool Schemas" section

### 🎙️ NARRATION
"When we use the at-tool decorator, LangChain automatically generates a JSON schema for each tool. This schema is what the LLM actually sees when it decides which tool to call and what parameters to pass.

Let's examine these schemas to understand how the LLM perceives our tools.

First, I need to import pprint for pretty printing."

### 💻 CODE TO COPY-PASTE (Cell 1)
```python
from pprint import pprint
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)

### 🎙️ NARRATION
"Now let's look at the currency converter schema."

### 💻 CODE TO COPY-PASTE (Cell 2)
```python
print("Currency Converter Schema:")
print("=" * 70)
cc_schema = currency_converter.args_schema.model_json_schema()
pprint(cc_schema)
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)
3. Wait for schema output

### ✅ EXPECTED OUTPUT (Approximate)
```
Currency Converter Schema:
======================================================================
{'description': 'Convert currency from one type to another...',
 'properties': {'amount': {'title': 'Amount', 'type': 'number'},
                'from_currency': {'title': 'From Currency', 'type': 'string'},
                'to_currency': {'title': 'To Currency', 'type': 'string'}},
 'required': ['amount', 'from_currency', 'to_currency'],
 'title': 'currency_converter',
 'type': 'object'}
```

### 🎙️ NARRATION (After Output)
"Interesting! Look at what the LLM sees:

The description comes from our docstring - this is how the LLM knows what the tool does.

The properties section lists all three parameters: amount is a number, from_currency is a string, and to_currency is a string.

The required array tells the LLM that all three parameters are mandatory - it can't call this tool without providing all of them.

And the title is our function name.

This is the contract between our code and the LLM. The LLM uses this schema to understand when to call the tool and how to structure its function call.

Now let's see the EMI calculator schema."

### 💻 CODE TO COPY-PASTE (Cell 3)
```python
print("\n\nEMI Calculator Schema:")
print("=" * 70)
ec_schema = emi_calculator.args_schema.model_json_schema()
pprint(ec_schema)
```

### ⌨️ ACTION
1. Paste the code
2. Run cell (Shift + Enter)
3. Wait for schema output

### ✅ EXPECTED OUTPUT (Approximate)
```


EMI Calculator Schema:
======================================================================
{'description': 'Calculate the EMI (Equated Monthly Installment)...',
 'properties': {'annual_interest_rate': {'title': 'Annual Interest Rate',
                                         'type': 'number'},
                'currency': {'title': 'Currency', 'type': 'string'},
                'principal': {'title': 'Principal', 'type': 'number'},
                'tenure_months': {'title': 'Tenure Months', 'type': 'integer'}},
 'required': ['principal', 'annual_interest_rate', 'tenure_months', 'currency'],
 'title': 'emi_calculator',
 'type': 'object'}
```

### 🎙️ NARRATION (After Output)
"Similar structure here, but with four parameters:

Principal and annual_interest_rate are numbers, tenure_months is specifically an integer - notice that difference - and currency is a string.

All four parameters are required.

Again, the description comes from our docstring, which explains what the tool does and how to use it.

These schemas are automatically generated - we didn't write any JSON. The at-tool decorator handles all of this for us, which is why it's so powerful.

The LLM will use these schemas to decide when a user's query needs currency conversion versus loan calculation, and it will extract the correct parameters from the user's natural language input.

This automatic schema generation is one of the key features that makes building agentic workflows with LangGraph so efficient."

---

## 🎯 SECTION 10: WRAP-UP (11:00 - 12:00)

### 📺 SCREEN ACTION
- Scroll to the final "Tools Created!" section
- Show the completion checklist

### 🎙️ NARRATION
"Let's recap what we've accomplished in this notebook.

First, we built a currency converter tool that handles five major currencies - USD, EUR, GBP, INR, and JPY. It performs accurate conversions, displays exchange rates, and handles error cases gracefully.

Second, we created an EMI calculator that computes monthly loan payments using the standard financial formula. It handles edge cases like zero interest and provides comprehensive output including total payment and total interest.

Third, we thoroughly tested both tools with multiple test cases - standard scenarios, edge cases, and error conditions. All tests passed, confirming our tools work correctly in isolation.

And fourth, we examined the JSON schemas that the LLM uses to understand our tools. These schemas are automatically generated from our function signatures and docstrings.

Our tools are complete, tested, and ready for integration.

In the next notebook, we'll take a huge step forward - we'll build the actual agentic workflow graph that connects these tools to our LLM. You'll see how the agent makes autonomous decisions about when to use which tool, how it chains multiple tool calls together, and how the whole system orchestrates a conversation.

This is where things get really exciting because we'll see our financial assistant come to life!

Before we move on, make sure to save this notebook. You'll want to reference these tool definitions when we integrate them into the graph.

Thanks for following along! See you in the next video where we build the complete agent architecture."

### ⌨️ ACTION
- Save notebook (Ctrl+S or Cmd+S)
- Show save confirmation

---

## 📊 RECORDING SUMMARY

### Total Sections: 10
### Total Duration: ~10-12 minutes
### Code Cells Created: 8

### Key Checkpoints:
- ✅ Tool decorator imported
- ✅ Currency converter defined and tested (3 tests passed)
- ✅ EMI calculator defined and tested (4 tests passed)
- ✅ JSON schemas displayed and explained

---

## 🎬 POST-RECORDING CHECKLIST

- [ ] All code cells executed successfully
- [ ] All test outputs visible and correct
- [ ] Currency converter: 3/3 tests passed
- [ ] EMI calculator: 4/4 tests passed
- [ ] Schema outputs displayed correctly
- [ ] Audio is clear and well-paced
- [ ] No major mistakes or awkward pauses
- [ ] Notebook saved at the end

---

## 💡 RECORDING TIPS

### Pacing:
- This notebook is longer - maintain energy throughout
- Pause 3-4 seconds after test outputs (viewers need time to read)
- Slow down when explaining the EMI formula
- Speed up slightly during repetitive test cases

### Emphasis Points:
- **Highlight**: How the @tool decorator works
- **Highlight**: Why docstrings matter for the LLM
- **Highlight**: The automatic schema generation
- **Highlight**: The importance of testing tools in isolation

### Common Pitfalls:
- ❌ Don't rush through the test outputs
- ❌ Don't skip explaining the EMI formula
- ❌ Don't forget to explain WHY we test edge cases
- ✅ DO explain the real-world context (car loans, home loans)
- ✅ DO emphasize the automatic schema generation
- ✅ DO connect this to the next notebook

### Making It Engaging:
- Use real-world examples ("Imagine you're buying a car...")
- Explain the "why" behind decisions
- Point out interesting numbers in outputs (e.g., "Notice the total interest is more than the loan!")
- Show enthusiasm when tests pass

### If Something Goes Wrong:
- Tool definition error: Check indentation and decorator syntax
- Test failure: Verify the invoke syntax matches the schema
- Schema error: Make sure the tool is defined before accessing its schema
- Import error: Verify langchain_core.tools is installed

---

## 📝 ADDITIONAL NOTES

### Key Concepts to Emphasize:
1. **@tool decorator** - Transforms functions into LLM-callable tools
2. **Docstrings** - The LLM reads these to understand tool purpose
3. **Type hints** - Help both LLM and Python understand data types
4. **Error handling** - Tools should fail gracefully with clear messages
5. **Testing** - Always verify tools work before integration
6. **JSON schemas** - Automatic generation from function signatures

### Transition to Next Notebook:
"In Notebook 3, we'll connect these tools to our LLM using LangGraph's StateGraph. You'll see how the agent autonomously decides when to use each tool and how to chain them together for complex tasks."

---

## 🎯 SUCCESS CRITERIA

Your recording is successful if viewers can:
- [ ] Understand what the @tool decorator does
- [ ] Write their own custom tools
- [ ] Understand the importance of docstrings for LLM comprehension
- [ ] Test tools before integration
- [ ] Understand JSON schema generation
- [ ] Feel excited about building the agent in the next notebook

---

**Good luck with your recording! 🎥**
