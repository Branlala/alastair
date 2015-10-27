BEGIN;



DROP VIEW IF EXISTS cooking_project_pricelist, cooking_project_pricelist_partial, cooking_meal_pricelist, cooking_meal_pricelist_partial, cooking_meal_receipe_pricelist, cooking_meal_receipe_pricelist_partial, cooking_project_readonly, cooking_meal_readonly, cooking_meal_receipe_readonly, cooking_receipe_readonly, cooking_receipe_ingredient_readonly, cooking_inventory_item_readonly, cooking_project_pricelist_partial_invsub, cooking_project_pricelist_invsub;

CREATE VIEW cooking_receipe_ingredient_readonly AS SELECT ri.id, ri.receipe_id, ri.ingredient_id, ri.amount, ri.measurement, ri.remarks, IF(ri.measurement = i.calculation_measurement, (ri.amount / i.calculation_quantity) * i.price, IF(ri.measurement = i.buying_measurement, (ri.amount / i.buying_quantity) * i.price, 0.0)) AS price_in_receipe FROM cooking_receipe_ingredient ri INNER JOIN cooking_ingredient i ON ri.ingredient_id = i.id WHERE 1;

CREATE VIEW cooking_receipe_readonly AS SELECT r.id, r.name, r.default_person_count, r.instructions, SUM(ri.price_in_receipe) AS price FROM cooking_receipe r INNER JOIN cooking_receipe_ingredient_readonly ri ON ri.receipe_id = r.id WHERE 1;

CREATE VIEW cooking_meal_receipe_readonly AS SELECT mr.id, mr.meal_id, mr.receipe_id, mr.person_count, (mr.person_count / r.default_person_count) * r.price AS price FROM cooking_meal_receipe mr INNER JOIN cooking_receipe_readonly r ON mr.receipe_id = r.id WHERE 1;

CREATE VIEW cooking_meal_readonly AS SELECT m.id, m.name, m.time, m.project_id, SUM(mr.price) AS price FROM cooking_meal m INNER JOIN cooking_meal_receipe_readonly mr ON mr.meal_id = m.id WHERE 1;

CREATE VIEW cooking_project_readonly AS SELECT p.id, p.name, p.start_date, p.end_date, SUM(m.price) AS price FROM cooking_project p INNER JOIN cooking_meal_readonly m ON p.id = m.project_id GROUP BY p.id;


-- CREATE VIEW cooking_meal_receipe_pricelist AS
-- SELECT mr.meal_id, 
--   mr.receipe_id, 
--   i.name, 
--   (mr.person_count / r.default_person_count) * ri.amount AS exact_amount, 
--   ri.measurement, (mr.person_count / r.default_person_count) * IF(ri.measurement = i.calculation_measurement, (ri.amount / i.calculation_quantity) * i.price, IF(ri.measurement = i.buying_measurement, (ri.amount / i.buying_quantity) * i.price, 0.0)) AS exact_price, 
--   IF(ri.measurement = i.calculation_measurement, CEIL(((mr.person_count / r.default_person_count) * ri.amount) / i.calculation_quantity) * i.buying_quantity, IF(ri.measurement = i.buying_measurement, CEIL(((mr.person_count / r.default_person_count) * ri.amount) / i.buying_quantity) * i.buying_quantity, 0)) AS effective_amount, 
--   i.buying_measurement AS effective_measurement, 
--   IF(ri.measurement = i.calculation_measurement, CEIL(((mr.person_count / r.default_person_count) * ri.amount) / i.calculation_quantity) * i.price, IF(ri.measurement = i.buying_measurement, CEIL(((mr.person_count / r.default_person_count) * ri.amount) / i.buying_quantity) * i.price, 0)) AS effective_price
-- FROM cooking_meal_receipe mr
-- INNER JOIN cooking_receipe r ON mr.receipe_id = r.id 
-- INNER JOIN cooking_receipe_ingredient ri ON ri.receipe_id = r.id 
-- INNER JOIN cooking_ingredient i ON i.id = ri.ingredient_id 
-- WHERE 1;

CREATE VIEW cooking_meal_receipe_pricelist_partial AS SELECT p.id AS proj_id,
  mr.meal_id AS meal_id,
  mr.receipe_id AS receipe_id,
  i.id AS ing_id,
  i.name AS name, 
  ((mr.person_count / r.default_person_count) * SUM(IF(ri.measurement = i.buying_measurement, ri.amount, (ri.amount / i.calculation_quantity) * i.buying_quantity))) AS exact_amount, 
  i.price AS price,
  i.buying_measurement AS buying_measurement,
  i.buying_quantity AS buying_quantity
