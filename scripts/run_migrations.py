"""
Run Supabase database migrations manually via Python
"""
import psycopg2
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

def run_migration(sql_file_path):
    """Execute a SQL migration file"""
    print(f"Running migration: {sql_file_path}")
    
    with open(sql_file_path, 'r') as f:
        sql = f.read()
    
    conn = psycopg2.connect(settings.database_url)
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql)
        print(f"✓ Successfully executed {sql_file_path}")
    except Exception as e:
        print(f"✗ Error executing {sql_file_path}: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    migrations_dir = os.path.join(base_dir, "supabase", "migrations")
    
    migrations = [
        "001_initial_schema.sql",
        "003_fix_rls_policies.sql",
        "004_add_entity_analysis.sql"
    ]
    
    for migration in migrations:
        migration_path = os.path.join(migrations_dir, migration)
        run_migration(migration_path)
    
    print("\n✓ All migrations completed successfully!")
