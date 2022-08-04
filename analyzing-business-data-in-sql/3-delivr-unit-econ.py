import sqlite3


## Unit Economics

def avg_revenue_per_user(db):
    '''Returns average revenue per user from inception as an absolute number'''
    query = '''
-- Create a CTE named kpi
WITH kpi AS (
    SELECT
        -- Select the user ID and calculate revenue
        o.user_id,
        SUM(m.meal_price * o.order_quantity) AS revenue
    FROM meals AS m
    JOIN orders AS o ON m.meal_id = o.meal_id
    GROUP BY o.user_id
)
-- Calculate ARPU
SELECT ROUND(AVG(revenue) :: NUMERIC, 2) AS arpu
FROM kpi;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows

def arpu_per_week(db):
    '''Return ARPU per week'''
    query = '''
WITH kpi AS (
    SELECT
        -- Select the week, revenue, and count of users
        DATE_TRUNC('week', o.order_date) :: DATE AS delivr_week,
        SUM(o.order_quantity * m.meal_price) AS revenue,
        COUNT(DISTINCT o.user_id) AS users
    FROM meals AS m
    JOIN orders AS o ON m.meal_id = o.meal_id
    GROUP BY delivr_week
)
SELECT
    delivr_week,
    -- Calculate ARPU
    ROUND(revenue :: NUMERIC / GREATEST(users, 1), 2) AS arpu
FROM kpi
ORDER BY delivr_week ASC;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows

def avg_orders_per_user(db):
    '''Returns average orders per user since inception'''
    query = '''
WITH kpi AS (
  SELECT
    -- Select the count of orders and users
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT user_id) AS users
  FROM orders
)
SELECT
  -- Calculate the average orders per user
  ROUND(
    orders / GREATEST(users, 1) :: NUMERIC, 2) AS arpu
FROM kpi;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows


## Histograms

def revenue_hist(db):
    '''Return frequency table of revenue per user'''
    query = '''
WITH user_revenues AS (
  SELECT
    -- Select the user ID and revenue
    o.user_id,
    SUM(o.order_quantity * m.meal_price) AS revenue
  FROM meals AS m
  JOIN orders AS o ON m.meal_id = o.meal_id
  GROUP BY user_id
)
SELECT
  -- Return the frequency table of revenues by user
  ROUND(revenue :: NUMERIC, -2) AS revenue_100,
  COUNT(DISTINCT user_id) AS users
FROM user_revenues
GROUP BY revenue_100
ORDER BY revenue_100 ASC;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows

def orders_hist(db):
    '''Return frequency table of orders per user'''
    query = '''
WITH user_orders AS (
  SELECT
    user_id,
    COUNT(DISTINCT order_id) AS orders
  FROM orders
  GROUP BY user_id
)
SELECT
  -- Return the frequency table of orders by user
  orders,
  COUNT(DISTINCT user_id) AS users
FROM user_orders
GROUP BY orders
ORDER BY orders ASC;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows


## Buckets

def bucketing_users_by_revenue(db):
    '''Returns table of low, medium, high revenue users'''
    query = '''
WITH user_revenues AS (
    SELECT
        -- Select the user IDs and the revenues they generate
        o.user_id,
        SUM(o.order_quantity * m.meal_price) AS revenue
    FROM meals AS m
    JOIN orders AS o ON m.meal_id = o.meal_id
    GROUP BY user_id
)
SELECT
    -- Fill in the bucketing conditions
    CASE
        WHEN revenue < 150 THEN 'Low-revenue users'
        WHEN revenue < 300 THEN 'Mid-revenue users'
        ELSE 'High-revenue users'
    END AS revenue_group,
    COUNT(DISTINCT user_id) AS users
FROM user_revenues
GROUP BY revenue_group;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows

def bucket_users_by_order(db):
    '''Returns a table of low, medium, high users by # orders'''
    query = '''
-- Store each user's count of orders in a CTE named user_orders
WITH user_orders AS (
  SELECT
    user_id,
    COUNT(DISTINCT order_id) AS orders
  FROM orders
  GROUP BY user_id
)
SELECT
  -- Write the conditions for the three buckets
  CASE
    WHEN orders < 8 THEN 'Low-orders users'
    WHEN orders < 15 THEN 'Mid-orders users'
    ELSE 'High-orders users'
  END AS order_group,
  -- Count the distinct users in each bucket
  COUNT(DISTINCT user_id) AS users
FROM user_orders
GROUP BY order_group;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows


## Percentiles

def revenue_quartiles(db):
    '''Return first, second, third quartiles and mean for revenue'''
    query = '''
WITH user_revenues AS (
  -- Select the user IDs and their revenues
  SELECT
    o.user_id,
    SUM(o.order_quantity * m.meal_price) AS revenue
  FROM meals AS m
  JOIN orders AS o ON m.meal_id = o.meal_id
  GROUP BY user_id
)
SELECT
  -- Calculate the first, second, and third quartile
  ROUND(
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue) :: NUMERIC,
  2) AS revenue_p25,
  ROUND(
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY revenue) :: NUMERIC,
  2) AS revenue_p50,
  ROUND(
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue) :: NUMERIC,
  2) AS revenue_p75,
  -- Calculate the average
  ROUND(AVG(revenue) :: NUMERIC, 2) AS avg_revenue
FROM user_revenues;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows

def iqr_users_by_revenue(db):
    '''return absolute number of users within the IQR by revenue generated'''
    query = '''
WITH user_revenues AS (
  SELECT
    -- Select user_id and calculate revenue by user
    user_id,
    SUM(m.meal_price * o.order_quantity) AS revenue
  FROM meals AS m
  JOIN orders AS o ON m.meal_id = o.meal_id
  GROUP BY user_id
),
quartiles AS (
  SELECT
    -- Calculate the first and third revenue quartiles
    ROUND(
      PERCENTILE_CONT(0.25) WITHIN GROUP
      (ORDER BY revenue ASC) :: NUMERIC,
    2) AS revenue_p25,
    ROUND(
      PERCENTILE_CONT(0.75) WITHIN GROUP
      (ORDER BY revenue ASC) :: NUMERIC,
    2) AS revenue_p75
  FROM user_revenues
)
SELECT
  -- Count the number of users in the IQR
  COUNT(DISTINCT user_id) AS users
FROM user_revenues
CROSS JOIN quartiles
-- Only keep users with revenues in the IQR range
WHERE revenue :: NUMERIC >= revenue_p25
  AND revenue :: NUMERIC <= revenue_p75;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows



