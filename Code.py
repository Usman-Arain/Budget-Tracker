import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
import os
from advanced_llm_assistant import AdvancedFinanceLLMAssistant, FinanceRuleBasedAssistant

# File to store data
DATA_FILE = "budget_history.csv"

# Load previous data if file exists
try:
    if os.path.exists(DATA_FILE):
        budget_data = pd.read_csv(DATA_FILE)
        # Validate the DataFrame has required columns
        required_columns = ["Amount", "Category", "Type"]
        if not all(col in budget_data.columns for col in required_columns):
            budget_data = pd.DataFrame(columns=required_columns)
    else:
        budget_data = pd.DataFrame(columns=["Amount", "Category", "Type"])
except Exception as e:
    print(f"Error loading data: {e}")
    budget_data = pd.DataFrame(columns=["Amount", "Category", "Type"])

# List of categories
categories = ["Groceries", "Utilities", "Rent", "Entertainment", "Salary", "Freelance"]

# Initialize AI assistants
hf_token = 'hf_token'
llm_assistant = AdvancedFinanceLLMAssistant(hf_token=hf_token)
rule_based_assistant = FinanceRuleBasedAssistant(budget_data, categories)

# Function to save data
def save_data():
    try:
        budget_data.to_csv(DATA_FILE, index=False)
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save data: {str(e)}")

# Function to add a transaction
def add_transaction():
    global budget_data
    amount = amount_entry.get().strip()
    category = category_combobox.get().strip()
    t_type = type_var.get()

    if not amount or not category or not t_type:
        messagebox.showerror("Missing Information", "Please fill out all fields.")
        return
    
    if category == "Select an option":
        messagebox.showerror("Invalid Category", "Please select a valid category.")
        return

        try:
            amount = float(amount)
            if amount <= 0:
                messagebox.showerror("Invalid Input", "Amount must be greater than 0.")
            return
            
            new_transaction = pd.DataFrame({"Amount": [amount], "Category": [category], "Type": [t_type]})
            budget_data = pd.concat([budget_data, new_transaction], ignore_index=True)
            update_treeview()
            update_totals()
            save_data()  # Save to file
            amount_entry.delete(0, tk.END)
            category_combobox.set("Select an option")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to add a new category
def add_category():
    new_category = new_category_entry.get().strip()
    if not new_category:
        messagebox.showerror("Invalid Category", "Please enter a category name.")
        return
        
    if new_category in categories:
        messagebox.showerror("Invalid Category", "Category already exists.")
        return
        
    try:
        categories.append(new_category)
        category_combobox['values'] = categories
        new_category_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"Category '{new_category}' added successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to update the treeview with the DataFrame data
def update_treeview():
    for i in tree.get_children():
        tree.delete(i)
    for idx, row in budget_data.iterrows():
        tree.insert("", tk.END, values=(idx, row["Amount"], row["Category"], row["Type"]))

# Function to update totals
def update_totals():
    total_expense = budget_data[budget_data["Type"] == "Expense"]["Amount"].sum()
    total_income = budget_data[budget_data["Type"] == "Income"]["Amount"].sum()
    total_amount = total_income - total_expense

    total_expense_label.config(text=f"Total Expense: ${total_expense:.2f}")
    total_income_label.config(text=f"Total Income: ${total_income:.2f}")
    total_amount_label.config(text=f"Overall Total: ${total_amount:.2f}")

# Function to visualize spending
def visualize_spending():
    try:
        expense_data = budget_data[budget_data["Type"] == "Expense"]
        if expense_data.empty:
            messagebox.showinfo("No Data", "No expense data available to visualize.")
            return
            
        expense_summary = expense_data.groupby("Category").sum()
        
        # Plotting a pie chart for expenses
        plt.figure(figsize=(8, 6))
        plt.pie(expense_summary["Amount"], labels=expense_summary.index, autopct='%1.1f%%')
        plt.title("Expenses by Category")
        plt.show()
    except Exception as e:
        messagebox.showerror("Visualization Error", f"Failed to create visualization: {str(e)}")
