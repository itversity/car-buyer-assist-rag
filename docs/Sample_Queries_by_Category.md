# Sample Queries by Category

**Car Buyer Assist RAG Application**

*Query Reference Document*

---

## Overview

This document extracts and organizes all sample queries from the [Car_Buyer_Assist_RAG_BRD_Streamlined.md](Car_Buyer_Assist_RAG_BRD_Streamlined.md) Business Requirements Document. These queries represent the diverse question types that the Car Buyer Assist RAG system should be able to handle, along with examples of out-of-scope queries that fall outside the system's intended capabilities.

**Total Query Categories:** 6
**Total Sample Queries:** 24 (18 in-scope + 6 out-of-scope)

---

## Specification Queries

Questions about vehicle specifications, performance metrics, and technical details.

- "What is the fuel efficiency of the Camry hybrid?"
- "How much horsepower does the RAV4 Prime have?"
- "What is the towing capacity of the Tacoma V6?"
- "What is the electric range of the bZ4X?"

---

## Comparison Queries

Questions comparing different vehicles or asking about differences between models.

- "Compare fuel efficiency between Prius and Prius Prime"
- "What are the differences between RAV4 and Highlander?"
- "Which sedan is better for first-time buyers?"
- "How does the Camry compare to the Honda Accord?"

---

## Feature & Safety Queries

Questions about available features, safety systems, technology, and vehicle options.

- "What safety features does the Corolla have?"
- "Does the Highlander have third-row seating?"
- "What technology features are in the RAV4?"
- "Is AWD available on the Camry?"

---

## Pricing & Value Queries

Questions about vehicle pricing, trim levels, and value propositions.

- "What is the starting price of the Corolla?"
- "Which Toyota SUV offers the best value?"
- "What trim levels are available for the Tacoma?"

---

## Recommendation Queries

Questions asking for vehicle suggestions or recommendations based on specific buyer needs and use cases.

- "What Toyota vehicle is best for a family of five?"
- "I need a fuel-efficient car for city driving, what do you recommend?"
- "Which hybrid has the longest electric range?"

---

## Out of Scope Queries

Questions that fall outside the system's intended capabilities and scope. These queries involve information not available in the Toyota specification documents or require functionality beyond the RAG system's design (such as real-time data, scheduling, or non-Toyota information).

- "Where is the nearest Toyota dealership?"
- "Can you schedule a test drive for me?"
- "How does the Honda CR-V compare to the RAV4?"
- "What's the insurance cost for a Camry?"
- "When is my car due for an oil change?"
- "What's better, Toyota or Lexus brand?"

---

## Notes

- **In-Scope Queries:** The system should provide accurate, well-cited responses for the first 5 categories based on the Toyota specification PDFs.
- **Out-of-Scope Queries:** The system should gracefully acknowledge these questions are outside its capabilities rather than attempting to answer or hallucinating information.
- **Source Document:** All in-scope queries are extracted from the "User Scenarios & Sample Queries" section of the BRD (lines 46-82).
