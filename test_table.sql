DROP TABLE IF EXISTS item_categories;
DROP TABLE IF EXISTS items;
CREATE TABLE
IF NOT EXISTS items
(
	id text NOT NULL PRIMARY KEY,
	name VARCHAR(50) NOT NULL,
	status SMALLINT NOT NULL,
	created_at TIMESTAMP NOT NULL
);

CREATE INDEX
IF NOT EXISTS items_status ON items(status);

DROP TABLE IF EXISTS categories;
CREATE TABLE
IF NOT EXISTS categories
(
	id text NOT NULL PRIMARY KEY,
	name VARCHAR(50) NOT NULL,
	created_at TIMESTAMP NOT NULL
);

CREATE TABLE item_categories
(
	id character varying NOT NULL,
	category_id text NOT NULL,
	item_id text NOT NULL,
	created_at timestamp NOT NULL,
	updated_at timestamp NOT NULL,

	CONSTRAINT fk_item FOREIGN KEY(item_id) REFERENCES items(id),
	CONSTRAINT fk_category FOREIGN KEY(category_id) REFERENCES categories(id)
);

CREATE INDEX IF NOT EXISTS item_categories_cateogory_id_item_id_idx ON item_categories (category_id, item_id);
