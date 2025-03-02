import sqlite3
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from dotenv import load_dotenv
import os

# -----------------------------------------------
# 2) Create a Small SQLite Database (In-Memory)
# -----------------------------------------------
# Option A: In-memory DB via SQLAlchemy URI
#   The "sqlite:///:memory:" URI doesn't work out-of-the-box with direct table creation 
#   using SQLDatabase.from_uri, so we'll do a hybrid approach:
#   - Manually create the table with sqlite3
#   - Then re-connect via LangChain's SQLDatabase

db_uri = "file:langchain_temp_db?mode=memory&cache=shared"
full_uri = f"sqlite:///{db_uri}"

# Create the in-memory database using sqlite3
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# Drop the table if it exists
cursor.execute("DROP TABLE IF EXISTS employees")

# Create a toy "employees" table
cursor.execute("""
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        country TEXT,
        salary INTEGER
    )
""")

# Insert sample rows
employees_data = [
    (1, 'Alice',   'USA',     100000),
    (2, 'Bob',     'Germany', 90000),
    (3, 'Charlie', 'USA',     120000),
    (4, 'Diana',   'France',  95000),
]
cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)", employees_data)
conn.commit()
conn.close()

# We'll keep this connection open, but let's wrap it with LangChain's SQLDatabase
# by attaching to the *same* in-memory DB through a "shared cache" trick.
# (SQLAlchemy can't directly share the same connection object, so we do the following).
#   1) Dump data to a temporary on-disk db or
#   2) Use the special URI syntax for shared in-memory

# For a truly ephemeral approach, let's switch to a file-based approach quickly:

# Create temporary file database
temp_db_file = "temp_langchain_employees.db"
# Recreate on disk so we can read it with SQLDatabase
conn_disk = sqlite3.connect(temp_db_file)
cur_disk = conn_disk.cursor()

# Drop the table if it exists in the disk database
cur_disk.execute("DROP TABLE IF EXISTS employees")

# Create the table in the disk database
cur_disk.execute("""
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        country TEXT,
        salary INTEGER
    )
""")

# Insert sample rows
cur_disk.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)", employees_data)
conn_disk.commit()
conn_disk.close()

# At the start of your script, print the full path
print(f"Database will be created at: {os.path.abspath(temp_db_file)}")

def main():
    # Load environment variables
    load_dotenv()

    # Initialize ChatOpenAI
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    # Create SQLDatabase instance - using our temporary database
    db = SQLDatabase.from_uri(f"sqlite:///{temp_db_file}")

    # Explore the database
    explore_db(temp_db_file)

    # Create SQL toolkit
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # Create SQL agent
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )

    # Run the agent
    result = agent.run("Do we have Alice in the database?")
    print(result)

def explore_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== Database Explorer ===")
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\nTables in database:")
    for table in tables:
        print(f"- {table[0]}")
        
        # Show schema for each table
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print("  Columns:")
        for col in columns:
            print(f"    {col[1]} ({col[2]})")
            
        # Show row count
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  Row count: {count}")
        
        # Show sample data
        cursor.execute(f"SELECT * FROM {table[0]} LIMIT 3")
        rows = cursor.fetchall()
        print("  Sample data:")
        for row in rows:
            print(f"    {row}")
        print()
    
    conn.close()

# Use it like this:
explore_db("temp_langchain_employees.db")

if __name__ == "__main__":
    main()