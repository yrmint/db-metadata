from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from backend.services.db_service import get_database_by_id
from backend.core import influxdb_config

def save_timestamp(stats_item):
    client = InfluxDBClient(
        url=influxdb_config.INFLUX_URL,
        token=influxdb_config.INFLUX_TOKEN,
        org=influxdb_config.INFLUX_ORG
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)

    db_item = get_database_by_id(stats_item.db_id)

    point = (
        Point("db_stats")
        .tag("db_id", stats_item.db_id)
        .tag("db_name", db_item.db_name)
    )
    fields = {
        "tables_count": stats_item.tables_count,
        "columns_count": stats_item.columns_count,
        "pk_count": stats_item.pk_count,
        "fk_count": stats_item.fk_count,
        "uk_count": stats_item.uk_count,
        "records_count": stats_item.records_count,
    }

    for key, value in fields.items():
        if value is not None:
            point.field(key, value)
        else:
            point.field(key, None)

    write_api.write(
        bucket=influxdb_config.INFLUX_BUCKET,
        org=influxdb_config.INFLUX_ORG,
        record=point
    )

    return {"status": "ok"}

def get_all_timestamps():
    client = InfluxDBClient(
        url=influxdb_config.INFLUX_URL,
        token=influxdb_config.INFLUX_TOKEN,
        org=influxdb_config.INFLUX_ORG
    )
    query_api = client.query_api()

    query = f'''
        from(bucket: "{influxdb_config.INFLUX_BUCKET}")
            |> range(start: 0)
            |> filter(fn: (r) => r._measurement == "db_stats")
        '''

    tables = query_api.query(org=influxdb_config.INFLUX_ORG, query=query)

    results = {}

    for table in tables:
        for record in table.records:
            time = record.get_time().isoformat()

            if time not in results:
                results[time] = {
                    "time": time,
                    "db_id": record.values.get("db_id"),
                    "db_name": record.values.get("db_name"),
                    "tables_count": None,
                    "columns_count": None,
                    "pk_count": None,
                    "fk_count": None,
                    "uk_count": None,
                    "records_count": None
                }

            results[time][record["_field"]] = record["_value"]

    return list(results.values())
