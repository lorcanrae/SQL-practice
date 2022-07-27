import sqlite3

def get_average_purchase(db):
    # return the average amount spent per order for each customer
    # ordered by customer ID
    query = """
WITH cust_data AS (
		SELECT od.OrderID
			, SUM(od.UnitPrice * od.Quantity) as order_amount
		FROM OrderDetails od
		GROUP BY od.OrderID
)
SELECT o.CustomerID
	,ROUND(AVG(cust_data.order_amount), 2)
FROM cust_data
JOIN Orders o ON o.OrderID = cust_data.OrderID
GROUP BY o.CustomerID
    """
    db.execute(query)
    rows = db.fetchall()
    return rows

def get_general_avg_order(db):
    # return the average amount spent per order
    query = """
WITH cust_data AS (
    SELECT od.OrderID
        , SUM(od.UnitPrice * od.Quantity) as order_amount
    FROM OrderDetails od
    GROUP BY od.OrderID
)
SELECT ROUND(AVG(cust_data.order_amount), 2) AS avg_per_cust
FROM cust_data
    """
    db.execute(query)
    rows = db.fetchall()
    return rows[0][0]

def best_customers(db):
    # return the customers who have an average purchase greater than the
    # general average purchase
    query = """
WITH OrderValues AS (
	SELECT od.OrderID
			, SUM(od.UnitPrice * od.Quantity) as order_amount
	FROM OrderDetails od
	GROUP BY od.OrderID
)
, GeneralOrderValue AS (
	SELECT ROUND(AVG(ov.order_amount), 2) AS average
	FROM OrderValues ov
)
, CustomerOrderValue AS (
	SELECT c.CustomerID
		,ROUND(AVG(ov.order_amount), 2) AS average
	FROM Customers c
	JOIN Orders o ON c.CustomerID = o.CustomerID
	JOIN OrderValues ov ON ov.OrderID = o.OrderID
	GROUP BY c.CustomerID
	ORDER BY c.CustomerID
)
SELECT
	cov.CustomerID
	, cov.average
FROM CustomerOrderValue cov
WHERE cov.average > (SELECT average FROM GeneralOrderValue)
GROUP BY cov.average
ORDER BY cov.average DESC
    """
    return db.execute(query).fetchall()

def top_ordered_product_per_customer(db):
    # return the list of the top ordered product by each customer based on the
    # total ordered amount in USD
    query = """
WITH OrderedProducts AS (
SELECT
    o.CustomerID
    , od.ProductID
    , SUM(od.UnitPrice * od.Quantity) AS ProductValue
FROM Orders o
JOIN OrderDetails od ON o.OrderID = od.OrderID
GROUP BY o.CustomerID, od.ProductID
)
SELECT
	op.CustomerID
	, op.ProductID
	, MAX (op.ProductValue) as MaxSpent
FROM OrderedProducts op
GROUP BY op.CustomerID
ORDER BY MaxSpent DESC
    """
    return db.execute(query).fetchall()

def average_number_of_days_between_orders(db):
    # return the average number of days between two consecutive
    # orders of the same customer
    query = """
WITH DatedOrders AS (
	SELECT
		o.CustomerID
		, o.OrderID
		, o.OrderDate
		, LAG(o.OrderDate, 1, 0) OVER(
			PARTITION BY o.CustomerID
			ORDER BY o.OrderDate
			) AS PreviousOrderDate
	FROM Orders o
)
SELECT ROUND(AVG(JULIANDAY(do.OrderDate) - JULIANDAY(do.PreviousOrderDate)))
FROM DatedOrders do
WHERE do.PreviousOrderDate <> 0
    """
    return int(db.execute(query).fetchall()[0][0])

if __name__ == '__main__':
    conn = sqlite3.connect('data/ecommerce.sqlite')
    db = conn.cursor()
    average_number_of_days_between_orders(db)
