# pip install sqlalchemy psycopg2-binary

from sqlalchemy import create_engine, Column, Integer, String, JSON, MetaData, Table
from sqlalchemy import select, insert, update, delete, text

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

    # NEW: Create a brand new table with a custom name
    def create_custom_table(self, table_name, columns_dict,primary_key_defined=False):
        """
        Creates a table dynamically.
        Example: columns_dict = {"name": String, "age": Integer}
        """
        # Creating an empty canvas
        self.metadata = MetaData()

        # To always add a Primary Key 'id' automatically if it is not defined by user while creating
        if(not primary_key_defined):
            cols = [Column('id', Integer, primary_key=True)]
        else:
            cols=[]
        for name, dtype in columns_dict.items():
            if(primary_key_defined==name):
                cols.append(Column(name, dtype, primary_key=True))
            else:
                cols.append(Column(name, dtype))

        #
        self.my_table = Table(table_name, self.metadata, *cols)

        # Creates all the tables that are defined under metadata
        self.metadata.create_all(self.engine)
        print("A Table named : ",table_name," has been created successfully.")

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

    def find_row_by_id(self, row_id):
        # row_id is simply the value of the Primary Key for the specific record you want to target.
        with self.SessionLocal() as session:
            # Returns a single object or None if not found
            return session.query(self.my_table).filter(self.my_table.id == row_id).first()

    def list_all_rows(self):
        # row_id is simply the value of the Primary Key for the specific record you want to target.

        with self.SessionLocal() as session:
            # Returns a Python list of all objects in the table
            print(session.query(self.my_table).all())
            return session.query(self.my_table).all()

    def modify_row(self, row_id, updates: dict):
        # row_id is simply the value of the Primary Key for the specific record you want to target.

        with self.SessionLocal() as session:
            record = session.query(self.my_table).filter(self.my_table.id == row_id).first()
            if record:
                for key, value in updates.items():
                    setattr(record, key, value)  # Dynamically set column values
                session.commit()
                return True
            return False

    def delete_row(self, row_id):
        # row_id is simply the value of the Primary Key for the specific record you want to target.

        with self.SessionLocal() as session:
            record = session.query(self.my_table).filter(self.my_table.id == row_id).first()
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








''' Usage Example '''

'''
class TokenDatabase(Base):
    __tablename__ = "Shreyas"
    token = Column(String)
    user_id = Column(Integer,primary_key=True)
#ro=TokenDatabase(token="JNPR-123", user_id=10)
obj=DatabaseManager("postgresql://user:password@localhost:5432/my_database")
obj.create_custom_table("Shreyas",{"token": String, "user_id": Integer},primary_key_defined='user_id')
obj.session_local()
#obj.add_row(ro)
ro=TokenDatabase(token="HPE", user_id=13)
obj.add_row(ro)
obj.list_all_rows()

'''


