import re
from typing import Dict, Any


class QueryGenerator:
    """Convert natural language to SQL queries"""
    
    def __init__(self):
        self.conversation_history = []
    
    def generate_sql(self, user_query: str, schema_info: Dict[str, Any]) -> str:
        """Generate SQL query from natural language"""
        
        # Simple pattern-based approach
        # In production, you'd use an LLM like OpenAI GPT-4 or local LLM
        
        query_lower = user_query.lower()
        
        # Extract table and column information from schema
        tables = list(schema_info.keys())
        
        # Pattern: "show me all X" or "list all X"
        if re.search(r'show\s+(me\s+)?all|list\s+all|get\s+all', query_lower):
            # Try to find matching table
            for table in tables:
                if table.lower() in query_lower:
                    return f"SELECT * FROM {table} LIMIT 100;"
        
        # Pattern: "count X"
        if 'count' in query_lower:
            for table in tables:
                if table.lower() in query_lower:
                    return f"SELECT COUNT(*) as count FROM {table};"
        
        # Pattern: "find X where Y = Z" or "filter X"
        if 'where' in query_lower or 'filter' in query_lower:
            # Extract table name
            for table in tables:
                if table.lower() in query_lower:
                    # Extract potential conditions
                    conditions = self._extract_conditions(user_query, schema_info.get(table, []))
                    if conditions:
                        return f"SELECT * FROM {table} WHERE {conditions} LIMIT 100;"
                    else:
                        return f"SELECT * FROM {table} LIMIT 100;"
        
        # Pattern: "join" or "combine"
        if 'join' in query_lower or 'combine' in query_lower:
            if len(tables) >= 2:
                # Simple join on first two tables
                table1, table2 = tables[0], tables[1]
                return f"SELECT * FROM {table1} JOIN {table2} ON {table1}.id = {table2}.{table1}_id LIMIT 100;"
        
        # Pattern: "order by" or "sort by"
        if 'sort' in query_lower or 'order' in query_lower:
            for table in tables:
                if table.lower() in query_lower:
                    # Try to extract column name
                    columns = [col['name'] for col in schema_info.get(table, [])]
                    order_col = 'id' if 'id' in columns else columns[0] if columns else 'id'
                    order_dir = 'DESC' if 'desc' in query_lower else 'ASC'
                    return f"SELECT * FROM {table} ORDER BY {order_col} {order_dir} LIMIT 100;"
        
        # Pattern: "group by" or "aggregate"
        if 'group' in query_lower or 'aggregate' in query_lower:
            for table in tables:
                if table.lower() in query_lower:
                    # Try to find a likely grouping column
                    columns = [col['name'] for col in schema_info.get(table, [])]
                    # Look for category-type columns
                    group_cols = [c for c in columns if any(x in c.lower() for x in ['type', 'category', 'status', 'group'])]
                    if group_cols:
                        group_col = group_cols[0]
                        return f"SELECT {group_col}, COUNT(*) as count FROM {table} GROUP BY {group_col};"
        
        # Default: return first table
        if tables:
            return f"SELECT * FROM {tables[0]} LIMIT 100;"
        
        return "SELECT 1;"
    
    def _extract_conditions(self, query: str, schema_columns: list) -> str:
        """Extract WHERE conditions from natural language"""
        # Very simple extraction - in production, use LLM
        conditions = []
        
        # Look for common patterns
        if 'status' in query.lower():
            # Try to find status value
            if 'active' in query.lower():
                conditions.append("status = 'active'")
            elif 'inactive' in query.lower():
                conditions.append("status = 'inactive'")
        
        if 'id' in query.lower():
            # Try to extract numeric ID
            numbers = re.findall(r'\d+', query)
            if numbers:
                conditions.append(f"id = {numbers[0]}")
        
        return " AND ".join(conditions) if conditions else ""
    
    def explain_query(self, sql_query: str, original_query: str) -> str:
        """Generate an explanation of the SQL query"""
        explanation = f"The query '{original_query}' was translated to:\n\n"
        explanation += f"```sql\n{sql_query}\n```\n\n"
        
        # Add basic explanation
        if 'SELECT' in sql_query.upper():
            explanation += "This query retrieves data from the database. "
        
        if 'WHERE' in sql_query.upper():
            explanation += "The WHERE clause filters the results based on specific conditions. "
        
        if 'JOIN' in sql_query.upper():
            explanation += "The JOIN combines data from multiple tables. "
        
        if 'GROUP BY' in sql_query.upper():
            explanation += "The GROUP BY clause groups rows with the same values. "
        
        if 'ORDER BY' in sql_query.upper():
            explanation += "The ORDER BY clause sorts the results. "
        
        if 'LIMIT' in sql_query.upper():
            explanation += "The LIMIT clause restricts the number of results returned. "
        
        return explanation

