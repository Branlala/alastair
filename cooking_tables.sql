BEGIN;

CREATE TABLE `cooking_allergen` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(256) NOT NULL
)
;
CREATE TABLE `cooking_ingredient_allergens` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `ingredient_id` integer NOT NULL,
    `allergen_id` integer NOT NULL,
    UNIQUE (`ingredient_id`, `allergen_id`)
)
;
ALTER TABLE `cooking_ingredient_allergens` ADD CONSTRAINT `allergen_id_refs_id_685b8900` FOREIGN KEY (`allergen_id`) REFERENCES `cooking_allergen` (`id`);
CREATE TABLE `cooking_ingredient` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(256) NOT NULL,
    `buying_quantity` double precision NOT NULL,
    `buying_measurement` varchar(2) NOT NULL,
    `calculation_quantity` double precision NOT NULL,
    `calculation_measurement` varchar(2) NOT NULL,
    `price` numeric(8, 2) NOT NULL,
    `cheapest_store` varchar(256) NOT NULL,
    `remarks` varchar(512) NOT NULL
)
;
ALTER TABLE `cooking_ingredient_allergens` ADD CONSTRAINT `ingredient_id_refs_id_560657dd` FOREIGN KEY (`ingredient_id`) REFERENCES `cooking_ingredient` (`id`);
CREATE TABLE `cooking_receipe` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(256) NOT NULL,
    `default_person_count` integer NOT NULL,
    `instructions` longtext NOT NULL
)
;
CREATE TABLE `cooking_project` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(256) NOT NULL
)
;
CREATE TABLE `cooking_meal` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(256) NOT NULL,
    `time` datetime(6) NOT NULL,
    `project_id` integer NOT NULL
)
;
ALTER TABLE `cooking_meal` ADD CONSTRAINT `project_id_refs_id_ba1f8d6c` FOREIGN KEY (`project_id`) REFERENCES `cooking_project` (`id`);
CREATE TABLE `cooking_receipe_ingredient` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `receipe_id` integer NOT NULL,
    `ingredient_id` integer NOT NULL,
    `amount` double precision NOT NULL,
    `remarks` varchar(256) NOT NULL
)
;
ALTER TABLE `cooking_receipe_ingredient` ADD CONSTRAINT `ingredient_id_refs_id_9d127311` FOREIGN KEY (`ingredient_id`) REFERENCES `cooking_ingredient` (`id`);
ALTER TABLE `cooking_receipe_ingredient` ADD CONSTRAINT `receipe_id_refs_id_a268b201` FOREIGN KEY (`receipe_id`) REFERENCES `cooking_receipe` (`id`);
CREATE TABLE `cooking_meal_receipe` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `meal_id` integer NOT NULL,
    `receipe_id` integer NOT NULL,
    `person_count` integer NOT NULL,
    `remarks` varchar(256) NOT NULL
)
;
ALTER TABLE `cooking_meal_receipe` ADD CONSTRAINT `meal_id_refs_id_2d54c61e` FOREIGN KEY (`meal_id`) REFERENCES `cooking_meal` (`id`);
ALTER TABLE `cooking_meal_receipe` ADD CONSTRAINT `receipe_id_refs_id_dea9c803` FOREIGN KEY (`receipe_id`) REFERENCES `cooking_receipe` (`id`);
CREATE INDEX `cooking_ingredient_allergens_8cbc2862` ON `cooking_ingredient_allergens` (`ingredient_id`);
CREATE INDEX `cooking_ingredient_allergens_d380d8a5` ON `cooking_ingredient_allergens` (`allergen_id`);
CREATE INDEX `cooking_meal_37952554` ON `cooking_meal` (`project_id`);
CREATE INDEX `cooking_receipe_ingredient_2cfb5610` ON `cooking_receipe_ingredient` (`receipe_id`);
CREATE INDEX `cooking_receipe_ingredient_8cbc2862` ON `cooking_receipe_ingredient` (`ingredient_id`);
CREATE INDEX `cooking_meal_receipe_7ebabbcb` ON `cooking_meal_receipe` (`meal_id`);
CREATE INDEX `cooking_meal_receipe_2cfb5610` ON `cooking_meal_receipe` (`receipe_id`);

COMMIT;