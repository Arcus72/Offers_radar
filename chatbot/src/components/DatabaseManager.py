import psycopg2
from datetime import date, datetime
from psycopg2.extras import  RealDictCursor
from schemas.FiltersFormat import FiltersFormat


class DatabaseManager:

    def __init__(self, db_name, db_user, db_password, db_host, db_port):

        self.conn = psycopg2.connect(
            dbname=db_name, user=db_user, password=db_password,
            host=db_host, port=db_port,
        )
        self.cur = self.conn.cursor()


    def get_filtered_offers(self, filters: FiltersFormat, limit: int = 10, table: str = "offers") -> list[dict]:
        conditions = []
        params = []

        list_fields = ["type", "city", "district", "street"]
        for field in list_fields:
            val = getattr(filters, field)
            if val:
                conditions.append(f"{field} = ANY(%s)")
                params.append(val)

        # Obsługa pól typu  Str
        scalar_fields = [
            ("building_type", filters.building_type),
            ("building_material", filters.building_material),
            ("kitchen_type", filters.kitchen_type),
            ("condition", filters.condition),
            ("parking", filters.parking),
            ("heating", filters.heating),
        ]
        for field_name, value in scalar_fields:
            if value is not None:
                conditions.append(f"{field_name} = %s")
                params.append(value)

        # Obsługa pól bool
        bool_fields = [
            ("lift", filters.lift),
            ("has_balcony", filters.has_balcony),
            ("storage_room", filters.storage_room),
            ("accessible", filters.accessible),
            ("fenced", filters.fenced),
            ("monitoring", filters.monitoring),
            ("school", filters.school),
            ("kindergarten", filters.kindergarten),
            ("university", filters.university),
            ("shop", filters.shop),
            ("public_transport", filters.public_transport),
            ("park", filters.park),
            ("medical", filters.medical),
            ("pharmacy", filters.pharmacy),
            ("city_center", filters.city_center),
        ]
        for field_name, value in bool_fields:
            if value is not None:
                conditions.append(f"{field_name} = %s")
                params.append(value)

        # Obsługa pól zakresowych RangeValue (min_value, exact_value, max_value)
        range_fields = [
            ("price", filters.price),
            ("area", filters.area),
            ("rooms", filters.rooms),
            ("bed_rooms", filters.bed_rooms),
            ("bathrooms", filters.bathrooms),
            ("floor", filters.floor),
            ("building_floors", filters.building_floors),
            ("build_year", filters.build_year),
            ("balcony_area", filters.balcony_area),
            ("rent_fee", filters.rent_fee),
            ("school_dist", filters.school_dist),
            ("kindergarten_dist", filters.kindergarten_dist),
            ("university_dist", filters.university_dist),
            ("shop_dist", filters.shop_dist),
            ("public_transport_dist", filters.public_transport_dist),
            ("park_dist", filters.park_dist),
            ("medical_dist", filters.medical_dist),
            ("pharmacy_dist", filters.pharmacy_dist),
            ("city_center_dist", filters.city_center_dist),
        ]

        for field_name, range_obj in range_fields:
            if range_obj is not None:
                if range_obj.exact_value is not None:
                    conditions.append(f"{field_name} = %s")
                    params.append(range_obj.exact_value)
                else:
                    if range_obj.min_value is not None:
                        conditions.append(f"{field_name} >= %s")
                        params.append(range_obj.min_value)
                    if range_obj.max_value is not None:
                        conditions.append(f"{field_name} <= %s")
                        params.append(range_obj.max_value)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT *
            FROM {table}
            {where_clause}
            LIMIT %s
        """
        params.append(limit)

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def close(self) -> None:
        if not self.cur.closed:
            self.cur.close()
        if not self.conn.closed:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
