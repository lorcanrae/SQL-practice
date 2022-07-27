import sqlite3

def detailed_orders(db):
    '''return a list of all orders (order_id, customer.contact_name,
    employee.firstname) ordered by order_id'''
    query = """
    SELECT o.OrderID , c.ContactName , e.FirstName
FROM Orders o
JOIN Customers c ON o.CustomerID = c.CustomerID
JOIN Employees e ON o.EmployeeID = e.EmployeeID
    """
    db.execute(query)
    rows = db.fetchall()
    return rows

def spent_per_customer(db):
    '''return the total amount spent per customer ordered by ascending total
    amount (to 2 decimal places)'''
    query = """
SELECT c.ContactName, ROUND(SUM(od.UnitPrice * od.Quantity), 2) AS total_spent
FROM Orders o
JOIN OrderDetails od ON o.OrderID = od.OrderID
JOIN Customers c ON o.CustomerID = c.CustomerID
GROUP BY c.ContactName
ORDER BY total_spent
    """
    db.execute(query)
    rows = db.fetchall()
    return rows

def best_employee(db):
    '''Implement the best_employee method to determine who is the best employee!
    By “best employee”, we mean the one who sells the most.
    We expect the function to return a tuple like:
    ('FirstName', 'LastName', 6000 (the sum of all purchase)).'''
    query = """
SELECT e.FirstName, e.LastName, SUM(od.UnitPrice * od.Quantity) AS total_sales
FROM Orders o
JOIN OrderDetails od ON o.OrderID = od.OrderID
JOIN Employees e ON o.EmployeeID = e.EmployeeID
GROUP BY o.EmployeeID
ORDER BY total_sales DESC
    """
    db.execute(query)
    rows = db.fetchall()
    return rows[0]

def orders_per_customer(db):
    '''Return a list of tuples where each tupel contains the contactName
    of the customer and the number of orders they made (contactName,
    number_of_orders). Order the list by ascending number of orders'''

    query = """
SELECT c.ContactName
		, COALESCE(COUNT(o.CustomerID), 0) AS orders_num
FROM Customers c
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
GROUP BY c.ContactName
ORDER BY orders_num
    """
    db.execute(query)
    rows = db.fetchall()
    return rows

if __name__ == '__main__':
    conn = sqlite3.connect('data/ecommerce.sqlite')
    db = conn.cursor()
    orders_per_customer(db)
