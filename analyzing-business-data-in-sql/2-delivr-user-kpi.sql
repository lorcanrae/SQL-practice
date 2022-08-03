-- USER REGISTRATIONS

-- User registration dates
SELECT
-- Get the earliest (minimum) order date by user ID
  user_id
  ,MIN(order_date) AS reg_date
FROM orders
GROUP BY user_id
-- Order by user ID
ORDER BY user_id ASC;
----------------------------------------------------------

-- Registrations by month
WITH reg_dates AS (
  SELECT user_id
    ,MIN(order_date) AS reg_date
  FROM orders
  GROUP BY user_id
)
SELECT
-- Count the unique user IDs by registration month
  DATE_TRUNC('month', reg_date) :: DATE AS delivr_month
  ,COUNT(user_id) AS regs
FROM reg_dates
GROUP BY delivr_month
ORDER BY delivr_month ASC;
----------------------------------------------------------

-- Monthly Active Users (MAU)
SELECT
  -- Truncate the order date to the nearest month
  DATE_TRUNC('month', order_date) :: DATE AS delivr_month
  -- Count the unique user IDs
  ,COUNT(DISTINCT user_id) AS mau
FROM orders
GROUP BY delivr_month
ORDER BY delivr_month ASC;

-- User Registrations per Month
WITH reg_dates AS (
  SELECT
    user_id
    ,MIN(order_date) AS reg_date
  FROM orders
  GROUP BY user_id
)
SELECT
  -- Select the month and the registrations
  DATE_TRUNC('month', reg_date) :: DATE AS delivr_month
  ,COUNT(user_id) AS regs
FROM reg_dates
GROUP BY delivr_month
ORDER BY delivr_month;
----------------------------------------------------------

-- Registrations Running Total
WITH reg_dates AS (
  SELECT user_id
    ,MIN(order_date) AS reg_date
  FROM orders
  GROUP BY user_id
),
regs AS (
  SELECT
    DATE_TRUNC('month', reg_date) :: DATE AS delivr_month
    ,COUNT(DISTINCT user_id) AS regs
  FROM reg_dates
  GROUP BY delivr_month
)
SELECT
    -- Calculate the registrations running total by month
  delivr_month
  ,SUM(regs) OVER (ORDER BY delivr_month) AS regs_rt
FROM regs
ORDER BY delivr_month ASC;
----------------------------------------------------------

-- Month, MAU, MAU-1
WITH mau AS (
  SELECT
    DATE_TRUNC('month', order_date) :: DATE AS delivr_month
    ,COUNT(DISTINCT user_id) AS mau
  FROM orders
  GROUP BY delivr_month
)
SELECT
  delivr_month
  ,mau
  ,COALESCE(
    LAG(mau) OVER (ORDER BY delivr_month), 0
  ) AS last_mau
FROM mau
ORDER BY delivr_month ASC;
----------------------------------------------------------

-- MAU Month on Month Delta and Growth Rate
WITH mau AS (
  SELECT
    DATE_TRUNC('month', order_date) :: DATE AS delivr_month
    ,COUNT(DISTINCT user_id) AS mau
  FROM orders
  GROUP BY delivr_month
),
mau_with_lag AS (
  SELECT
    delivr_month
    ,mau
    ,GREATEST(
      LAG(mau) OVER (ORDER BY delivr_month ASC), 1
    ) AS last_mau
  FROM mau
)
SELECT
  -- Calculate the MoM MAU delta and growth rates
  delivr_month
  ,(mau - last_mau) AS delta
  ,ROUND(
    (mau - last_mau) / last_mau :: NUMERIC,
  2) AS growth
FROM mau_with_lag
-- Order by month in ascending order
ORDER BY delivr_month;
----------------------------------------------------------

-- Orders Month on Month Delta and Growth Rate
WITH orders AS (
  SELECT
    DATE_TRUNC('month', order_date) :: DATE AS delivr_month
    --  Count the unique order IDs
    ,COUNT(DISTINCT order_id) AS orders
  FROM orders
  GROUP BY delivr_month
),
orders_with_lag AS (
  SELECT
    delivr_month
    -- Fetch each month's current and previous orders
    ,orders
    ,COALESCE(
      LAG(orders) OVER(ORDER BY delivr_month),
    1) AS last_orders
  FROM orders
)
SELECT
  delivr_month
  ,(orders - last_orders) AS delta
  -- Calculate the MoM order growth rate
  ,ROUND(
    (orders - last_orders) / last_orders :: NUMERIC,
  2) AS growth
FROM orders_with_lag
ORDER BY delivr_month ASC;
----------------------------------------------------------

-- Retention Rates
WITH user_monthly_activity AS (
  SELECT
    DISTINCT DATE_TRUNC('month', order_date) :: DATE AS delivr_month
    ,user_id
  FROM orders
)
SELECT
    -- Calculate the MoM retention rates
    previous.delivr_month
    ,ROUND(
        COUNT(DISTINCT current.user_id) /
        GREATEST(COUNT(DISTINCT previous.user_id)) :: NUMERIC,
    2) AS retention_rate
FROM user_monthly_activity AS previous
LEFT JOIN user_monthly_activity AS current
-- Fill in the user and month join conditions
ON previous.user_id = current.user_id
AND previous.delivr_month = (current.delivr_month - INTERVAL '1 month')
GROUP BY previous.delivr_month
ORDER BY previous.delivr_month ASC;
----------------------------------------------------------
