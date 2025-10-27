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
            
            # Extract keywords from query
            query_words = query_lower.split()
            important_words = []
            for word in query_words:
                # Skip common words
                if word not in ['get', 'me', 'all', 'the', 'of', 'and', 'or', 'a', 'an', 'is', 'are', 'was', 'were']:
                    important_words.append(word)
            
            # Split table name by underscores/dashes
            table_parts = table_lower.replace('_', ' ').replace('-', ' ').split()
            
            # Check if any table part matches any important word
            for part in table_parts:
                if len(part) > 2:  # Minimum 3 char words
                    for word in important_words:
                        # Check exact match or substring
                        if part in word or word in part:
                            return True
            
            # Check for key components in table name
            keywords = ['wallet', 'vcc', 'org', 'organisation', 'organization', 'account', 'detail', 'organizations', 'oragnisations']
            for keyword in keywords:
                if keyword in table_lower and keyword in query_lower:
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
            table_scores = {}
            
            for table in tables:
                # Use fuzzy matching with scoring
                if fuzzy_match_table(user_query, table):
                    # Calculate relevance score
                    score = 0
                    table_lower = table.lower()
                    
                    # High priority for exact business terms
                    if 'wallet' in table_lower and 'wallet' in query_lower:
                        score += 100
                    if 'vcc' in table_lower and 'vcc' in query_lower:
                        score += 100
                    if ('org' in table_lower or 'organisation' in table_lower or 'organization' in table_lower) and ('org' in query_lower or 'organisation' in query_lower or 'organization' in query_lower):
                        score += 100
                    
                    # Lower priority for generic/technical tables
                    if 'account' in table_lower or 'detail' in table_lower:
                        score -= 50
                    
                    table_scores[table] = score
                    
                    if table not in potential_tables:
                        potential_tables.append(table)
                        print(f"DEBUG: potential_tables added (fuzzy): {table} (score: {score})")
                
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
                    print(f"DEBUG: Using best table (by score): {sorted_tables[0]}")
                    return f"SELECT * FROM {sorted_tables[0]} LIMIT 100;"
        
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
        
        # Remove duplicate tables while preserving order
        tables = list(dict.fromkeys(tables))
        
        if len(tables) < 2:
            return f"SELECT * FROM {tables[0]} LIMIT 100;"
        
        print(f"DEBUG: Generating JOIN for tables: {tables}")
        
        # Determine the main table (usually wallets if present)
        main_table = None
        for table in tables:
            if 'wallet' in table.lower():
                main_table = table
                break
        
        if not main_table:
            main_table = tables[0]
        
        # Remove duplicates
        other_tables = [t for t in tables if t != main_table]
        other_tables = list(dict.fromkeys(other_tables))  # Remove duplicates while preserving order
        
        # Build FROM clause with unique aliases
        used_aliases = {'w'}  # Track used aliases
        aliases = {main_table: 'w'}  # Wallet is 'w'
        
        for i, table in enumerate(other_tables):
            if 'org' in table.lower() or 'organisation' in table.lower() or 'organization' in table.lower():
                alias = 'o' if 'o' not in used_aliases else chr(97 + i)
            elif 'vcc' in table.lower():
                alias = 'v' if 'v' not in used_aliases else chr(97 + i)
            else:
                # Generate unique alias starting from 'a'
                alias = chr(97 + i)
            
            # If alias is already used, find next available
            while alias in used_aliases:
                alias = chr(ord(alias) + 1)
            
            aliases[table] = alias
            used_aliases.add(alias)
        
        from_clause = f"FROM {main_table} {aliases[main_table]}"
        join_clauses = []
        
        # Build JOIN clauses with proper relationships
        for table in other_tables:
            table_alias = aliases[table]
            prev_tables = [main_table] + other_tables[:other_tables.index(table)]
            
            # Get columns for this table
            table_cols = [col['name'] for col in schema_info.get(table, [])]
            
            # Try to find the best join condition
            join_condition = None
            
            # Special handling for organizations joining to wallets
            if 'org' in table.lower() or 'organisation' in table.lower() or 'organization' in table.lower():
                # Look for organization_id in wallet table
                wallet_table = main_table if 'wallet' in main_table.lower() else None
                if wallet_table:
                    wallet_cols = [col['name'] for col in schema_info.get(wallet_table, [])]
                    if 'organization_id' in wallet_cols:
                        # Join wallets to organizations
                        join_condition = f"INNER JOIN {table} {table_alias} ON {aliases[wallet_table]}.organization_id = {table_alias}.organization_id"
            
            # Special handling for vccs joining to wallets
            elif 'vcc' in table.lower():
                # Look for funding_wallet_id or wallet_id in vcc table
                vcc_cols = table_cols
                if 'funding_wallet_id' in vcc_cols:
                    # Join vccs to wallets via funding_wallet_id
                    join_condition = f"INNER JOIN {table} {table_alias} ON {table_alias}.funding_wallet_id = {aliases[main_table]}.funding_wallet_id"
                elif 'wallet_id' in vcc_cols:
                    # Join vccs to wallets via wallet_id
                    join_condition = f"INNER JOIN {table} {table_alias} ON {table_alias}.wallet_id = {aliases[main_table]}.wallet_id"
            
            # Generic foreign key matching
            if not join_condition:
                for prev_table in prev_tables:
                    prev_cols = [col['name'] for col in schema_info.get(prev_table, [])]
                    
                    # Check if current table has FK to previous
                    fk_pattern = f"{prev_table}_id"
                    if fk_pattern in table_cols:
                        join_condition = f"INNER JOIN {table} {table_alias} ON {table_alias}.{fk_pattern} = {aliases[prev_table]}.id"
                        break
                    
                    # Check if previous table has FK to current
                    if fk_pattern in prev_cols:
                        join_condition = f"INNER JOIN {table} {table_alias} ON {aliases[prev_table]}.{fk_pattern} = {table_alias}.id"
                        break
            
            # Fallback: use common column names
            if not join_condition and prev_tables:
                prev_cols = [col['name'] for col in schema_info.get(prev_tables[-1], [])]
                common_cols = set(prev_cols) & set(table_cols)
                if common_cols:
                    join_col = list(common_cols)[0]
                    prev_alias = aliases[prev_tables[-1]]
                    join_condition = f"INNER JOIN {table} {table_alias} ON {prev_alias}.{join_col} = {table_alias}.{join_col}"
            
            # Final fallback
            if not join_condition and prev_tables:
                prev_alias = aliases[prev_tables[-1]]
                join_condition = f"INNER JOIN {table} {table_alias} ON {prev_alias}.id = {table_alias}.id"
            
            if join_condition:
                join_clauses.append(join_condition)
                print(f"DEBUG: Added join: {join_condition}")
        
        join_str = " ".join(join_clauses) if join_clauses else ""
        
        # Build SELECT clause
        select_cols = f"{aliases[main_table]}.*"
        for table in other_tables:
            select_cols += f", {aliases[table]}.*"
        
        query_sql = f"SELECT {select_cols} {from_clause} {join_str} LIMIT 100;"
        print(f"DEBUG: Generated query: {query_sql}")
        return query_sql
    
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

