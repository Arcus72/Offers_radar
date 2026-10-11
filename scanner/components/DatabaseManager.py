import typing
import psycopg2
from pydantic import BaseModel
from datetime import date, datetime
from schemas.OfferFormat import OfferFormat
from schemas.RawOfferData import RawOfferData
from psycopg2.extras import execute_values, RealDictCursor
class DatabaseManager:
    PG_TYPES = {str: "TEXT", int: "INTEGER", float: "DOUBLE PRECISION", bool: "BOOLEAN", date: "DATE",  datetime: "TIMESTAMP",}

    def __init__(self, db_name, db_user, db_password, db_host, db_port):

        self.conn = psycopg2.connect(
            dbname=db_name, user=db_user, password=db_password,
            host=db_host, port=db_port,
        )
        self.cur = self.conn.cursor()

        self.create_table(OfferFormat, "offers")
        self.create_table(RawOfferData, "raw_offers")


    def check_connection(self) -> bool:
        try:
            self.cur.execute("SELECT 1")
            self.cur.fetchone()
            info = self.conn.info
            print(f"Połączono: {info.user}@{info.host}:{info.port}/{info.dbname} "
                  f"(PostgreSQL {info.server_version}, PID {info.backend_pid})")
            return True
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Brak połączenia: {e}")
            return False

    def create_table(self, model: type[BaseModel], table: str) -> None:
        cols = []
        for name, field in model.model_fields.items():
            args = typing.get_args(field.annotation)
            nullable = type(None) in args
            base = next((a for a in args if a is not type(None)), field.annotation)
            if typing.get_origin(base) is typing.Literal:
                base = str
            constraint = " PRIMARY KEY" if name == "offer_id" else "" if nullable else " NOT NULL"
            cols.append(f"{name} {self.PG_TYPES[base]}{constraint}")
        query = f"CREATE TABLE IF NOT EXISTS {table} (\n  " + ",\n  ".join(cols) + "\n);"
        self._execute(query)

    def drop_table(self, table: str) -> None:
        self._execute(f"DROP TABLE IF EXISTS {table}")

    def clear_table(self, table: str) -> None:
        self._execute(f"TRUNCATE TABLE {table}")

    def insert(self, obj: BaseModel, table: str = "offers") -> str:
        data = obj.model_dump()
        cols = ", ".join(data)
        placeholders = ", ".join(["%s"] * len(data))
        self._execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) RETURNING offer_id",
            list(data.values()),
        )
        return self.cur.fetchone()[0]



    def insert_many(self, objs: list[BaseModel], table: str = "offers") -> list[str]:
        if not objs:
            return []

        cols = list(type(objs[0]).model_fields)
        rows = [tuple(getattr(o, c) for c in cols) for o in objs]

        query = (
            f"INSERT INTO {table} ({', '.join(cols)}) VALUES %s "
            f"ON CONFLICT (offer_id) DO NOTHING RETURNING offer_id"
        )
        result = execute_values(self.cur, query, rows, fetch=True)
        self.conn.commit()
        return [r[0] for r in result]

    def get_all_offers_id(self, table: str = "offers") -> set[int]:
        query = f"Select offer_id from {table}"
        with self.conn.cursor() as cur:
            cur.execute(query)
            return {row[0] for row in cur.fetchall()}

    def get_all_data(self, table: str) -> list[dict]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"Select * from {table}")
            return [dict(row) for row in cur.fetchall()]

    def get_missing_market_price(self, table: str = "offers") -> list[dict]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {table} WHERE market_price IS NULL")
            return [dict(row) for row in cur.fetchall()]

    def update_column(self, rows: list[tuple[str, int]], column: str, table: str = "offers") -> None:
        execute_values(
            self.cur,
            f"UPDATE {table} AS t SET {column} = v.value FROM (VALUES %s) AS v(offer_id, value) "
            f"WHERE t.offer_id = v.offer_id",
            rows,
        )
        self.conn.commit()

    def delete_values(self, values: list, column: str, table: str = "offers") -> None:
        self._execute(f"DELETE FROM {table} WHERE {column} = ANY(%s)", (list(values),))

    def _execute(self, query, params=None) -> None:
        try:
            self.cur.execute(query, params)
            self.conn.commit()
        except psycopg2.Error:
            self.conn.rollback() 
            raise

    def close(self) -> None:
        if not self.cur.closed:
            self.cur.close()
        if not self.conn.closed:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()