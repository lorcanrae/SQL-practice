import sqlite3

def order_rank_per_customer(db):

    query = """
SELECT o.OrderID
		,o.CustomerID
		,o.OrderDate
		,RANK() OVER (
		PARTITION BY o.CustomerID
		ORDER BY o.OrderDate
		)
FROM Orders o
    """
    db.execute(query)
    rows = db.fetchall()
    return rows

def order_cumulative_amount_per_customer(db):

    query = """
SELECT o.OrderID
		,o.CustomerID
		,o.OrderDate
		,SUM(SUM(od.UnitPrice * od.Quantity)) OVER (
		PARTITION BY o.CustomerID
		ORDER BY o.OrderDate
		) AS cum_sum
FROM Orders o
JOIN OrderDetails od ON o.OrderID = od.OrderID
GROUP BY o.OrderID
    """
    db.execute(query)
    rows = db.fetchall()
    return rows

if __name__ == '__main__':
    conn = sqlite3.connect('data/ecommerce.sqlite')
    db = conn.cursor()
    order_cumulative_amount_per_customer(db)
