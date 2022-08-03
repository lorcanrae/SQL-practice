-- Revenue Queries

-- Total spent per user_id
SELECT SUM(meals.meal_price * orders.order_quantity) AS revenue
FROM meals
JOIN orders ON meals.meal_id = orders.meal_id
-- Keep only the records of customer ID 15
WHERE orders.user_id = 15;
----------------------------------------------------------

-- Revenue per week
SELECT DATE_TRUNC('week', order_date) :: DATE AS delivr_week,
  -- Calculate revenue
  SUM(m.meal_price * o.order_quantity) AS revenue
FROM meals m
JOIN orders o ON m.meal_id = o.meal_id
-- Keep only the records in June 2018
WHERE o.order_date BETWEEN '2018-06-01' AND '2018-07-01'
GROUP BY delivr_week
ORDER BY delivr_week ASC;
----------------------------------------------------------

-- Cost and Common Table Expressions (CTE) Queries

-- Total cost to business
SELECT SUM(m.meal_cost * s.stocked_quantity)
FROM stock s
JOIN meals m ON m.meal_id = s.meal_id
----------------------------------------------------------

-- Top five meals by cost to company
SELECT m.meal_id
  ,SUM(s.stocked_quantity * m.meal_cost) AS cost
FROM meals m
JOIN stock s ON m.meal_id = s.meal_id
GROUP BY m.meal_id
ORDER BY cost DESC
LIMIT 5;
----------------------------------------------------------

-- Average cost per month before Sep 2018
WITH cost_per_month as(
SELECT
  DATE_TRUNC('month', s.stocking_date) :: DATE AS delivr_month
  ,SUM(m.meal_cost * s.stocked_quantity) AS cost
FROM meals m
JOIN stock s ON m.meal_id = s.meal_id
GROUP BY delivr_month
ORDER BY delivr_month ASC
)
SELECT AVG(cpm.cost)
FROM cost_per_month cpm
WHERE cpm.delivr_month < '2018-09-01'
----------------------------------------------------------

-- Profit per eatery
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
SELECT r.eatery
  ,(r.revenue - c.cost) AS profit
FROM revenue r
JOIN cost c ON r.eatery = c.eatery
ORDER BY profit DESC;
----------------------------------------------------------

-- Profit per month
WITH revenue AS (
-- Revenue CTE
  SELECT
    DATE_TRUNC('month', order_date) :: DATE AS delivr_month
    ,SUM(m.meal_price * o.order_quantity) AS revenue
  FROM meals m
  JOIN orders o ON m.meal_id = o.meal_id
  GROUP BY delivr_month
),
cost AS (
-- Cost CTE
  SELECT
    DATE_TRUNC('month', stocking_date) :: DATE AS delivr_month
    ,SUM(s.stocked_quantity * m.meal_cost) AS cost
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
----------------------------------------------------------
