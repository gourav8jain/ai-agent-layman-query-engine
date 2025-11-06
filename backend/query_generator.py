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
            """Check if query mentions this table with fuzzy matching - ULTRA STRICT version"""
            query_lower = query_text.lower()
            table_lower = table_name.lower()
            
            # ONLY match the exact core business tables
            # This prevents ALL over-matching
            
            # Check for wallet - ONLY "wallets" table
            if 'wallet' in query_lower and table_lower == 'wallets':
                return True
            
            # Check for vcc - ONLY "vccs" table
            if 'vcc' in query_lower and table_lower == 'vccs':
                return True
            
            # Check for organisation/organization - ONLY "organizations" table
            if ('org' in query_lower or 'organisation' in query_lower or 'organization' in query_lower) and table_lower == 'organizations':
                return True
            
            return False
        
        # Extract core business tables (wallets, vccs, organizations) from query
        core_tables = []
        query_lower = user_query.lower()
        
        # Check for wallet references
        if 'wallet' in query_lower:
            if 'wallets' in [t.lower() for t in tables]:
                core_tables.append('wallets')
                print(f"DEBUG: Added wallets to core tables")
        
        # Check for vcc references  
        if 'vcc' in query_lower:
            if 'vccs' in [t.lower() for t in tables]:
                core_tables.append('vccs')
                print(f"DEBUG: Added vccs to core tables")
        
        # Check for organization references
        if 'org' in query_lower or 'organisation' in query_lower or 'organization' in query_lower:
            if 'organizations' in [t.lower() for t in tables]:
                core_tables.append('organizations')
                print(f"DEBUG: Added organizations to core tables")
        
        # Only proceed with JOIN if we have at least 2 core tables
        print(f"DEBUG: Core tables detected: {core_tables}")
        if len(core_tables) >= 2:
            print(f"DEBUG: Calling _generate_join_query with: {core_tables}")
            return self._generate_join_query(core_tables, schema_info, query_lower)
        
        # Otherwise use mentioned_tables for single table queries
        mentioned_tables = core_tables
        
        print(f"DEBUG: Mentioned tables: {mentioned_tables}")
        
        # Check for filter conditions FIRST (before generating query)
        where_conditions = self._extract_conditions(user_query, schema_info, core_tables if core_tables else mentioned_tables)
        print(f"DEBUG: Extracted WHERE conditions: {where_conditions}")
        
        # Pattern: "show me all X" or "list all X"
        if re.search(r'show\s+(me\s+)?all|list\s+all|get\s+all|get\s+me', query_lower):
            # Skip fuzzy matching - use core_tables if available
            if len(core_tables) >= 1:
                print(f"DEBUG: Using core_tables for query")
                # Return the appropriate query based on core_tables
                if len(core_tables) == 1:
                    table_name = core_tables[0]
                    if where_conditions:
                        return f"SELECT * FROM {table_name} WHERE {where_conditions} LIMIT 100;"
                    return f"SELECT * FROM {table_name} LIMIT 100;"
                elif len(core_tables) >= 2:
                    join_query = self._generate_join_query(core_tables, schema_info, query_lower)
                    if where_conditions:
                        # Add WHERE clause to JOIN query
                        join_query = join_query.rstrip(';')
                        return f"{join_query} WHERE {where_conditions};"
                    return join_query
            
            # Only if no core_tables found, use fallback
            potential_tables = core_tables.copy()
            table_scores = {}
            
            for table in tables:
                # Only check if it's an exact core table
                table_lower = table.lower()
                if table_lower == 'wallets' and 'wallet' in query_lower:
                    if table not in potential_tables:
                        potential_tables.append(table)
                        table_scores[table] = 100
                        print(f"DEBUG: Added {table} to potential_tables")
                elif table_lower == 'vccs' and 'vcc' in query_lower:
                    if table not in potential_tables:
                        potential_tables.append(table)
                        table_scores[table] = 100
                        print(f"DEBUG: Added {table} to potential_tables")
                elif table_lower == 'organizations' and ('org' in query_lower or 'organisation' in query_lower or 'organization' in query_lower):
                    if table not in potential_tables:
                        potential_tables.append(table)
                        table_scores[table] = 100
                        print(f"DEBUG: Added {table} to potential_tables")
                
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
                # Sort by score (highest first) to prioritize business tables
                sorted_tables = sorted(potential_tables, key=lambda t: table_scores.get(t, 0), reverse=True)
                return self._generate_join_query(sorted_tables, schema_info, query_lower)
            
            # Otherwise, return first matching table
            if potential_tables:
                # If we only found 1 table but query mentions multiple entities, 
                # try harder to find related tables
                if len(potential_tables) == 1 and ('wallet' in query_lower or 'vcc' in query_lower or 'organisation' in query_lower or 'organization' in query_lower):
                    # Try to find additional related tables
                    for table in tables:
                        table_lower = table.lower()
                        if table not in potential_tables:
                            # Look for wallet-related tables
                            if 'wallet' in query_lower and 'wallet' in table_lower:
                                potential_tables.append(table)
                                print(f"DEBUG: Added additional wallet table: {table}")
                            # Look for vcc-related tables
                            elif 'vcc' in query_lower and 'vcc' in table_lower:
                                potential_tables.append(table)
                                print(f"DEBUG: Added additional vcc table: {table}")
                            # Look for organisation-related tables
                            elif ('organisation' in query_lower or 'organization' in query_lower or 'oragnisation' in query_lower) and ('org' in table_lower or 'organisation' in table_lower or 'organization' in table_lower):
                                potential_tables.append(table)
                                print(f"DEBUG: Added additional org table: {table}")
                    
                    # Try again with updated tables
                    if len(potential_tables) >= 2:
                        print(f"DEBUG: Now generating JOIN query for: {potential_tables}")
                        # Sort by score (highest first)
                        sorted_tables = sorted(potential_tables, key=lambda t: table_scores.get(t, 0), reverse=True)
                        return self._generate_join_query(sorted_tables, schema_info, query_lower)
                
                # Sort tables by score and return best match
                if potential_tables:
                    sorted_tables = sorted(potential_tables, key=lambda t: table_scores.get(t, 0), reverse=True)
                    table_name = sorted_tables[0]
                    print(f"DEBUG: Using best table (by score): {table_name}")
                    if where_conditions:
                        return f"SELECT * FROM {table_name} WHERE {where_conditions} LIMIT 100;"
                    return f"SELECT * FROM {table_name} LIMIT 100;"
        
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
                    conditions = self._extract_conditions(user_query, schema_info, [table])
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
        """Generate a JOIN query for wallets, vccs, and organizations only"""
        
        # Remove duplicates and filter to only our 3 core tables
        tables = list(dict.fromkeys(tables))
        core_tables = []
        
        for table in tables:
            table_lower = table.lower()
            if table_lower in ['wallets', 'vccs', 'organizations']:
                core_tables.append(table)
        
        # If not enough core tables, return simple query
        if len(core_tables) < 2:
            if core_tables:
                return f"SELECT * FROM {core_tables[0]} LIMIT 100;"
            return f"SELECT * FROM {tables[0]} LIMIT 100;"
        
        print(f"DEBUG: Generating JOIN for CORE tables: {core_tables}")
        
        # Determine main table (wallets)
        main_table = 'wallets' if 'wallets' in core_tables else core_tables[0]
        
        # Build fixed aliases - NO DUPLICATES
        aliases = {main_table: 'w'}
        used_aliases = {'w'}
        
        for table in core_tables:
            if table == main_table:
                continue
            
            table_lower = table.lower()
            if 'org' in table_lower or 'organisation' in table_lower or 'organization' in table_lower:
                if 'o' not in used_aliases:
                    aliases[table] = 'o'
                    used_aliases.add('o')
                else:
                    # Skip if already used
                    print(f"DEBUG: Skipping {table} - alias 'o' already used")
                    continue
            elif 'vcc' in table_lower:
                if 'v' not in used_aliases:
                    aliases[table] = 'v'
                    used_aliases.add('v')
                else:
                    # Skip if already used
                    print(f"DEBUG: Skipping {table} - alias 'v' already used")
                    continue
        
        from_clause = f"FROM {main_table} {aliases[main_table]}"
        join_clauses = []
        
        # Build SELECT with only unique aliases
        select_cols = []
        for table, alias in aliases.items():
            select_cols.append(f"{alias}.*")
        
        # Build JOIN clauses
        for table in core_tables:
            if table == main_table or table not in aliases:
                continue
            
            table_alias = aliases[table]
            
            # Organizations join
            if 'org' in table.lower() or 'organisation' in table.lower() or 'organization' in table.lower():
                join_clauses.append(f"INNER JOIN {table} {table_alias} ON w.organization_id = {table_alias}.organization_id")
                print(f"DEBUG: Added org join for {table}")
            
            # VCCs join
            elif 'vcc' in table.lower():
                join_clauses.append(f"INNER JOIN {table} {table_alias} ON {table_alias}.funding_wallet_id = w.funding_wallet_id")
                print(f"DEBUG: Added vcc join for {table}")
        
        join_str = " ".join(join_clauses)
        
        query_sql = f"SELECT {', '.join(select_cols)} {from_clause} {join_str} LIMIT 100;"
        print(f"DEBUG: Final query: {query_sql}")
        return query_sql
    
    def _extract_conditions(self, query: str, schema_info: Dict[str, Any], tables: list) -> str:
        """Extract WHERE conditions from natural language"""
        print(f"DEBUG: _extract_conditions called with query: '{query}', tables: {tables}")
        query_lower = query.lower()
        conditions = []
        
        # Get the first table to check columns
        if not tables:
            print(f"DEBUG: No tables provided, returning empty conditions")
            return ""
        
        table_name = tables[0] if isinstance(tables, list) else tables
        print(f"DEBUG: Using table: '{table_name}'")
        schema_columns = schema_info.get(table_name, [])
        print(f"DEBUG: Schema columns for {table_name}: {len(schema_columns)} columns")
        column_names = [col['name'].lower() if isinstance(col, dict) else str(col).lower() for col in schema_columns]
        print(f"DEBUG: Column names: {column_names[:5]}...")  # Print first 5 columns
        
        # Pattern: "name matches with X" or "name matches X" or "name like X"
        # Also handle: "matches the name as X" or "which matches name as X"
        match_patterns = [
            # Standard: "name matches with X" or "name matches X"
            r'(?:of\s+)?(\w+)\s+matches\s+(?:with\s+)?(["\']?)(\w+)',
            # Reverse: "matches the name as X" or "matches name as X"
            r'matches\s+(?:the\s+)?(\w+)\s+as\s+(["\']?)(\w+)',
            # Reverse with "with": "matches the name with X"
            r'matches\s+(?:the\s+)?(\w+)\s+with\s+(["\']?)(\w+)',
            # Other patterns
            r'(?:of\s+)?(\w+)\s+like\s+(["\']?)(\w+)',
            r'(?:of\s+)?(\w+)\s+contains\s+(["\']?)(\w+)',
            r'(?:of\s+)?(\w+)\s+equals\s+(["\']?)(\w+)',
            r'(?:of\s+)?(\w+)\s+is\s+(["\']?)(\w+)',
            r'(?:of\s+)?(\w+)\s+=\s+(["\']?)(\w+)',
        ]
        
        for pattern in match_patterns:
            matches = re.finditer(pattern, query_lower, re.IGNORECASE)
            for match in matches:
                print(f"DEBUG: Pattern matched: {pattern}")
                print(f"DEBUG: Match groups: {match.groups()}")
                column_candidate = match.group(1).lower()
                # For patterns with 3 groups, value is group 3, otherwise group 2
                if len(match.groups()) >= 3:
                    value = match.group(3).strip("'\"")
                else:
                    value = match.group(2).strip("'\"")
                print(f"DEBUG: Extracted column_candidate: '{column_candidate}', value: '{value}'")
                
                # Find matching column name
                matched_column = None
                for col in column_names:
                    col_clean = col.lower().replace('_', ' ')
                    # Check if column_candidate matches the column name
                    # e.g., "name" should match "organization_name" or "name"
                    if (column_candidate == col or 
                        column_candidate in col_clean or 
                        col_clean.endswith(column_candidate) or
                        col.endswith('_' + column_candidate)):
                        matched_column = col
                        print(f"DEBUG: Matched column '{column_candidate}' to '{col}'")
                        break
                
                if matched_column:
                    # Use ILIKE for case-insensitive matching (PostgreSQL)
                    if 'matches' in match.group(0) or 'like' in match.group(0) or 'contains' in match.group(0):
                        conditions.append(f"{matched_column} ILIKE '%{value}%'")
                    else:
                        conditions.append(f"{matched_column} = '{value}'")
                    print(f"DEBUG: Extracted condition: {matched_column} matches '{value}'")
        
        print(f"DEBUG: Total conditions found: {len(conditions)}")
        if conditions:
            print(f"DEBUG: Final WHERE conditions: {' AND '.join(conditions)}")
        
        # Pattern: "where X = Y" explicit
        if 'where' in query_lower:
            where_match = re.search(r'where\s+(\w+)\s*=\s*(["\']?)(\w+)\2', query_lower)
            if where_match:
                col = where_match.group(1).lower()
                val = where_match.group(3)
                for column in column_names:
                    if col in column.lower() or column.lower() in col:
                        conditions.append(f"{column} = '{val}'")
                        break
        
        # Look for common patterns
        if 'status' in query_lower:
            # Try to find status value
            if 'active' in query_lower:
                status_col = next((col for col in column_names if 'status' in col or col == 'is_active'), 'status')
                conditions.append(f"{status_col} = 'active'")
            elif 'inactive' in query_lower:
                status_col = next((col for col in column_names if 'status' in col or col == 'is_active'), 'status')
                conditions.append(f"{status_col} = 'inactive'")
        
        if 'id' in query_lower:
            # Try to extract numeric ID
            numbers = re.findall(r'\bid\s*[=:]\s*(\d+)', query_lower)
            if not numbers:
                numbers = re.findall(r'\b(\d+)\b', query)
            if numbers:
                id_col = next((col for col in column_names if 'id' in col), 'id')
                conditions.append(f"{id_col} = {numbers[0]}")
        
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