FROM cooking_project p
INNER JOIN cooking_meal m ON m.project_id = p.id
INNER JOIN cooking_meal_receipe mr ON m.id = mr.meal_id
INNER JOIN cooking_receipe r ON mr.receipe_id = r.id 
INNER JOIN cooking_receipe_ingredient ri ON ri.receipe_id = r.id 
INNER JOIN cooking_ingredient i ON i.id = ri.ingredient_id 
WHERE 1
GROUP BY p.id, mr.id, i.id;

CREATE VIEW cooking_meal_receipe_pricelist AS SELECT CONCAT(proj_id, meal_id, receipe_id, ing_id) AS id, proj_id, meal_id, receipe_id, ing_id, name, exact_amount, (exact_amount / buying_quantity) * price AS exact_price, CEIL(exact_amount / buying_quantity) * buying_quantity AS effective_amount, CEIL(exact_amount / buying_quantity) AS buying_count, buying_quantity, buying_measurement, CEIL(exact_amount / buying_quantity) * price AS effective_price
FROM cooking_meal_receipe_pricelist_partial;


CREATE VIEW cooking_meal_pricelist_partial AS SELECT m.id AS id, i.name AS name, ((mr.person_count / r.default_person_count) * SUM(IF(ri.measurement = i.buying_measurement, ri.amount, (ri.amount / i.calculation_quantity) * i.buying_quantity))) AS exact_amount, i.price AS price, i.buying_measurement AS buying_measurement, i.buying_quantity AS buying_quantity
FROM cooking_meal m
INNER JOIN cooking_meal_receipe mr ON m.id = mr.meal_id
INNER JOIN cooking_receipe r ON mr.receipe_id = r.id 
INNER JOIN cooking_receipe_ingredient ri ON ri.receipe_id = r.id 
INNER JOIN cooking_ingredient i ON i.id = ri.ingredient_id 
WHERE 1
GROUP BY i.id;


CREATE VIEW cooking_meal_pricelist AS SELECT id, name, exact_amount, exact_amount * price AS exact_price, CEIL(exact_amount / buying_quantity) * buying_quantity AS effective_amount, CEIL(exact_amount / buying_quantity) AS buying_count, buying_quantity, buying_measurement, CEIL(exact_amount / buying_quantity) * price AS effective_price FROM cooking_meal_pricelist_partial;


CREATE VIEW cooking_project_pricelist_partial AS (SELECT p.id AS project_id,
  i.id AS ing_id,
  i.name AS name, 
  ((mr.person_count / r.default_person_count) * SUM(IF(ri.measurement = i.buying_measurement, ri.amount, (ri.amount / i.calculation_quantity) * i.buying_quantity))) AS exact_amount, 
  i.price AS price,
  i.buying_measurement AS buying_measurement,
  i.buying_quantity AS buying_quantity,
  i.calculation_quantity AS calculation_quantity,
  i.calculation_measurement AS calculation_measurement,
  i.remarks AS remarks,
  MIN(m.time) AS first_occurrence
FROM cooking_project p
INNER JOIN cooking_meal m ON m.project_id = p.id
INNER JOIN cooking_meal_receipe mr ON m.id = mr.meal_id
INNER JOIN cooking_receipe r ON mr.receipe_id = r.id 
INNER JOIN cooking_receipe_ingredient ri ON ri.receipe_id = r.id 
INNER JOIN cooking_ingredient i ON i.id = ri.ingredient_id 
WHERE 1
GROUP BY p.id, i.id);


CREATE VIEW cooking_project_pricelist AS SELECT project_id, ing_id, name, exact_amount, (exact_amount / buying_quantity) * price AS exact_price, CEIL(exact_amount / buying_quantity) * buying_quantity AS effective_amount, CEIL(exact_amount / buying_quantity) AS buying_count, buying_quantity, buying_measurement, CEIL(exact_amount / buying_quantity) * price AS effective_price, calculation_quantity, calculation_measurement, remarks, first_occurrence
FROM cooking_project_pricelist_partial;

CREATE VIEW cooking_inventory_item_readonly AS SELECT inv.id, inv.project_id, inv.ingredient_id, 
IF(i.buying_measurement = inv.measurement,
   inv.amount, 
   IF(i.calculation_measurement = inv.measurement, 
      (inv.amount / i.calculation_quantity) * i.buying_quantity, 
      0)) AS exact_amount,
