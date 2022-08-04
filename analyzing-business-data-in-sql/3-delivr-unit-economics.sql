-- Unit Economics

-- Average Revenue Per User (ARPU)
WITH kpi AS (
  SELECT
    -- Select the user ID and calculate revenue
    o.user_id
    ,SUM(m.meal_price * o.order_quantity) AS revenue
  FROM meals AS m
  JOIN orders AS o ON m.meal_id = o.meal_id
  GROUP BY o.user_id
)
-- Calculate ARPU
SELECT ROUND(AVG(revenue) :: NUMERIC, 2) AS arpu
FROM kpi;
----------------------------------------------------------

-- ARPU per week
WITH kpi AS (
  SELECT
    -- Select the week, revenue, and count of users
    DATE_TRUNC('week', o.order_date) :: DATE AS delivr_week
    ,SUM(o.order_quantity * m.meal_price) AS revenue
    ,COUNT(DISTINCT o.user_id) AS users
  FROM meals AS m
  JOIN orders AS o ON m.meal_id = o.meal_id
  GROUP BY delivr_week
)
SELECT
    delivr_week
    -- Calculate ARPU
    ,ROUND(revenue :: NUMERIC / GREATEST(users, 1), 2) AS arpu
FROM kpi
ORDER BY delivr_week ASC;
----------------------------------------------------------

-- Average Orders per user
WITH kpi AS (
  SELECT
    -- Select the count of orders and users
    COUNT(DISTINCT order_id) AS orders
    ,COUNT(DISTINCT user_id) AS users
  FROM orders
)
SELECT
  -- Calculate the average orders per user
  ROUND(orders / GREATEST(users, 1) :: NUMERIC, 2) AS arpu
FROM kpi;
----------------------------------------------------------

-- HISTOGRAMS

-- Revenue Histogram Data
WITH user_revenues AS (
  SELECT
    -- Select the user ID and revenue
    o.user_id
    ,SUM(o.order_quantity * m.meal_price) AS revenue
  FROM meals AS m
  JOIN orders AS o ON m.meal_id = o.meal_id
  GROUP BY user_id
)
SELECT
  -- Return the frequency table of revenues by user
  ROUND(revenue :: NUMERIC, -2) AS revenue_100
  ,COUNT(DISTINCT user_id) AS users
FROM user_revenues
GROUP BY revenue_100
ORDER BY revenue_100 ASC;
----------------------------------------------------------

-- Orders Histogram Data
WITH user_orders AS (
  SELECT
    user_id
    ,COUNT(DISTINCT order_id) AS orders
  FROM orders
  GROUP BY user_id
)
SELECT
  -- Return the frequency table of orders by user
  orders
  ,COUNT(DISTINCT user_id) AS users
FROM user_orders
GROUP BY orders
ORDER BY orders ASC;
----------------------------------------------------------

-- BUCKETS FOR BAR GRAPHS

-- Bucketting users by revenue
WITH user_revenues AS (
  SELECT
    -- Select the user IDs and the revenues they generate
    o.user_id
    ,SUM(o.order_quantity * m.meal_price) AS revenue
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
  ,COUNT(DISTINCT user_id) AS users
FROM user_revenues
GROUP BY revenue_group;
----------------------------------------------------------

-- Bucketting users by order count
WITH user_orders AS (
-- Store each user's count of orders in a CTE named user_orders
  SELECT
    user_id
    ,COUNT(DISTINCT order_id) AS orders
  FROM orders
  GROUP BY user_id
)
SELECT
  -- Write the conditions for the three buckets
  CASE
    WHEN orders < 8 THEN 'Low-orders users'
    WHEN orders < 15 THEN 'Mid-orders users'
    ELSE 'High-orders users'
  END AS order_group
  -- Count the distinct users in each bucket
  ,COUNT(DISTINCT user_id) AS users
FROM user_orders
GROUP BY order_group;
----------------------------------------------------------

-- PERCENTILES

-- Revenue quartiles and mean
WITH user_revenues AS (
  -- Select the user IDs and their revenues
  SELECT
    o.user_id
    ,SUM(o.order_quantity * m.meal_price) AS revenue
  FROM meals AS m
  JOIN orders AS o ON m.meal_id = o.meal_id
  GROUP BY user_id
)
SELECT
  -- Calculate the first, second, and third quartile
  ROUND(
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue) :: NUMERIC,
  2) AS revenue_p25
  ,ROUND(
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY revenue) :: NUMERIC,
  2) AS revenue_p50
  ,ROUND(
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue) :: NUMERIC,
  2) AS revenue_p75
  -- Calculate the average
  ,ROUND(AVG(revenue) :: NUMERIC, 2) AS avg_revenue
FROM user_revenues;
----------------------------------------------------------

-- IQR number users by revenue
WITH user_revenues AS (
  SELECT
    -- Select user_id and calculate revenue by user
    user_id
    ,SUM(m.meal_price * o.order_quantity) AS revenue
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
    2) AS revenue_p25
    ,ROUND(
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
----------------------------------------------------------
