import sqlite3

# Revenue
def total_per_user_id(db, user_id):
    '''Total spent per user_id'''
    query = '''
SELECT SUM(meals.meal_price * orders.order_quantity) AS revenue
FROM meals
JOIN orders ON meals.meal_id = orders.meal_id
-- Keep only the records of customer ID 15
WHERE orders.user_id = ?;
    '''
    db.execute(query,(user_id,))
    rows = db.fetchall()
    return rows[0]

def revenue_per_week(db):
    '''Get the revenue per week for each week in June
    and check whether there's any consistent growth in revenue.'''
    query = '''
SELECT DATE_TRUNC('week', order_date) :: DATE AS delivr_week,
    -- Calculate revenue
    SUM(m.meal_price * o.order_quantity) AS revenue
FROM meals m
JOIN orders o ON m.meal_id = o.meal_id
-- Keep only the records in June 2018
WHERE o.order_date BETWEEN '2018-06-01' AND '2018-07-01'
GROUP BY delivr_week
ORDER BY delivr_week ASC;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows


# Cost and Common Table Expressions (CTE)

def total_cost(db):
    '''Total cost to business'''
    query = '''
SELECT SUM(m.meal_cost * s.stocked_quantity)
FROM stock s
JOIN meals m ON m.meal_id = s.meal_id
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows[0][0]

def top_five_meals_by_cost(db):
    '''Returns top five meals by cost to the company'''
    query = '''
SELECT m.meal_id
    ,SUM(s.stocked_quantity * m.meal_cost) AS cost
FROM meals m
JOIN stock s ON m.meal_id = s.meal_id
GROUP BY m.meal_id
ORDER BY cost DESC
LIMIT 5;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows

def avg_cost_per_month(db):
    '''Returns average cost per month to the company before September 2018'''
    query = '''
WITH cost_per_month as(
SELECT
    DATE_TRUNC('month', s.stocking_date)::DATE AS delivr_month
    ,SUM(m.meal_cost * s.stocked_quantity) AS cost
FROM meals m
JOIN stock s ON m.meal_id = s.meal_id
GROUP BY delivr_month
ORDER BY delivr_month ASC
)
SELECT AVG(cpm.cost)
FROM cost_per_month cpm
WHERE cpm.delivr_month < '2018-09-01'
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows[0]

def profit_per_eatery(db):
    '''Revenue per eatery'''
    query = '''
WITH revenue AS (
    -- Calculate revenue per eatery
    SELECT m.eatery
        ,SUM(m.meal_price * o.order_quantity) AS revenue
    FROM meals m
    JOIN orders o ON m.meal_id = o.meal_id
    GROUP BY eatery
),
cost AS (
    -- Calculate cost per eatery
    SELECT m.eatery
        ,SUM(m.meal_cost * s.stocked_quantity) AS cost
    FROM meals m
    JOIN stock s ON m.meal_id = s.meal_id
    GROUP BY eatery
)
-- Calculate profit per eatery
SELECT r.eatery,
    (r.revenue - c.cost) AS profit
FROM revenue r
JOIN cost c ON r.eatery = c.eatery
ORDER BY profit DESC;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows

def profit_per_month(db):
    '''Returns profit per month'''
    query = '''
WITH revenue AS (
-- Revenue CTE
    SELECT
    DATE_TRUNC('month', order_date) :: DATE AS delivr_month,
    SUM(m.meal_price * o.order_quantity) AS revenue
    FROM meals m
    JOIN orders o ON m.meal_id = o.meal_id
    GROUP BY delivr_month
),
cost AS (
-- Cost CTE
    SELECT
    DATE_TRUNC('month', stocking_date) :: DATE AS delivr_month,
    SUM(s.stocked_quantity * m.meal_cost) AS cost
    FROM meals m
    JOIN stock s ON m.meal_id = s.meal_id
    GROUP BY delivr_month
)
-- Calculate profit by joining the CTEs
SELECT r.delivr_month
    ,(r.revenue - c.cost) AS profit
FROM revenue r
JOIN cost c ON c.delivr_month = r.delivr_month
ORDER BY r.delivr_month ASC;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows

def placeholder(db):
    '''placeholder'''
    query = '''

    '''
    db.execute(query)
    rows = db.fetchall()
    return rows


def placeholder(db):
    '''placeholder'''
    query = '''

    '''
    db.execute(query)
    rows = db.fetchall()
    return rows
