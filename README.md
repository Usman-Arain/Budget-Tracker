# Budget Tracker with AI Assistant

## **Project Overview**
The Budget Tracker is a Python-based application designed to help users manage their finances by tracking income and expenses.
It provides a simple transaction manager, visual insights, and an AI-powered finance assistant that answers user queries about budgeting, savings, debt, and investments.

The tool aims to make personal finance management simple, accessible, and intelligent for users of all financial backgrounds.
---

## **Implemented Features**

### **1. Transaction Management**
- **Easy Transaction Entry**: Users can easily add transactions by specifying the amount, category, and whether it is income or an expense.
- **Update/Delete Transactions**: Users can edit or delete existing transactions to keep their records accurate and up-to-date.
- **Data Storage**: Transaction data is efficiently managed using a Pandas DataFrame.

### **2. Category Management**
- **Built-in and Custom Categories**: Users can select categories from a predefined list or create custom ones on the fly.
- **Flexible Allocation**: This feature allows users to categorize their income and expenses according to their personal financial situation.

### **3. Data Representation**
- **Visual Spending Analysis**: A pie chart visualizes spending by category, helping users understand their spending habits.
- **Visualization Tools**: The application utilizes Matplotlib for creating these visual insights.

### **4. Summary of Totals**
- **Comprehensive Financial Overview**: Users receive detailed information on total expenses, overall balance, and total income, providing a complete picture of their financial health.

### **5. AI Assistant**
- **Hugging Face Integration** → Uses Hugging Face Inference API to provide AI-powered responses.
- **Rule-Based Fallback** → If API is unavailable, a rule-based assistant gives reliable financial tips.
- **Smart Queries** → Ask:
  - “What is my total income?”
  - “What is my spending summary?”
  - “How can I save money?”
- **Predefined Suggestions** → Quick-access questions for instant advice.

---

## **Tools & Libraries Used**
- **Python**: The core programming language used for developing the application.
- **Pandas**: Utilized for managing and processing budget data.
- **Matplotlib**: Used to design and implement visualizations.
- **Tkinter**: Employed for creating the graphical user interface (GUI).
- **Requests**: Hugging Face API communication
---

## **How to Run the Application**
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/your-repo/budget-tracker.git
   cd budget-tracker


2. Create and activate virtual environment (recommended)
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate # Linux/Mac

3. Install the required libraries:
   ```bash
   pip install pandas matplotlib
   ```
   ```bash
   pip install pandas
   
4. Add Hugging Face API key:
  - Create a free account on Hugging Face
  - Get your API token from: https://huggingface.co/settings/tokens
  - Set it in your environment:
     ```bash
     $env:HF_TOKEN="your_api_token_here"

5. Run the application:
   ```bash
   python budget_tracker.py

---

This project combines traditional finance tracking with modern AI assistance, giving users not only insights into their current financial health but also practical advice for better money management.
