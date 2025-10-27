from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
from datetime import datetime
from database_manager import DatabaseManager
from query_generator import QueryGenerator
from result_visualizer import ResultVisualizer

app = FastAPI(title="AI Query Engine")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
db_manager = DatabaseManager()
query_generator = QueryGenerator()
visualizer = ResultVisualizer()


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    db_connection_id: Optional[str] = None


class DBConnection(BaseModel):
    name: str
    host: str
    port: int
    username: str
    password: str
    database: str
    db_type: str = "postgresql"  # postgresql, mysql, sqlite


class MessageHistory(BaseModel):
    messages: List[ChatMessage]


@app.get("/")
async def root():
    return {"message": "AI Query Engine API", "version": "1.0.0"}


@app.post("/api/databases", response_model=Dict[str, Any])
async def add_database_connection(connection: DBConnection):
    """Add a new database connection"""
    try:
        connection_id = db_manager.add_connection(
            name=connection.name,
            host=connection.host,
            port=connection.port,
            username=connection.username,
            password=connection.password,
            database=connection.database,
            db_type=connection.db_type
        )
        return {"success": True, "connection_id": connection_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/databases", response_model=Dict[str, Any])
async def list_databases():
    """List all database connections"""
    connections = db_manager.list_connections()
    return {"connections": connections}


@app.delete("/api/databases/{connection_id}")
async def remove_database_connection(connection_id: str):
    """Remove a database connection"""
    try:
        db_manager.remove_connection(connection_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/chat", response_model=Dict[str, Any])
async def chat(request: ChatRequest):
    """Handle chat messages and generate SQL queries"""
    try:
        # Validate database connection
        if request.db_connection_id:
            if not db_manager.has_connection(request.db_connection_id):
                raise HTTPException(status_code=404, detail="Database connection not found")
        else:
            # Use default connection if available
            connections = db_manager.list_connections()
            if not connections:
                raise HTTPException(status_code=400, detail="No database connections configured")
            request.db_connection_id = list(connections.keys())[0]
        
        # Get database schema for context
        schema_info = await db_manager.get_schema_info(request.db_connection_id)
        
        # Generate SQL query from natural language
        sql_query = query_generator.generate_sql(
            user_query=request.message,
            schema_info=schema_info
        )
        
        # Execute query
        results = await db_manager.execute_query(request.db_connection_id, sql_query)
        
        # Get visualizations
        visualizations = visualizer.create_visualizations(results)
        
        # Generate explanation
        explanation = query_generator.explain_query(sql_query, request.message)
        
        return {
            "sql_query": sql_query,
            "results": results,
            "visualizations": visualizations,
            "explanation": explanation,
            "connection_id": request.db_connection_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validate-connection")
async def validate_connection(connection: DBConnection):
    """Validate if database connection is working"""
    try:
        is_valid, error_message = await db_manager.test_connection(
            host=connection.host,
            port=connection.port,
            username=connection.username,
            password=connection.password,
            database=connection.database,
            db_type=connection.db_type
        )
        if is_valid:
            return {"valid": True}
        else:
            return {"valid": False, "error": error_message}
    except Exception as e:
        return {"valid": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

