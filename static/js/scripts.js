// app.js
document.getElementById('expense-form').addEventListener('submit', function(event) {
    event.preventDefault();
  
    const expenseName = document.getElementById('expense-name').value;
    const expenseAmount = parseFloat(document.getElementById('expense-amount').value);
    const expenseCategory = document.getElementById('expense-category').value;
  
    if (expenseName && expenseAmount > 0) {
      // Save expense to local storage (or backend later)
      let expenses = JSON.parse(localStorage.getItem('expenses')) || [];
      expenses.push({ name: expenseName, amount: expenseAmount, category: expenseCategory });
      localStorage.setItem('expenses', JSON.stringify(expenses));
  
      // Update the dashboard with new expenses
      displayExpenses();
  
      // Reset form
      document.getElementById('expense-form').reset();
    }
  });
  
  function displayExpenses() {
    const expenses = JSON.parse(localStorage.getItem('expenses')) || [];
    const summary = document.getElementById('expense-summary');
    summary.innerHTML = '<h3>Expense Summary</h3>';
  
    if (expenses.length === 0) {
      summary.innerHTML += '<p>No expenses recorded yet.</p>';
      return;
    }
  
    let total = 0;
    expenses.forEach(expense => {
      total += expense.amount;
      summary.innerHTML += `<p>${expense.name} - $${expense.amount} (${expense.category})</p>`;
    });
  
    summary.innerHTML += `<h3>Total: $${total}</h3>`;
  }
  
  // Initial display
  displayExpenses();