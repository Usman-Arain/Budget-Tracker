import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
import os

# File to store data
DATA_FILE = "budget_history.csv"

# Load previous data if file exists
if os.path.exists(DATA_FILE):
    budget_data = pd.read_csv(DATA_FILE)
  
else:
    budget_data = pd.DataFrame(columns=["Amount", "Category", "Type"])

# List of categories
categories = ["Groceries", "Utilities", "Rent", "Entertainment", "Salary", "Freelance"]

# Function to save data
def save_data():
    budget_data.to_csv(DATA_FILE, index=False)

# Function to add a transaction
def add_transaction():
    global budget_data
    amount = amount_entry.get()
    category = category_combobox.get()
    t_type = type_var.get()

    if amount and category and t_type:
        try:
            amount = float(amount)
            new_transaction = pd.DataFrame({"Amount": [amount], "Category": [category], "Type": [t_type]})
            budget_data = pd.concat([budget_data, new_transaction], ignore_index=True)
            update_treeview()
            update_totals()
            save_data()  # Save to file
            amount_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount.")
    else:
        messagebox.showerror("Missing Information", "Please fill out all fields.")

# Function to add a new category
def add_category():
    new_category = new_category_entry.get()
    if new_category and new_category not in categories:
        categories.append(new_category)
        category_combobox['values'] = categories
        new_category_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Invalid Category", "Please enter a valid, unique category.")

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
    expense_data = budget_data[budget_data["Type"] == "Expense"]
    expense_summary = expense_data.groupby("Category").sum()
    
    # Plotting a pie chart for expenses
    plt.figure(figsize=(8, 6))
    plt.pie(expense_summary["Amount"], labels=expense_summary.index, autopct='%1.1f%%')
    plt.title("Expenses by Category")
    plt.show()
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
            item_index = int(tree.item(selected_item)["values"][0])  # Get the original index stored in the last column
            budget_data.at[item_index, "Amount"] = new_amount
            budget_data.at[item_index, "Category"] = new_category
            budget_data.at[item_index, "Type"] = new_type
            update_treeview()
            update_totals()
            save_data()  # Save changes
            edit_window.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount.")

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
        item_index = int(tree.item(selected_item)["values"][0])  # Get the original index stored in the last column
        global budget_data
        budget_data = budget_data.drop(index=item_index).reset_index(drop=True)
        update_treeview()
        update_totals()
        save_data()

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

# Function to handle AI assistant queries (advanced rule-based AI)
def ai_assistant_query(query):
    query = query.lower()
    response = "I didn't understand that. Try asking about totals, categories, or adding a transaction."

    if "total" in query:
        total_expense = budget_data[budget_data["Type"] == "Expense"]["Amount"].sum()
        total_income = budget_data[budget_data["Type"] == "Income"]["Amount"].sum()
        response = f"Your total income is ${total_income:.2f} and total expenses are ${total_expense:.2f}."
    elif "category" in query:
        response = f"The available categories are: {', '.join(categories)}."
    elif "add transaction" in query:
        response = "You can add a transaction by filling in the amount, selecting a category, choosing the type (Income or Expense), and clicking 'Add Transaction'."
    elif "spending summary" in query:
        expense_data = budget_data[budget_data["Type"] == "Expense"]
        if not expense_data.empty:
            max_category = expense_data.groupby("Category")["Amount"].sum().idxmax()
            response = f"You are spending the most on {max_category}. Consider reviewing this category."
        else:
            response = "No expense data available to analyze."
    elif "daily balance" in query:
        total_expense = budget_data[budget_data["Type"] == "Expense"]["Amount"].sum()
        total_income = budget_data[budget_data["Type"] == "Income"]["Amount"].sum()
        days_in_month = 30  # Assuming a standard month
        daily_balance = (total_income - total_expense) / days_in_month
        response = f"Your per-day balance for the month is approximately ${daily_balance:.2f}."
    elif "monthly breakdown" in query:
        expense_data = budget_data[budget_data["Type"] == "Expense"]
        if not expense_data.empty:
            breakdown = expense_data.groupby("Category")["Amount"].sum().to_dict()
            response = "Monthly breakdown:\n" + "\n".join([f"{cat}: ${amt:.2f}" for cat, amt in breakdown.items()])
        else:
            response = "No expense data available for a breakdown."
    elif "savings suggestion" in query:
        total_income = budget_data[budget_data["Type"] == "Income"]["Amount"].sum()
        total_expense = budget_data[budget_data["Type"] == "Expense"]["Amount"].sum()
        savings = total_income - total_expense
        if savings > 0:
            response = f"You are saving ${savings:.2f}. Great job! Consider investing or saving for future goals."
        else:
            response = "You are spending more than you earn. Consider cutting down on non-essential expenses."

    return response

# Function to open assistant popup
def open_assistant_popup():
    def handle_query():
        user_query = assistant_entry.get()
        response = ai_assistant_query(user_query)
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, f"You: {user_query}\n")
        chat_log.insert(tk.END, f"Assistant: {response}\n\n")
        chat_log.config(state=tk.DISABLED)
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
        "Show categories",
        "How to add a transaction?",
        "What is my spending summary?",
        "What is my daily balance?",
        "What is my monthly breakdown?",
        "Give me savings suggestions."
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
tree.grid(row=4, column=0, columnspan=3, pady=10)
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

# Load previous data if file exists
if os.path.exists(DATA_FILE):
    budget_data = pd.read_csv(DATA_FILE)
    update_treeview()  # Ensure data is displayed on startup
    update_totals()  # Ensure totals are updated on startup
else:
    budget_data = pd.DataFrame(columns=["Amount", "Category", "Type"])

# Start the main application loop
root.mainloop()
