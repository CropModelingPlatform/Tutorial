import pyodbc
import sqlite3
from pathlib import Path


def decode_sketchy_utf16(raw_bytes):
    s = raw_bytes.decode("utf-16le", "ignore")
    try:
        n = s.index('\u0000')
        s = s[:n]  # respect null terminator
    except ValueError:
        pass
    return s

def convert_access_to_sqlite(path_to_access_db, path_to_sql_db):
    """
    Converts an Access database to a SQLite database.
    """
    print(path_to_sql_db)
    
    # Map Access types to SQLite types
    type_mapping = {
        'COUNTER': 'INTEGER',
        'INTEGER': 'INTEGER',
        'LONG': 'INTEGER',
        'SHORT': 'INTEGER',
        'BYTE': 'INTEGER',
        'SINGLE': 'REAL',
        'DOUBLE': 'REAL',
        'CURRENCY': 'REAL',
        'DECIMAL': 'REAL',
        'VARCHAR': 'TEXT',
        'LONGCHAR': 'TEXT',
        'DATETIME': 'TEXT',
        'BIT': 'INTEGER',
        'YESNO': 'INTEGER',
        'Long Integer': 'INTEGER',
        'integer': 'INTEGER',
        'Iouble': 'REAL',
        "SMALLINT": "INTEGER",
    
    }
    
    # Make sqlite connections
    sqlite_conn = sqlite3.connect(path_to_sql_db)
    sqlite_cursor = sqlite_conn.cursor()
 
    # Make mdb connections
    constr = "DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={0};".format(Path(path_to_access_db))
    access_conn = pyodbc.connect(constr, autocommit=False)
    access_conn.setdecoding(pyodbc.SQL_WCHAR, encoding='latin-1')
    
    prev_converter = access_conn.get_output_converter(pyodbc.SQL_WVARCHAR)
    access_conn.add_output_converter(pyodbc.SQL_WVARCHAR, decode_sketchy_utf16)

    cursor = access_conn.cursor()
    
    tables = [table_info.table_name for table_info in cursor.tables(tableType='TABLE')]
 
    for table in tables:
        # Access databases, have several internal tables. They all start with the
        # "MSys" prefix. If you need them, just remove the if clause.
        if not table.startswith("MSys"):
            print(table)
            ## Create tables
            columns = [column for column in cursor.columns(table=table)]
            access_conn.add_output_converter(pyodbc.SQL_WVARCHAR, prev_converter)

            s = []

            for column in columns:
                # Map Access type to SQLite type
                access_type = column.type_name.upper()
                print("----------------", column.column_name, access_type)
                sqlite_type = type_mapping.get(access_type, 'TEXT')  # Default to TEXT if unknown
                
                # For INTEGER types, don't include size specification
                if sqlite_type == 'INTEGER':
                    s.append("[%s] %s" % (column.column_name, sqlite_type))
                else:
                    s.append("[%s] %s" % (column.column_name, sqlite_type))
            creation_string = ("CREATE TABLE [%s] (\n" % table +
                               ",\n".join(s) +
                               "\n);")
            sqlite_cursor.execute(creation_string)
 
            ## Insert values
            # select everything from the mdb-table
            rows = [row for row in cursor.execute("SELECT * FROM [%s];" % table)]
            # Check if the table has data. If it doesn't go to the next table, else
            # insert them to the sqlite database.
            try:
                length = len(rows[0])
            except IndexError:
                pass
            else:
                insertion_string = "insert into [%s] values " % table
                insertion_string += "(" + ", ".join(["?" for i in range(length)]) + ")"
                sqlite_conn.executemany(insertion_string, rows)
    
    # close databases
    sqlite_conn.commit()
    sqlite_conn.close()
    access_conn.close()
 
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert Access DB to SQLite DB")
    parser.add_argument("access_db", type=str, help="Path to the Access database file")
    parser.add_argument("sqlite_db", type=str, help="Path to the output SQLite database file")

    args = parser.parse_args()

    convert_access_to_sqlite(args.access_db, args.sqlite_db)