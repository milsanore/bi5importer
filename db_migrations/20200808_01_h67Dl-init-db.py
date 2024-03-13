"""
init db
"""

from yoyo import step

__depends__ = {}

steps = [
	step("""
	CREATE TABLE instruments (
		id 				SMALLSERIAL PRIMARY KEY,
		instrument_name VARCHAR(50) NOT NULL CHECK (instrument_name <> ''),
		point_value 	NUMERIC(10, 4) 	NOT NULL CHECK (point_value > 0)
	)
	"""),
	step("""
	CREATE UNIQUE INDEX UNIQUE_instrument_name on instruments (TRIM(LOWER(instrument_name)));
	"""),
	step("""
	INSERT INTO instruments(instrument_name, point_value) VALUES ('AUDSGD', 0.01);
	"""),

	step("""
	CREATE TABLE price_history (
		id 				BIGSERIAL 		PRIMARY KEY,
		id_instrument 	SMALLSERIAL 	NOT NULL,
		date 			TIMESTAMP 		NOT NULL CHECK (date >= '2000-01-01'),
		bid 			NUMERIC(10, 4) 	NOT NULL CHECK (bid > 0),
		bid_volume 		NUMERIC(10, 4) 	NOT NULL CHECK (bid_volume >= 0),
		ask 			NUMERIC(10, 4) 	NOT NULL CHECK (ask > 0),
		ask_volume 		NUMERIC(10, 4) 	NOT NULL CHECK (ask_volume >= 0),

		CONSTRAINT UNIQUE_instrument_and_date UNIQUE(id_instrument, date),
		CONSTRAINT fk_instrument_id FOREIGN KEY(id_instrument) REFERENCES instruments(id)
	)
	"""),
	step("""
	CREATE INDEX price_history_date_idx ON public.price_history ("date");
	""")
]