# Function to open the edit transaction dialog
def edit_transaction():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("No Selection", "Please select a transaction to edit.")
        return

    def save_edit():
        nonlocal selected_item
        try:
            new_amount = float(edit_amount_entry.get())
            new_category = edit_category_combobox.get()
            new_type = edit_type_var.get()
            
            # Update the data in the DataFrame
            item_index = int(tree.item(selected_item)["values"][0])  # Get the DataFrame index
            if item_index in budget_data.index:
                budget_data.at[item_index, "Amount"] = new_amount
                budget_data.at[item_index, "Category"] = new_category
                budget_data.at[item_index, "Type"] = new_type
                update_treeview()
                update_totals()
                save_data()  # Save changes
                edit_window.destroy()
            else:
                messagebox.showerror("Error", "Transaction not found. Please refresh and try again.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    item_data = tree.item(selected_item)["values"]
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Transaction")

    ttk.Label(edit_window, text="Edit Amount:").grid(row=0, column=0, padx=5, pady=5)
    edit_amount_entry = ttk.Entry(edit_window)
    edit_amount_entry.grid(row=0, column=1, padx=5, pady=5)
    edit_amount_entry.insert(0, item_data[1])  # Pre-fill amount

    ttk.Label(edit_window, text="Edit Category:").grid(row=1, column=0, padx=5, pady=5)
    edit_category_combobox = ttk.Combobox(edit_window, values=categories)
    edit_category_combobox.grid(row=1, column=1, padx=5, pady=5)
    edit_category_combobox.set(item_data[2])  # Pre-fill category

    ttk.Label(edit_window, text="Edit Type:").grid(row=2, column=0, padx=5, pady=5)
    edit_type_var = tk.StringVar(value=item_data[3])
    ttk.Radiobutton(edit_window, text="Income", variable=edit_type_var, value="Income").grid(row=2, column=1, sticky=tk.W)
    ttk.Radiobutton(edit_window, text="Expense", variable=edit_type_var, value="Expense").grid(row=3, column=1, sticky=tk.W)

    ttk.Button(edit_window, text="Save Changes", command=save_edit).grid(row=4, column=0, columnspan=2, pady=10)

# Function to delete a transaction
def delete_transaction():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("No Selection", "Please select a transaction to delete.")
        return

    if messagebox.askyesno("Delete Transaction", "Are you sure you want to delete this transaction?"):
        try:
            item_index = int(tree.item(selected_item)["values"][0])  # Get the DataFrame index
            global budget_data
            if item_index in budget_data.index:
                budget_data = budget_data.drop(index=item_index).reset_index(drop=True)
                update_treeview()
                update_totals()
                save_data()
            else:
                messagebox.showerror("Error", "Transaction not found. Please refresh and try again.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Add right-click context menu for Treeview
def setup_treeview_context_menu():
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Edit Transaction", command=edit_transaction)
    menu.add_command(label="Delete Transaction", command=delete_transaction)

    def show_context_menu(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    tree.bind("<Button-3>", show_context_menu)  # Right-click event

# Function to get budget context for LLM
def get_budget_context():
    """Generate a summary of the user's budget data for LLM context"""
    try:
        total_income = budget_data[budget_data["Type"] == "Income"]["Amount"].sum()
        total_expense = budget_data[budget_data["Type"] == "Expense"]["Amount"].sum()
        net_balance = total_income - total_expense
        
        # Get top spending categories
        expense_data = budget_data[budget_data["Type"] == "Expense"]
        if not expense_data.empty:
            top_categories = expense_data.groupby("Category")["Amount"].sum().nlargest(3)
            top_categories_str = ", ".join([f"{cat}: ${amt:.2f}" for cat, amt in top_categories.items()])
        else:
            top_categories_str = "No expense data"
        
        context = f"""Budget Summary:
- Total Income: ${total_income:.2f}
- Total Expenses: ${total_expense:.2f}
- Net Balance: ${net_balance:.2f}
- Top Spending Categories: {top_categories_str}
- Available Categories: {', '.join(categories)}
- Total Transactions: {len(budget_data)}"""
        
        return context
    except Exception as e:
        return f"Error generating budget context: {str(e)}"

# Function to handle AI assistant queries with LLM integration
def ai_assistant_query(query):
    global rule_based_assistant
    
    # Initialize rule-based assistant if not done yet
    if rule_based_assistant is None:
        rule_based_assistant = FinanceRuleBasedAssistant(budget_data, categories)
    
    # First, handle conversational greetings and common queries
    query_lower = query.lower()
    
    # Handle greetings and conversational queries
    if any(word in query_lower for word in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
        return "👋 Hello! I'm your personal finance assistant. I can help you with budget analysis, financial advice, investment strategies, and more. What would you like to know about your finances?"
    
    elif any(word in query_lower for word in ["how are you", "how's it going", "what's up"]):
        return "😊 I'm doing great! I'm here to help you with all your financial questions and budget management. How can I assist you today?"
    
    elif any(word in query_lower for word in ["thank", "thanks"]):
        return "😊 You're welcome! I'm always here to help with your financial questions. Is there anything else you'd like to know?"
    
    elif any(word in query_lower for word in ["help", "what can you do"]):
        return "🤖 I can help you with:\n• Analyzing your budget and spending patterns\n• Providing personalized financial advice\n• Investment and savings strategies\n• Debt management tips\n• Tax planning and optimization\n• Credit score improvement\n• Real estate and retirement planning\n• And much more!\n\nWhat specific area would you like to explore?"
    
    # Handle simple acknowledgments with friendly responses
    elif any(word in query_lower for word in ["ok", "okay", "alright", "sure", "yes", "yeah"]):
        return "😊 Great! I'm here to help with any financial questions you have. What would you like to know about your budget or personal finance?"
    
    elif any(word in query_lower for word in ["no", "nope", "not really"]):
        return "😊 No problem! Take your time. I'm here whenever you need help with your finances or budget questions."
    
    elif any(word in query_lower for word in ["maybe", "perhaps", "i think so"]):
        return "😊 That's perfectly fine! Feel free to ask me anything about your finances when you're ready. I'm here to help!"
    
    # Handle specific budget-related queries
    elif any(word in query_lower for word in ["total", "income", "expense", "balance"]):
        total_expense = budget_data[budget_data["Type"] == "Expense"]["Amount"].sum()
        total_income = budget_data[budget_data["Type"] == "Income"]["Amount"].sum()
        net_balance = total_income - total_expense
        
        if "total" in query_lower:
            return f"📊 **Your Budget Summary:**\n• Total Income: ${total_income:.2f}\n• Total Expenses: ${total_expense:.2f}\n• Net Balance: ${net_balance:.2f}"
        elif "income" in query_lower:
            return f"💰 **Income Summary:**\n• Total Income: ${total_income:.2f}\n• Number of income transactions: {len(budget_data[budget_data['Type'] == 'Income'])}"
        elif "expense" in query_lower:
            return f"💸 **Expense Summary:**\n• Total Expenses: ${total_expense:.2f}\n• Number of expense transactions: {len(budget_data[budget_data['Type'] == 'Expense'])}"
        elif "balance" in query_lower:
            return f"⚖️ **Current Balance:** ${net_balance:.2f}\n{'✅ You are saving money!' if net_balance > 0 else '⚠️ You are spending more than you earn.'}"
    
    elif "category" in query_lower or "categories" in query_lower:
        return f"📋 **Available Categories:**\n{', '.join(categories)}\n\n💡 You can add new categories using the 'Add New Category' field below."
    
    elif "add transaction" in query_lower or "how to add" in query_lower:
        return "➕ **How to Add a Transaction:**\n1. Enter the amount in the 'Amount' field\n2. Select a category from the dropdown\n3. Choose 'Income' or 'Expense' type\n4. Click 'Add Transaction'\n\n💡 The transaction will be automatically saved!"
    
    elif "spending summary" in query_lower or "breakdown" in query_lower:
        expense_data = budget_data[budget_data["Type"] == "Expense"]
        if not expense_data.empty:
            breakdown = expense_data.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            response = "📊 **Spending Breakdown:**\n"
            for cat, amt in breakdown.items():
                percentage = (amt / breakdown.sum()) * 100
                response += f"• {cat}: ${amt:.2f} ({percentage:.1f}%)\n"
            max_category = breakdown.index[0]
            response += f"\n💡 **Insight:** You spend the most on {max_category}. Consider reviewing this category."
            return response
        else:
            return "📊 No expense data available to analyze. Add some expense transactions to see your spending breakdown!"
    
    elif "daily balance" in query_lower:
        total_expense = budget_data[budget_data["Type"] == "Expense"]["Amount"].sum()
        total_income = budget_data[budget_data["Type"] == "Income"]["Amount"].sum()
        days_in_month = 30
        daily_balance = (total_income - total_expense) / days_in_month
        return f"📅 **Daily Balance:** ${daily_balance:.2f} per day\n💡 This is your average daily spending power based on a 30-day month."
    
    elif "savings suggestion" in query_lower or "saving advice" in query_lower:
        total_income = budget_data[budget_data["Type"] == "Income"]["Amount"].sum()
        total_expense = budget_data[budget_data["Type"] == "Expense"]["Amount"].sum()
        savings = total_income - total_expense
        if savings > 0:
            return f"🎉 **Great job!** You're saving ${savings:.2f}!\n\n💡 **Next Steps:**\n• Consider investing in low-cost index funds\n• Build an emergency fund (3-6 months expenses)\n• Set up automatic transfers to savings"
        else:
            return f"⚠️ **Spending Alert:** You're spending ${abs(savings):.2f} more than you earn.\n\n💡 **Action Plan:**\n• Review and cut non-essential expenses\n• Look for ways to increase income\n• Create a strict budget and stick to it"
    
    # Try simple LLM first for natural responses
    try:
        # Get budget context for LLM
        budget_context = get_budget_context()
        
        # Try simple LLM
        llm_response = llm_assistant.generate_response(query, budget_context)
        if llm_response and _is_valid_response(llm_response):
            return f"🤖 **AI Assistant:**\n{llm_response}"
            
    except Exception as e:
        print(f"LLM error: {e}")
    
    # Use smart template system for natural chatbot feel
    try:
        # Get a natural, contextual response
        natural_response = get_natural_response(query, budget_data, categories)
        if natural_response:
            return natural_response
    except Exception as e:
        print(f"Natural response error: {e}")
    
    # Fallback to rule-based assistant for specific financial topics
    try:
        rule_response = rule_based_assistant.generate_response(query)
        if rule_response:
            return f"💡 **Financial Advice:**\n{rule_response}"
    except Exception as e:
        print(f"Rule-based assistant error: {e}")
    
    # Final fallback with conversational response
    return "🤔 I'm not sure I understand that question. I can help you with:\n• Your budget analysis and totals\n• Financial advice and planning\n• Investment and savings strategies\n• Debt management\n• How to use this budget tracker\n\nWhat would you like to know about your finances?"

def get_natural_response(query, budget_data, categories):
    """Generate natural, contextual responses that feel like a real chatbot"""
    query_lower = query.lower()
    
    # Get budget context for personalized responses
    total_income = budget_data[budget_data["Type"] == "Income"]["Amount"].sum()
    total_expense = budget_data[budget_data["Type"] == "Expense"]["Amount"].sum()
    net_balance = total_income - total_expense
    
    # Natural conversation patterns
    if any(word in query_lower for word in ["how are you", "how's it going", "what's up", "how do you do"]):
        responses = [
            "😊 I'm doing great! I'm here to help you with all your financial questions and budget management. How can I assist you today?",
            "😊 I'm excellent! Ready to help you with your finances. What would you like to know about your budget?",
            "😊 I'm doing wonderful! I'm here to support you with financial planning and budget analysis. What can I help you with?"
        ]
        return responses[hash(query) % len(responses)]
    
    elif any(word in query_lower for word in ["thank", "thanks", "appreciate"]):
        responses = [
            "😊 You're very welcome! I'm always here to help with your financial questions. Is there anything else you'd like to know?",
            "😊 My pleasure! I'm here whenever you need assistance with your budget or finances. What else can I help with?",
            "😊 You're welcome! I'm glad I could help. Feel free to ask me anything about your finances!"
        ]
        return responses[hash(query) % len(responses)]
    
    elif any(word in query_lower for word in ["ok", "okay", "alright", "sure", "yes", "yeah", "good", "great"]):
        responses = [
            "😊 Great! I'm here to help with any financial questions you have. What would you like to know about your budget or personal finance?",
            "😊 Excellent! I'm ready to assist you with your finances. What specific area would you like to explore?",
            "😊 Perfect! I'm here to help you with budget analysis, financial advice, or any money-related questions. What's on your mind?"
        ]
        return responses[hash(query) % len(responses)]
    
    elif any(word in query_lower for word in ["no", "nope", "not really", "maybe later"]):
        responses = [
            "😊 No problem! Take your time. I'm here whenever you need help with your finances or budget questions.",
            "😊 That's perfectly fine! Feel free to ask me anything about your finances when you're ready. I'm here to help!",
            "😊 No worries at all! I'll be here whenever you need assistance with your budget or financial planning."
        ]
        return responses[hash(query) % len(responses)]
    
    elif any(word in query_lower for word in ["help", "what can you do", "capabilities", "what do you know"]):
        responses = [
            "🤖 I can help you with:\n• Analyzing your budget and spending patterns\n• Providing personalized financial advice\n• Investment and savings strategies\n• Debt management tips\n• Tax planning and optimization\n• Credit score improvement\n• Real estate and retirement planning\n• And much more!\n\nWhat specific area would you like to explore?",
            "🤖 I'm your personal finance assistant! I can help with:\n• Budget analysis and tracking\n• Financial planning and advice\n• Investment strategies\n• Debt management\n• Savings optimization\n• Retirement planning\n• And any other money-related questions!\n\nWhat would you like to know about?",
            "🤖 I specialize in personal finance! I can assist with:\n• Budget creation and management\n• Investment guidance\n• Debt reduction strategies\n• Savings plans\n• Financial goal setting\n• Money management tips\n• And so much more!\n\nWhat financial topic interests you?"
        ]
        return responses[hash(query) % len(responses)]
    
    # Financial advice with natural language
    elif any(word in query_lower for word in ["save", "saving", "savings", "how to save"]):
        responses = [
            "💡 Great question about saving! Here are some effective strategies:\n• Follow the 50/30/20 rule: 50% needs, 30% wants, 20% savings\n• Set up automatic transfers to savings accounts\n• Build an emergency fund covering 3-6 months of expenses\n• Use high-yield savings accounts for better returns\n• Track your savings progress monthly\n\nWould you like me to help you create a specific savings plan?",
            "💡 I love helping with savings strategies! Here's what I recommend:\n• Start with small, consistent amounts\n• Automate your savings to make it effortless\n• Build an emergency fund first, then focus on other goals\n• Consider different types of savings accounts\n• Review and adjust your savings goals regularly\n\nWhat's your current savings goal?",
            "💡 Saving money is one of my favorite topics! Here are some proven methods:\n• Pay yourself first - save before spending\n• Use the envelope method for discretionary spending\n• Look for ways to reduce recurring expenses\n• Set up multiple savings accounts for different goals\n• Celebrate small savings milestones\n\nHow much are you looking to save each month?"
        ]
        return responses[hash(query) % len(responses)]
    
    elif any(word in query_lower for word in ["invest", "investment", "investing", "stocks", "portfolio"]):
        responses = [
            "📈 Investing is a great way to build wealth! Here's what I suggest:\n• Start with low-cost index funds or ETFs\n• Diversify your portfolio across different asset classes\n• Consider your risk tolerance and time horizon\n• Take advantage of employer 401(k) matching\n• Regularly rebalance your portfolio\n• Remember: time in market beats timing the market\n\nWhat's your investment timeline and risk tolerance?",
            "📈 I'm excited to help with investing! Here are the basics:\n• Start early to benefit from compound interest\n• Don't try to time the market\n• Diversify across stocks, bonds, and other assets\n• Consider tax-advantaged accounts like IRAs\n• Keep costs low with index funds\n• Stay disciplined and avoid emotional decisions\n\nWhat type of investments are you considering?",
            "📈 Great question about investing! Here's my advice:\n• Begin with a solid foundation of index funds\n• Dollar-cost average to reduce timing risk\n• Don't put all your eggs in one basket\n• Consider your age and investment timeline\n• Rebalance periodically to maintain your target allocation\n• Focus on long-term growth, not short-term gains\n\nWhat's your current investment experience level?"
        ]
        return responses[hash(query) % len(responses)]
    
    elif any(word in query_lower for word in ["debt", "loan", "credit", "pay off", "payoff"]):
        responses = [
            "💳 Debt management is crucial for financial health! Here's my approach:\n• Pay off high-interest debt first (credit cards)\n• Consider debt consolidation if rates are lower\n• Make more than minimum payments when possible\n• Use the debt snowball or avalanche method\n• Avoid taking on new debt while paying off existing debt\n• Consider balance transfer cards for temporary relief\n\nWhat type of debt are you dealing with?",
            "💳 I understand debt can be stressful! Here's how to tackle it:\n• List all your debts with interest rates and minimum payments\n• Choose a strategy: snowball (smallest first) or avalanche (highest rate first)\n• Look for ways to increase your debt payments\n• Consider negotiating with creditors for better terms\n• Avoid new debt while paying off existing debt\n• Celebrate each debt you pay off!\n\nWhat's your current debt situation?",
            "💳 Debt doesn't have to control your life! Here's my strategy:\n• Focus on one debt at a time for maximum impact\n• Consider the debt avalanche method for fastest payoff\n• Look for opportunities to refinance at lower rates\n• Create a realistic budget that includes extra debt payments\n• Use windfalls (bonuses, tax refunds) to pay down debt\n• Stay motivated by tracking your progress\n\nHow much total debt are you working with?"
        ]
        return responses[hash(query) % len(responses)]
    
    # Personalized budget responses
    elif any(word in query_lower for word in ["my budget", "my money", "my finances", "my spending"]):
        if net_balance > 0:
            responses = [
                f"🎉 That's fantastic! You're currently saving ${net_balance:.2f} each month. This is a great position to be in! You might want to consider:\n• Building up your emergency fund\n• Investing for long-term goals\n• Paying down any high-interest debt\n• Setting up automatic investments\n\nWhat would you like to focus on next?",
                f"🎉 Excellent work! You have a positive cash flow of ${net_balance:.2f}. This gives you great options:\n• Emergency fund (3-6 months of expenses)\n• Retirement savings (401k, IRA)\n• Investment portfolio\n• Debt payoff acceleration\n• Major purchase savings\n\nWhat's your next financial priority?",
                f"🎉 You're doing great! With ${net_balance:.2f} in monthly savings, you're in a strong position. Consider:\n• Automating your savings\n• Diversifying your investments\n• Planning for major life events\n• Optimizing your tax situation\n• Building long-term wealth\n\nWhat financial goal is most important to you?"
            ]
        else:
            responses = [
                f"⚠️ I see you're spending ${abs(net_balance):.2f} more than you earn. Let's work on this together:\n• Review your expenses to find areas to cut\n• Look for ways to increase your income\n• Create a realistic budget you can stick to\n• Focus on needs vs. wants\n• Consider a side hustle or part-time work\n\nWhat's your biggest expense category?",
                f"⚠️ You're currently overspending by ${abs(net_balance):.2f} monthly. Here's how we can fix this:\n• Track every expense for a month\n• Identify and eliminate unnecessary spending\n• Look for ways to reduce fixed costs\n• Consider increasing your income\n• Set up automatic savings\n\nWhich expense category is taking up most of your budget?",
                f"⚠️ I notice you're spending ${abs(net_balance):.2f} more than your income. Let's turn this around:\n• Create a zero-based budget\n• Cut non-essential expenses\n• Look for cheaper alternatives\n• Consider a second job or side business\n• Focus on building an emergency fund\n\nWhat's the first expense you'd like to tackle?"
            ]
        return responses[hash(query) % len(responses)]
    
    # General financial questions
    elif any(word in query_lower for word in ["what should i do", "advice", "recommend", "suggest"]):
        responses = [
            "🤔 That's a great question! To give you the best advice, I'd love to know more about your situation. Are you looking for help with:\n• Budgeting and expense management?\n• Saving for specific goals?\n• Investment strategies?\n• Debt payoff plans?\n• Retirement planning?\n\nWhat's your biggest financial challenge right now?",
            "🤔 I'd be happy to help! To provide the most relevant advice, could you tell me:\n• What's your current financial situation?\n• What are your main financial goals?\n• What's your biggest concern or challenge?\n• What's your timeline for achieving these goals?\n\nThis will help me give you personalized recommendations!",
            "🤔 Excellent question! I'd love to help you create a plan. To give you the best guidance, I need to understand:\n• Your current income and expenses\n• Your financial goals and priorities\n• Your risk tolerance\n• Your timeline for different goals\n\nWhat's most important to you financially right now?"
        ]
        return responses[hash(query) % len(responses)]
    
    return None

def _is_valid_response(response):
    """Check if the LLM response is valid and meaningful"""
    if not response or len(response.strip()) < 20:
        return False
    
    # Check for common LLM failure patterns
    invalid_patterns = [
        "a helpful, concise response",
        "Please provide a helpful",
        "Keep it practical and actionable",
        "Answer:",
        "User question:",
        "Financial advice:",
        "hack", "brain", "mind powers", "drunk", "games", "targets",
        "ai but then", "data there was", "move on", "pain in the ass",
        "kindneuts", "comp...", "targets.", "broad term"
    ]
    
    response_lower = response.lower()
    for pattern in invalid_patterns:
        if pattern.lower() in response_lower:
            return False
    
    # Check if response has meaningful content (at least one complete sentence)
    if response.count('.') == 0 and response.count('!') == 0 and response.count('?') == 0:
        return False
    
    # Check for financial or conversational relevance
    relevant_keywords = [
        "money", "budget", "save", "invest", "debt", "income", "expense",
        "financial", "finance", "dollar", "cost", "price", "pay", "earn",
        "spend", "wealth", "retirement", "insurance", "credit", "loan",
        "you", "your", "help", "advice", "suggest", "recommend", "consider",
        "should", "could", "would", "can", "will", "may", "might"
    ]
    
    has_relevant_content = any(keyword in response_lower for keyword in relevant_keywords)
    if not has_relevant_content:
        return False
    
    # Check for repetitive text
    words = response.split()
    if len(words) > 10:
        unique_words = len(set(word.lower() for word in words))
        if unique_words < len(words) * 0.4:  # Less than 40% unique words
            return False
    
    return True

# Function to open assistant popup
def open_assistant_popup():
    def handle_query():
        user_query = assistant_entry.get().strip()
        if not user_query:
            return
            
        # Show loading indicator
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, f"You: {user_query}\n")
        chat_log.insert(tk.END, "Assistant: Thinking... 🤔\n")
        chat_log.config(state=tk.DISABLED)
        chat_log.see(tk.END)
        assistant_window.update()
        
        # Get response
        response = ai_assistant_query(user_query)
        
        # Update chat log with response
        chat_log.config(state=tk.NORMAL)
        # Remove the "Thinking..." line
        chat_log.delete(tk.END + "-2l", tk.END + "-1l")
        chat_log.insert(tk.END, f"Assistant: {response}\n\n")
        chat_log.config(state=tk.DISABLED)
        chat_log.see(tk.END)
        assistant_entry.delete(0, tk.END)

    assistant_window = tk.Toplevel(root)
    assistant_window.title("AI Assistant")

    main_frame = ttk.Frame(assistant_window)
    main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Left frame for chat log
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    ttk.Label(left_frame, text="Ask the Assistant:").pack(pady=5)

    # Chat log
    chat_log = tk.Text(left_frame, width=50, height=15, state=tk.DISABLED)
    chat_log.pack(padx=10, pady=5)

    # Entry field
    assistant_entry = ttk.Entry(left_frame, width=40)
    assistant_entry.pack(padx=10, pady=5)

    # Ask button
    ttk.Button(left_frame, text="Ask", command=handle_query).pack(pady=5)

    # Right frame for suggested queries
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side=tk.RIGHT, padx=10, fill=tk.Y)

    ttk.Label(right_frame, text="Suggestions:").pack(pady=5)

    suggestions = [
        "What is my total?",
        "Show my spending breakdown",
        "How to save money?",
        "Give me investment advice",
        "What is my current balance?",
        "How to manage debt?",
        "Budgeting tips for beginners",
        "Emergency fund advice",
        "Retirement planning tips",
        "Insurance recommendations"
    ]

    for suggestion in suggestions:
        ttk.Button(right_frame, text=suggestion, command=lambda q=suggestion: assistant_entry.insert(0, q),width=30).pack(pady=2, padx=(5, 0), anchor="w")

# Main GUI setup
root = tk.Tk()
root.title("Budget Tracker")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Entry fields
ttk.Label(frame, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
amount_entry = ttk.Entry(frame, width = 23)
amount_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
category_combobox = ttk.Combobox(frame, values=categories, width = 20)
category_combobox.set("Select an option")  # Set the placeholder text
category_combobox.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame, text="Type:").grid(row=2, column=0, padx=5, pady=5)
type_var = tk.StringVar(value="Expense")
ttk.Radiobutton(frame, text="Income", variable=type_var, value="Income").grid(row=2, column=1, padx=5, pady=5)
ttk.Radiobutton(frame, text="Expense", variable=type_var, value="Expense").grid(row=2, column=2, padx=5, pady=5)

# Buttons
ttk.Button(frame, text="Add Transaction", command=add_transaction).grid(row=3, column=0, columnspan=3, padx=5, pady=5)
ttk.Button(frame, text="Visualize Spending", command=visualize_spending).grid(row=4, column=0, columnspan=3, padx=5, pady=5)
ttk.Button(frame, text="AI Assistant", command=open_assistant_popup).grid(row=5, column=0, columnspan=3, padx=5, pady=5)

# Create the Treeview
tree = ttk.Treeview(frame, columns=("Index", "Amount", "Category", "Type"), show="headings", height=10)
tree.heading("Index", text="Index")
tree.heading("Amount", text="Amount")
tree.heading("Category", text="Category")
tree.heading("Type", text="Type")
tree.column("Index", width=50, anchor=tk.CENTER, stretch=False)  # Center-aligned
tree.column("Amount", width=100, anchor=tk.W, stretch=False)    # Left-aligned
tree.column("Category", width=150, anchor=tk.W, stretch=False)  # Left-aligned
tree.column("Type", width=100, anchor=tk.W, stretch=False)      # Left-aligned
tree.grid(row=6, column=0, columnspan=3, pady=10)
setup_treeview_context_menu()


# Total labels
total_income_label = ttk.Label(frame, text="Total Income: $0.00")
total_income_label.grid(row=7, column=0, padx=5, pady=5)
total_expense_label = ttk.Label(frame, text="Total Expense: $0.00")
total_expense_label.grid(row=7, column=1, padx=5, pady=5)
total_amount_label = ttk.Label(frame, text="Overall Total: $0.00")
total_amount_label.grid(row=7, column=2, padx=5, pady=5)

# Add Category section
ttk.Label(frame, text="Add New Category:").grid(row=8, column=0, padx=5, pady=5)
new_category_entry = ttk.Entry(frame)
new_category_entry.grid(row=8, column=1, padx=5, pady=5)
ttk.Button(frame, text="Add Category", command=add_category).grid(row=8, column=2, padx=5, pady=5)

# Initialize data display
update_treeview()  # Ensure data is displayed on startup
update_totals()  # Ensure totals are updated on startup

# Start the main application loop
root.mainloop()
