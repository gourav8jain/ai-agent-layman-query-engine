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
        
        # DEBUG: Print tables and query
        print(f"DEBUG: Tables in schema: {tables}")
        print(f"DEBUG: Query: {user_query}")
        
        # Pattern: Detect when multiple tables are mentioned
        # e.g., "get wallets and vccs of organisations"
        mentioned_tables = []
        
        def get_singular(table_name):
            """Convert plural to singular"""
            if table_name.endswith('ies'):
                return table_name[:-3] + 'y'
            elif table_name.endswith('s') and not table_name.endswith('ss'):
                return table_name[:-1]
            return table_name
        
        def fuzzy_match_table(query_text, table_name):
            """Check if query mentions this table with fuzzy matching"""
            query_lower = query_text.lower()
            table_lower = table_name.lower()
            
            # Exact match or part of table name
            if table_lower in query_lower or table_lower in query_lower.split():
                return True
            
            # Check for key components in table name
            keywords = ['wallet', 'vcc', 'org', 'organisation', 'organization', 'account', 'detail']
            for keyword in keywords:
                if keyword in table_lower and keyword in query_lower:
                    return True
            
            # Remove common suffixes for fuzzy matching
            base_table = table_lower.replace('_', ' ').replace('-', ' ')
            base_words = base_table.split()
            for word in base_words:
                if len(word) > 3 and word in query_lower:
                    return True
            
            return False
        
        for table in tables:
            table_lower = table.lower()
            
            # Use fuzzy matching
            if fuzzy_match_table(user_query, table):
                if table not in mentioned_tables:
                    mentioned_tables.append(table)
                    print(f"DEBUG: Fuzzy matched table '{table}'")
            
            # Also try exact/singular/plural matching as fallback
            table_singular = get_singular(table_lower)
            variations = [
                table_lower,
                table_singular,
                table_lower + 's' if not table_lower.endswith('s') else table_lower,
                table_singular + 's',
            ]
            
            for variation in variations:
                if variation and len(variation) > 2 and variation in query_lower:
                    if table not in mentioned_tables:
                        mentioned_tables.append(table)
                        print(f"DEBUG: Matched table '{table}' using variation '{variation}'")
        
        # If multiple tables are mentioned, try to create a JOIN
        if len(mentioned_tables) >= 2:
            print(f"DEBUG: Found multiple tables: {mentioned_tables}")
            return self._generate_join_query(mentioned_tables, schema_info, query_lower)
        
        print(f"DEBUG: Mentioned tables: {mentioned_tables}")
        
        # Pattern: "show me all X" or "list all X"
        if re.search(r'show\s+(me\s+)?all|list\s+all|get\s+all|get\s+me', query_lower):
            # Check if multiple tables are mentioned BEFORE returning
            potential_tables = []
            for table in tables:
                # Use fuzzy matching
                if fuzzy_match_table(user_query, table):
                    if table not in potential_tables:
                        potential_tables.append(table)
                        print(f"DEBUG: potential_tables added (fuzzy): {table}")
                
                # Also try exact matching as backup
                table_lower = table.lower()
                table_singular = get_singular(table_lower)
                
                if table not in potential_tables:
                    matches = False
                    # Exact match or singular/plural variants
                    if table_lower in query_lower or table_singular in query_lower:
                        matches = True
                    # Check if singular table name matches plural in query
                    elif table_singular + 's' in query_lower or table_lower + 's' in query_lower:
                        matches = True
                    # Check if plural table name matches singular in query
                    elif table_lower.endswith('s') and table_lower[:-1] in query_lower:
                        matches = True
                    
                    if matches:
                        potential_tables.append(table)
                        print(f"DEBUG: potential_tables added: {table}")
            
            # If we found multiple tables, generate JOIN
            print(f"DEBUG: potential_tables found: {potential_tables}")
            if len(potential_tables) >= 2:
                print(f"DEBUG: Generating JOIN query for: {potential_tables}")
                return self._generate_join_query(potential_tables, schema_info, query_lower)
            
            # Otherwise, return first matching table
            if potential_tables:
                return f"SELECT * FROM {potential_tables[0]} LIMIT 100;"
        
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
    
    def _generate_join_query(self, tables: list, schema_info: Dict[str, Any], query: str) -> str:
        """Generate a JOIN query for multiple tables"""
        
        if len(tables) < 2:
            return f"SELECT * FROM {tables[0]} LIMIT 100;"
        
        # Try to find relationships between tables
        # Look for foreign key patterns: table_id, org_id, etc.
        
        # Build FROM clause with JOINs
        from_clause = f"FROM {tables[0]}"
        join_clauses = []
        
        # Get columns from each table
        main_table_cols = [col['name'] for col in schema_info.get(tables[0], [])]
        
        for i, table in enumerate(tables[1:], 1):
            # Try to find relationship
            # Option 1: table_id in main table
            fk_pattern = f"{table}_id"
            rfk_pattern = f"{tables[0]}_id"
            
            prev_table_cols = [col['name'] for col in schema_info.get(tables[i-1], [])]
            current_table_cols = [col['name'] for col in schema_info.get(table, [])]
            
            # Check if there's a foreign key
            if fk_pattern in prev_table_cols or fk_pattern in current_table_cols:
                if fk_pattern in prev_table_cols:
                    # Previous table has FK to current
                    join_clauses.append(f"JOIN {table} ON {tables[i-1]}.{fk_pattern} = {table}.id")
                else:
                    # Current table has FK to previous
                    join_clauses.append(f"JOIN {table} ON {tables[i-1]}.id = {table}.{fk_pattern}")
            elif rfk_pattern in current_table_cols:
                # Current table has reverse FK
                join_clauses.append(f"JOIN {table} ON {tables[i-1]}.id = {table}.{rfk_pattern}")
            else:
                # Default: try to find any matching column
                common_cols = set(prev_table_cols) & set(current_table_cols)
                if common_cols:
                    join_col = list(common_cols)[0]
                    join_clauses.append(f"JOIN {table} ON {tables[i-1]}.{join_col} = {table}.{join_col}")
                else:
                    # Fallback: assume first matching pattern
                    join_clauses.append(f"JOIN {table} ON {tables[i-1]}.id = {table}.id")
        
        join_str = " ".join(join_clauses) if join_clauses else ""
        
        return f"SELECT {tables[0]}.*, {', '.join([f'{t}.*' for t in tables[1:]])} {from_clause} {join_str} LIMIT 100;"
    
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

