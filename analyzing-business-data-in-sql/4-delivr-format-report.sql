-- FORMATTING

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
----------------------------------------------------------

-- PIVOTING

-- Pivoting user revenue by month
CREATE EXTENSION IF NOT EXISTS tablefunc;

SELECT * FROM CROSSTAB($$
  SELECT
    user_id,
    DATE_TRUNC('month', order_date) :: DATE AS delivr_month,
    SUM(meal_price * order_quantity) :: FLOAT AS revenue
  FROM meals
  JOIN orders ON meals.meal_id = orders.meal_id
 WHERE user_id IN (0, 1, 2, 3, 4)
   AND order_date < '2018-09-01'
 GROUP BY user_id, delivr_month
 ORDER BY user_id, delivr_month;
$$)
-- Select user ID and the months from June to August 2018
AS ct (user_id INT,
        "2018-06-01" FLOAT,
        "2018-07-01" FLOAT,
        "2018-08-01" FLOAT)
ORDER BY user_id ASC;
----------------------------------------------------------

-- Total Costs by eatery for November and December
CREATE EXTENSION IF NOT EXISTS tablefunc;

SELECT * FROM CROSSTAB($$
  SELECT
    -- Select eatery and calculate total cost
    eatery,
    DATE_TRUNC('month', stocking_date) :: DATE AS delivr_month,
    SUM(meal_cost * stocked_quantity) :: FLOAT AS cost
  FROM meals
  JOIN stock ON meals.meal_id = stock.meal_id
  -- Keep only the records after October 2018
  WHERE DATE_TRUNC('month', stocking_date) > '2018-10-01'
  GROUP BY eatery, delivr_month
  ORDER BY eatery, delivr_month;
$$)
-- Select the eatery and November and December 2018 as columns
AS ct (eatery TEXT,
       "2018-11-01" FLOAT,
       "2018-12-01" FLOAT)
ORDER BY eatery ASC;
----------------------------------------------------------

-- Executive report
CREATE EXTENSION IF NOT EXISTS tablefunc;

SELECT * FROM CROSSTAB($$
  WITH eatery_users AS  (
    SELECT
      eatery,
      -- Format the order date so "2018-06-01" becomes "Q2 2018"
      TO_CHAR(order_date, '"Q"Q YYYY') AS delivr_quarter,
      -- Count unique users
      COUNT(DISTINCT user_id) AS users
    FROM meals m
    JOIN orders o ON m.meal_id = o.meal_id
    GROUP BY eatery, delivr_quarter
    ORDER BY delivr_quarter, users
  )
  SELECT
    -- Select eatery and quarter
    eatery,
    delivr_quarter,
    -- Rank rows, partition by quarter and order by users
    RANK() OVER
      (PARTITION BY delivr_quarter
       ORDER BY users DESC) :: INT AS users_rank
  FROM eatery_users
  ORDER BY eatery, delivr_quarter;
$$)
-- Select the columns of the pivoted table
AS  ct (eatery TEXT,
        "Q2 2018" INT,
        "Q3 2018" INT,
        "Q4 2018" INT)
ORDER BY "Q4 2018";
----------------------------------------------------------
