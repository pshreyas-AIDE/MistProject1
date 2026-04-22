# pip install sqlalchemy psycopg2-binary

from sqlalchemy import create_engine, Column, Integer, String, JSON, MetaData, Table,inspect
from sqlalchemy import select, insert, update, delete, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.dialects.postgresql import ARRAY, MACADDR
import json
'''
create_engine: This is the "Engine Room." It manages the actual connection to your PostgreSQL database.

Column, Integer, String, JSON: These are "Building Blocks." They define the data types for your database tables. Using the JSON type is an expert move—it allows Postgres to store your dictionary payloads natively.

'''

from sqlalchemy.orm import DeclarativeBase
'''
declarative_base: This is a "Blueprint Factory." It creates a base class that all your database tables will inherit from. It keeps your code organized.
'''

from sqlalchemy.orm import sessionmaker
'''
sessionmaker: Think of this as a "Transaction Clerk." It creates "Sessions," which are temporary windows used to talk to the database (Save, Delete, Update). 
'''

class Base(DeclarativeBase):
    pass
'''We initialize the blueprint here. Any class we create using Base will automatically be converted into a table in PostgreSQL.
'''



class DatabaseManager:
    def __init__(self, db_url):
        # This line creates the engine and 'attaches' it to the class instance.
        # This Just creates connection pool but no TCP connection to Postgre sql are made here - Just resource allocation and specifying the path we need to use for database
        # The URL format: postgresql://user:password@hostname:port/database_name
        self.engine =create_engine(
                        db_url,
                        pool_size=10,        # Keep 10 "pipes" open at all times
                        max_overflow=20,     # If 10 aren't enough, allow up to 20 more temporary ones
                        pool_timeout=30,     # If all pipes are busy, wait 30 seconds before giving up
                        pool_recycle=1800    # Close and refresh a pipe every 30 minutes (safety measure)
                            )

    # NEW: Create a brand new table with a custom name. If table with name already present use the table
    def create_custom_table(self, table_name, columns_dict,primary_key_defined=False):
        """
        Creates a table dynamically.
        Example: columns_dict = {"name": String, "age": Integer}
        """
        # Creating an empty canvas
        self.metadata = MetaData()

        """Checks if table exists, reuses it, or creates it."""
        inspector = inspect(self.engine)

        if inspector.has_table(table_name):
            # Reuse the existing table structure from the DB
            self.my_table = Table(table_name, self.metadata, autoload_with=self.engine)
        else:
            # To always add a Primary Key 'id' automatically if it is not defined by user while creating
            if (not primary_key_defined):
                cols = [Column('id', Integer, primary_key=True)]
            else:
                cols = []
            for name, dtype in columns_dict.items():
                if (primary_key_defined == name):
                    cols.append(Column(name, dtype, primary_key=True))
                else:
                    cols.append(Column(name, dtype))

            #
            self.my_table = Table(table_name, self.metadata, *cols,extend_existing=True)

            # Creates all the tables that are defined under metadata
            self.metadata.create_all(self.engine)
            print("A Table named : ", table_name, " has been created successfully.")

    def session_local(self):
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        '''
        sessionmaker: This is a class factory. It doesn't open a session yet; it just stores the "recipe" for how a session should behave.

        bind=self.engine: This tells the factory: "Whenever you create a session, tell it to use this specific engine (and its TCP connection pool) to talk to Postgres."

        autocommit=False: This is a safety feature. It means no changes are saved to the database unless you explicitly call .commit(). This prevents accidental half-finished data from being saved.
        '''

    def add_row(self,record_object):
        '''

        Argument : Must be of  type Object of the sqlalchemy.orm.declarative_base instance

        eg :

        class TokenDatabase(Base):
            __tablename__ = "token_database"
            id = Column(Integer, primary_key=True)
            token = Column(String)
            user_id = Column(Integer)

        new_entry = TokenDatabase(token="JNPR-ALPHA-99", user_id=101)

        :param record_object:
        :return:
        '''


        # 1. Open the session (This 'borrows' a TCP connection from the engine's pool)
        session = self.SessionLocal()

        try:
            # 2. Add the object to the "Staging Area"
            session.add(record_object)

            # 3. Flush & Commit (This sends the actual SQL INSERT command)
            session.commit()

            # 4. Refresh (Pulls the auto-generated ID back into your Python object)
            session.refresh(record_object)

        except Exception as e:
            session.rollback()  # If there is an error, undo everything
            raise e
        finally:
            session.close()  # Return the TCP connection to the pool

    def find_row_by_column(self, column_name, value):
        """
        Searches for a row where column_name == value.
        Example: find_row_by_column("email", "test@example.com")
        """
        with self.SessionLocal() as session:
            # # 1. Get the column object from the table's column collection (.c)
            column_to_search = getattr(self.my_table.c, column_name)

            # 2. Build the select statement
            stmt = select(self.my_table).where(column_to_search == value)

            # column_to_search = self.my_table.c[column_name]
            #
            # # This forces Postgres to treat the column as a string for this comparison
            # stmt = select(self.my_table).where(column_to_search == str(value))

            # 3. Execute and return the first result (or None)
            result = session.execute(stmt).first()
            return result

    def find_row_by_complex_value(self, column_name, list_value):
        with self.SessionLocal() as session:
            column_to_search = getattr(self.my_table.c, column_name)

            # Convert Python list to a JSON string
            json_value = json.dumps(list_value)

            # If the column is JSONB/JSON in the DB:
            stmt = select(self.my_table).where(column_to_search == json_value)

            # OR if you need to cast a text column to JSON for comparison:
            # stmt = select(self.my_table).where(cast(column_to_search, JSON) == list_value)

            result = session.execute(stmt).first()
            return result

    def find_row_by_id(self, row_id):
        # row_id is simply the value of the Primary Key for the specific record you want to target.
        with self.SessionLocal() as session:
            # .get() is the standard way to find by Primary Key
            # If your table was created dynamically as self.my_table:
            return session.get(self.my_table, row_id)

    def list_all_rows(self):
        # row_id is simply the value of the Primary Key for the specific record you want to target.

        with self.SessionLocal() as session:
            # Returns a Python list of all objects in the table
            print(session.query(self.my_table).all())
            return session.query(self.my_table).all()

    def modify_row(self, pk_value, updates: dict):
        with self.SessionLocal() as session:
            pk_column = self.my_table.primary_key.columns.values()[0]

            # Ensure 'mac' is actually a list before sending to Postgres
            if "mac" in updates and isinstance(updates["mac"], str):
                updates["mac"] = [updates["mac"]]  # Wrap it in a list

            stmt = (
                self.my_table.update()
                .where(pk_column == pk_value)
                .values(**updates)
            )
            session.execute(stmt)
            session.commit()

    def upsert_tokenized_data(self, sentence, mac_list):
        with self.SessionLocal() as session:
            # 1. Create the base insert
            stmt = insert(self.my_table).values(
                tokenized_sentence=sentence,
                mac_list=mac_list
            )

            # 2. Define what happens on a Conflict
            # This turns an INSERT into an UPDATE if the sentence exists
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=["tokenized_sentence"],
                set_={"mac_list": mac_list}
            )

            session.execute(upsert_stmt)
            session.commit()

    def delete_row(self, row_id):
        # row_id is simply the value of the Primary Key for the specific record you want to target.
        pk_column = self.my_table.primary_key.columns.values()[0]
        with self.SessionLocal() as session:
            record = session.query(self.my_table).filter(pk_column == row_id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False

    def list_rows_paginated(self, table_obj, limit=20, offset=0):
        """Fetch data in chunks. offset=20 skips the first 20 rows."""
        with self.engine.connect() as conn:
            query = select(table_obj).limit(limit).offset(offset)
            return conn.execute(query).fetchall()

    def check_table_exists(self,cursor, table_name):
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """, (table_name,))
        return cursor.fetchone()[0]








''' Usage Example '''


# class TokenDatabase(Base):
#     __tablename__ = "Shreyas_new1"
#     token = Column(String)
#     user_id = Column(Integer,primary_key=True)
#     mac=Column(ARRAY(MACADDR),default=[])
# # ro=TokenDatabase(token="JNPR-123", user_id=11,mac=["14b3a1130380","14b3a1130680"])
# obj=DatabaseManager("postgresql://user:password@localhost:5432/my_database")
# obj.create_custom_table("Shreyas_new1",{"token": String, "user_id": Integer,"14b3a1130680":ARRAY(MACADDR)},primary_key_defined='user_id')
# obj.session_local()
# # obj.add_row(ro)
# # ro=TokenDatabase(token="HPE", user_id=16,mac=["14b3a1130380"])
# # obj.add_row(ro)
# res=obj.list_all_rows()
# for i in res:
#     for j in i:
#         print(type(j))
# res=obj.find_row_by_column("user_id",150)
# print(res)
# res[2].append("14b3a1130680")
# d={"mac":"14b3a1130685"}
# obj.modify_row(15,d)

# updates_to_make = {
#     "email": "new_email@web.com",
#     "username": "PowerUser99"
# }
#
# db_manager.modify_row(5, updates_to_make)
#
#

