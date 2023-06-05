import pandas as pds
from sqlalchemy import create_engine
import psycopg2
import re
from datetime import datetime

# Set up database connection parameters
db_endpoint =
db_port =
db_name =
db_user =
db_password =
connectionstring = f'postgresql://{db_user}:{db_password}@{db_endpoint}:{db_port}/{db_name}'

# Load the different migration scripts in
migration1 = open(
    '..//smtp-crawler/src/main/resources/db/migration/migration_1_create_smtp_data.sql',
    'r').read()
migration2 = open(
    '..//smtp-crawler/src/main/resources/db/migration/migration_2_per_ip_per_day.sql',
    'r').read()
migration3 = open(
    '..//smtp-crawler/src/main/resources/db/migration/migration_3_smtp_conversation.sql',
    'r').read()
migration4 = open(
    '..//smtp-crawler/src/main/resources/db/migration/migration_4_smtp_visit.sql',
    'r').read()
migration4_split = re.split("---", migration4)
migration5 = open(
    '..//smtp-crawler/src/main/resources/db/migration/migration_5_smtp_host.sql',
    'r').read()

smtp_crawl_result_per_month = "create table smtp_crawl_result_per_month as " + \
                              "select min(id) min_id, max(id) max_id, count(1) rowcount, date_trunc('month', crawl_timestamp) as month " + \
                              "from smtp_crawler.smtp_crawl_result " + \
                              "group by date_trunc('month', crawl_timestamp);"

conn = None
try:
    conn = psycopg2.connect(connectionstring)
    cursor = conn.cursor()
    print(str(datetime.now()) + ": Creating smtp_crawl_result_per_month")
    cursor.execute(smtp_crawl_result_per_month)
    cursor.close()
    conn.commit()

    alchemyEngine = create_engine(connectionstring)
    dbConnection = alchemyEngine.connect()
    results_per_month = pds.read_sql("select * from smtp_crawl_result_per_month order by month",
                                     dbConnection)
    dbConnection.close()
    months = results_per_month.loc[:, "month"]
    print(str(datetime.now()) + ": Done, now starting month per month migration")
    for month in months:
        print(str(datetime.now()) + ": Currently migrating month: " + str(month))
        cursor = conn.cursor()
        filled_in_migration1 = re.sub(r"\)--where month = '.*'",
                                      " where month = '" + str(month) + "'",
                                      migration1)
        cursor.execute(filled_in_migration1)
        conn.commit()
        cursor.execute(migration2)
        conn.commit()
        cursor.execute(migration3)
        cursor.execute(migration4_split[0])
        conn.commit()
        cursor.execute(migration5)
        cursor.execute("drop table smtp_data;")
        cursor.execute("drop table per_ip_per_day;")
        cursor.close()
        conn.commit()

    print(str(datetime.now()) + ": Monthly migrations done, now migrating results without servers")
    cursor = conn.cursor()
    cursor.execute(migration4_split[1])
    conn.commit()
    print(str(datetime.now()) + ": Done, dropping smtp_crawl_result_per_month")
    cursor.execute("drop table smtp_crawl_result_per_month")
    print(str(datetime.now()) + ": Execute done")
    cursor.close()
    conn.commit()
finally:
    if conn is not None:
        conn.close()
