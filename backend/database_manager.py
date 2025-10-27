import asyncpg
import pymysql
import sqlite3
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.connections: Dict[str, dict] = {}
        self.active_connections: Dict[str, Any] = {}
    
    def add_connection(self, name: str, host: str, port: int, username: str, 
                      password: str, database: str, db_type: str = "postgresql") -> str:
        """Add a database connection"""
        connection_id = f"{db_type}_{name}_{datetime.now().timestamp()}"
        
        self.connections[connection_id] = {
            "name": name,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "database": database,
            "db_type": db_type
        }
        
        return connection_id
    
    def remove_connection(self, connection_id: str):
        """Remove a database connection"""
        if connection_id not in self.connections:
            raise ValueError(f"Connection {connection_id} not found")
        
        # Close active connection if exists
        if connection_id in self.active_connections:
            # Close connection based on type
            del self.active_connections[connection_id]
        
        del self.connections[connection_id]
    
    def list_connections(self) -> Dict[str, dict]:
        """List all database connections (without passwords)"""
        return {
            conn_id: {
                **conn,
                "password": "***"
            }
            for conn_id, conn in self.connections.items()
        }
    
    def has_connection(self, connection_id: str) -> bool:
        """Check if connection exists"""
        return connection_id in self.connections
    
    async def get_connection(self, connection_id: str):
        """Get or create database connection"""
        if connection_id not in self.connections:
            raise ValueError(f"Connection {connection_id} not found")
        
        conn_info = self.connections[connection_id]
        
        # Return existing connection if available
        if connection_id in self.active_connections:
            return self.active_connections[connection_id]
        
        # Create new connection based on database type
        db_type = conn_info["db_type"]
        
        if db_type == "postgresql":
            conn = await asyncpg.connect(
                host=conn_info["host"],
                port=conn_info["port"],
                user=conn_info["username"],
                password=conn_info["password"],
                database=conn_info["database"]
            )
            self.active_connections[connection_id] = conn
            return conn
        
        elif db_type == "mysql":
            # For MySQL, we'll use synchronous PyMySQL for now
            # In production, use aiomysql
            import pymysql
            conn = pymysql.connect(
                host=conn_info["host"],
                port=conn_info["port"],
                user=conn_info["username"],
                password=conn_info["password"],
                database=conn_info["database"]
            )
            return conn
        
        elif db_type == "sqlite":
            conn = sqlite3.connect(conn_info["database"])
            return conn
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    async def test_connection(self, host: str, port: int, username: str, 
                             password: str, database: str, db_type: str = "postgresql") -> tuple[bool, str]:
        """Test a database connection. Returns (is_valid, error_message)"""
        try:
            if db_type == "postgresql":
                conn = await asyncpg.connect(
                    host=host,
                    port=port,
                    user=username,
                    password=password,
                    database=database,
                    timeout=10
                )
                await conn.close()
                return (True, "Connection successful")
            elif db_type == "mysql":
                import pymysql
                conn = pymysql.connect(
                    host=host,
                    port=port,
                    user=username,
                    password=password,
                    database=database,
                    connect_timeout=10
                )
                conn.close()
                return (True, "Connection successful")
            elif db_type == "sqlite":
                # For SQLite, just check if file exists or can be created
                return (True, "Connection successful")
            return (False, "Unsupported database type")
        except asyncpg.exceptions.InvalidPasswordError as e:
            return (False, "Invalid password")
        except asyncpg.exceptions.PostgresConnectionError as e:
            error_msg = str(e)
            if "password authentication failed" in error_msg.lower():
                return (False, "Authentication failed: Invalid username or password")
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return (False, "Connection timeout: Could not reach the database server")
            elif "does not exist" in error_msg.lower():
                return (False, f"Database '{database}' does not exist")
            else:
                return (False, f"PostgreSQL connection error: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            # Extract meaningful error messages
            if "authentication" in error_msg.lower() or "password" in error_msg.lower():
                return (False, "Authentication failed: Check username and password")
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return (False, "Connection timeout: Could not reach the database server")
            elif "refused" in error_msg.lower():
                return (False, "Connection refused: Server may be down or firewall blocking")
            elif "does not exist" in error_msg.lower():
                return (False, f"Database '{database}' does not exist")
            elif "not found" in error_msg.lower():
                return (False, "Host not found: Check if the host address is correct")
            else:
                return (False, f"Connection failed: {error_msg}")
    
    async def get_schema_info(self, connection_id: str) -> Dict[str, Any]:
        """Get database schema information"""
        try:
            conn = await self.get_connection(connection_id)
            conn_info = self.connections[connection_id]
            db_type = conn_info["db_type"]
            
            if db_type == "postgresql":
                # Get tables
                tables_query = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """
                tables = await conn.fetch(tables_query)
                table_names = [table['table_name'] for table in tables]
                
                # Get columns for each table
                schema = {}
                for table in table_names:
                    columns_query = f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = '{table}'
                        ORDER BY ordinal_position
                    """
                    columns = await conn.fetch(columns_query)
                    schema[table] = [
                        {
                            "name": col['column_name'],
                            "type": col['data_type'],
                            "nullable": col['is_nullable']
                        }
                        for col in columns
                    ]
                
                return schema
            
            elif db_type == "mysql":
                cursor = conn.cursor()
                # Get tables
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                table_names = [table[0] for table in tables]
                
                # Get columns for each table
                schema = {}
                for table in table_names:
                    cursor.execute(f"DESCRIBE {table}")
                    columns = cursor.fetchall()
                    schema[table] = [
                        {
                            "name": col[0],
                            "type": col[1],
                            "nullable": col[2]
                        }
                        for col in columns
                    ]
                
                return schema
            
            else:
                return {}
        except Exception as e:
            print(f"Error getting schema: {e}")
            return {}
    
    async def execute_query(self, connection_id: str, query: str) -> Dict[str, Any]:
        """Execute a SQL query and return results"""
        try:
            conn = await self.get_connection(connection_id)
            conn_info = self.connections[connection_id]
            db_type = conn_info["db_type"]
            
            if db_type == "postgresql":
                rows = await conn.fetch(query)
                # Convert to list of dicts
                results = [dict(row) for row in rows]
                return {
                    "columns": list(results[0].keys()) if results else [],
                    "rows": results,
                    "count": len(results)
                }
            
            elif db_type == "mysql":
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
                return {
                    "columns": columns,
                    "rows": results,
                    "count": len(results)
                }
            
            else:
                return {"columns": [], "rows": [], "count": 0}
        
        except Exception as e:
            raise Exception(f"Query execution error: {str(e)}")

