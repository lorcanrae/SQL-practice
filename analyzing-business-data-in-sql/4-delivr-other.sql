-- Formatting

-- Format Date
SELECT DISTINCT
  -- Select the order date
  order_date
  -- Format the order date
  ,TO_CHAR(order_date, 'FMDay DD, FMMonth YYYY') AS format_order_date
FROM orders
ORDER BY order_date ASC
LIMIT 3;
----------------------------------------------------------

-- Rank users by count of orders
WITH user_count_orders AS (
-- Set up the user_count_orders CTE
  SELECT
    user_id
    ,COUNT(DISTINCT order_id) AS count_orders
  FROM orders
  -- Only keep orders in August 2018
  WHERE DATE_TRUNC('month', order_date) = '2018-08-01'
  GROUP BY user_id
)
SELECT
  -- Select user ID, and rank user ID by count_orders
  user_id
  ,RANK() OVER (
    ORDER BY count_orders DESC
  ) AS count_orders_rank
FROM user_count_orders
ORDER BY count_orders_rank ASC
