import os
from django.db import connection
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def load_data_script(sender, **kwargs):
    sql_file_path = os.path.join(settings.BASE_DIR, 'User', 'initial_data.sql')

    if not os.path.exists(sql_file_path):
        print(f'SQL file not found: {sql_file_path}')
        return

    affected_tables = ['categories', 'products', 'roles', '"user"', 'orders', 'order_items']

    with connection.cursor() as cursor:
        for table in affected_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                if count == 0:
                    with open(sql_file_path, 'r') as file:
                        sql = file.read()
                        table_data = extract_table_data(sql, table)
                        if table_data:
                            for stmt in table_data.split(';'):
                                clean_stmt = stmt.strip()
                                if clean_stmt:
                                    cursor.execute(clean_stmt)
                            print(f'Successfully loaded data for table {table}')
            except Exception as e:
                print(f"Skipping table {table}: {e}")
                continue

def extract_table_data(sql, table):
    sql_statements = sql.split(';')
    table_data = []

    for statement in sql_statements:
        if table.replace('"', '') in statement.lower():
            table_data.append(statement.strip())

    return ';\n'.join(table_data) + ';' if table_data else None