i.buying_measurement AS measurement
FROM cooking_inventory_item inv
INNER JOIN cooking_ingredient i ON inv.ingredient_id = i.id
WHERE 1;

CREATE VIEW cooking_project_pricelist_partial_invsub AS SELECT p.id AS project_id,
  i.id AS ing_id,
  i.name AS name, 
  IF(((mr.person_count / r.default_person_count) * SUM(IF(ri.measurement = i.buying_measurement, ri.amount, (ri.amount / i.calculation_quantity) * i.buying_quantity))) - IFNULL(inv.exact_amount, 0) >= 0, ((mr.person_count / r.default_person_count) * SUM(IF(ri.measurement = i.buying_measurement, ri.amount, (ri.amount / i.calculation_quantity) * i.buying_quantity))) - IFNULL(inv.exact_amount, 0), 0) AS exact_amount, 
  i.price AS price,
  i.buying_measurement AS buying_measurement,
  i.buying_quantity AS buying_quantity,
  i.calculation_quantity AS calculation_quantity,
  i.calculation_measurement AS calculation_measurement,
  i.remarks AS remarks,
  MIN(m.time) AS first_occurrence
FROM cooking_project p
INNER JOIN cooking_meal m ON m.project_id = p.id
INNER JOIN cooking_meal_receipe mr ON m.id = mr.meal_id
INNER JOIN cooking_receipe r ON mr.receipe_id = r.id 
INNER JOIN cooking_receipe_ingredient ri ON ri.receipe_id = r.id 
INNER JOIN cooking_ingredient i ON i.id = ri.ingredient_id 
LEFT JOIN cooking_inventory_item_readonly inv ON p.id = inv.project_id AND i.id = inv.ingredient_id
WHERE 1
GROUP BY p.id, i.id;

CREATE VIEW cooking_project_pricelist_invsub AS SELECT project_id, ing_id, name, exact_amount, (exact_amount / buying_quantity) * price AS exact_price, CEIL(exact_amount / buying_quantity) * buying_quantity AS effective_amount, CEIL(exact_amount / buying_quantity) AS buying_count, buying_quantity, buying_measurement, CEIL(exact_amount / buying_quantity) * price AS effective_price, calculation_quantity, calculation_measurement, remarks, first_occurrence
FROM cooking_project_pricelist_partial_invsub;



/*
SELECT id, name, exact_amount, exact_amount * price AS exact_price, CEIL(exact_amount / buying_quantity) * buying_quantity AS effective_amount, buying_measurement, CEIL(exact_amount / buying_quantity) * price AS effective_price
FROM 
(SELECT m.id AS id, 
  i.name AS name, 
  ((mr.person_count / r.default_person_count) * SUM(IF(ri.measurement = i.buying_measurement, ri.amount, (ri.amount / i.calculation_quantity) * i.buying_quantity))) AS exact_amount, 
  i.price AS price,
  i.buying_measurement AS buying_measurement,
  i.buying_quantity AS buying_quantity
FROM cooking_meal m
INNER JOIN cooking_meal_receipe mr ON m.id = mr.meal_id
INNER JOIN cooking_receipe r ON mr.receipe_id = r.id 
INNER JOIN cooking_receipe_ingredient ri ON ri.receipe_id = r.id 
INNER JOIN cooking_ingredient i ON i.id = ri.ingredient_id 
WHERE 1
GROUP BY i.id) dt

SELECT project_id, name, exact_amount, exact_amount * price AS exact_price, CEIL(exact_amount / buying_quantity) * buying_quantity AS effective_amount, buying_measurement, CEIL(exact_amount / buying_quantity) * price AS effective_price
FROM 
(SELECT p.id AS project_id, 
  i.name AS name, 
  ((mr.person_count / r.default_person_count) * SUM(IF(ri.measurement = i.buying_measurement, ri.amount, (ri.amount / i.calculation_quantity) * i.buying_quantity))) AS exact_amount, 
  i.price AS price,
  i.buying_measurement AS buying_measurement,
  i.buying_quantity AS buying_quantity
FROM cooking_project p
INNER JOIN cooking_meal m ON m.project_id = p.id
INNER JOIN cooking_meal_receipe mr ON m.id = mr.meal_id
INNER JOIN cooking_receipe r ON mr.receipe_id = r.id 
INNER JOIN cooking_receipe_ingredient ri ON ri.receipe_id = r.id 
INNER JOIN cooking_ingredient i ON i.id = ri.ingredient_id 
WHERE 1
GROUP BY i.id) dt*/



COMMIT;
