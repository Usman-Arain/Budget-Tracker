import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt

# Initialize an empty DataFrame
budget_data = pd.DataFrame(columns=["Amount", "Category", "Type"])

# List of categories
categories = ["Groceries", "Utilities", "Rent", "Entertainment", "Salary", "Freelance"]

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
        tree.insert("", tk.END, values=(row["Amount"], row["Category"], row["Type"]))

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

# Main GUI setup
root = tk.Tk()
root.title("Budget Tracker")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Entry fields
ttk.Label(frame, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
amount_entry = ttk.Entry(frame)
amount_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
category_combobox = ttk.Combobox(frame, values=categories)
category_combobox.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame, text="Type:").grid(row=2, column=0, padx=5, pady=5)
type_var = tk.StringVar(value="Expense")
ttk.Radiobutton(frame, text="Income", variable=type_var, value="Income").grid(row=2, column=1, padx=5, pady=5)
ttk.Radiobutton(frame, text="Expense", variable=type_var, value="Expense").grid(row=2, column=2, padx=5, pady=5)

# Buttons
ttk.Button(frame, text="Add Transaction", command=add_transaction).grid(row=3, column=0, columnspan=3, padx=5, pady=5)
ttk.Button(frame, text="Visualize Spending", command=visualize_spending).grid(row=4, column=0, columnspan=3, padx=5, pady=5)

# Treeview for displaying the budget data
tree = ttk.Treeview(frame, columns=("Amount", "Category", "Type"), show="headings")
tree.heading("Amount", text="Amount")
tree.heading("Category", text="Category")
tree.heading("Type", text="Type")
tree.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

# Labels for totals
total_expense_label = ttk.Label(frame, text="Total Expense: $0.00")
total_expense_label.grid(row=6, column=0, columnspan=1, padx=5, pady=5)

total_income_label = ttk.Label(frame, text="Total Income: $0.00")
total_income_label.grid(row=6, column=1, columnspan=1, padx=5, pady=5)

total_amount_label = ttk.Label(frame, text="Overall Total: $0.00")
total_amount_label.grid(row=6, column=2, columnspan=1, padx=5, pady=5)

# Entry for new category
ttk.Label(frame, text="New Category:").grid(row=7, column=0, padx=5, pady=5)
new_category_entry = ttk.Entry(frame)
new_category_entry.grid(row=7, column=1, padx=5, pady=5)
ttk.Button(frame, text="Add Category", command=add_category).grid(row=7, column=2, padx=5, pady=5)

root.mainloop()
