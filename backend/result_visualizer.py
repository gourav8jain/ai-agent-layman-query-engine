from typing import Dict, List, Any
import json


class ResultVisualizer:
    """Create visualizations from query results"""
    
    def create_visualizations(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create multiple visualization formats"""
        visualizations = {
            "table": self._create_table_visualization(results),
            "charts": self._create_chart_visualizations(results),
            "summary": self._create_summary(results)
        }
        return visualizations
    
    def _create_table_visualization(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create table format"""
        return {
            "type": "table",
            "columns": results.get("columns", []),
            "rows": results.get("rows", []),
            "row_count": results.get("count", 0)
        }
    
    def _create_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create statistical summary"""
        count = results.get("count", 0)
        summary = {
            "total_rows": count,
            "row_count": count,  # For compatibility
            "columns": results.get("columns", []),
        }
        
        # Try to calculate numeric statistics
        rows = results.get("rows", [])
        if rows and len(rows) > 0:
            numeric_columns = []
            for col in results.get("columns", []):
                # Try to determine if column is numeric
                if any(row.get(col) and isinstance(row.get(col), (int, float)) for row in rows[:5]):
                    values = [row.get(col) for row in rows if row.get(col) is not None]
                    if values:
                        numeric_columns.append({
                            "column": col,
                            "count": len(values),
                            "min": min(values),
                            "max": max(values),
                            "avg": sum(values) / len(values)
                        })
            
            summary["numeric_summary"] = numeric_columns
        
        return summary
    
    def _create_chart_visualizations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create various chart visualizations"""
        charts = []
        rows = results.get("rows", [])
        
        if not rows:
            return charts
        
        columns = results.get("columns", [])
        
        # Detect chart types based on data
        # Bar chart for categorical + numeric
        categorical_cols = []
        numeric_cols = []
        
        for col in columns:
            # Check if mostly categorical
            unique_values = set()
            for row in rows[:10]:  # Sample first 10 rows
                val = row.get(col)
                if val is not None:
                    unique_values.add(str(val))
            
            # If few unique values relative to row count, likely categorical
            if rows and len(unique_values) < len(rows) / 2:
                categorical_cols.append(col)
            
            # Check if numeric
            if any(isinstance(row.get(col), (int, float)) for row in rows):
                numeric_cols.append(col)
        
        # Bar Chart
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            # Aggregate data
            data_map = {}
            for row in rows:
                key = str(row.get(cat_col, ""))
                val = row.get(num_col, 0)
                data_map[key] = data_map.get(key, 0) + (val if isinstance(val, (int, float)) else 0)
            
            if data_map:
                charts.append({
                    "type": "bar",
                    "title": f"{num_col} by {cat_col}",
                    "data": [
                        {"label": k, "value": v}
                        for k, v in data_map.items()
                    ]
                })
        
        # Pie Chart (for categorical data with counts)
        if categorical_cols:
            cat_col = categorical_cols[0]
            data_map = {}
            for row in rows:
                key = str(row.get(cat_col, ""))
                data_map[key] = data_map.get(key, 0) + 1
            
            if len(data_map) <= 10:  # Only for few categories
                charts.append({
                    "type": "pie",
                    "title": f"Distribution of {cat_col}",
                    "data": [
                        {"label": k, "value": v}
                        for k, v in data_map.items()
                    ]
                })
        
        # Line Chart (for ordered numeric data)
        if numeric_cols and len(rows) > 1:
            num_col = numeric_cols[0]
            # Check if data seems sequential
            values = [row.get(num_col) for row in rows if row.get(num_col) is not None]
            if len(values) >= 2:
                charts.append({
                    "type": "line",
                    "title": f"{num_col} over time",
                    "data": [
                        {"x": i, "y": v}
                        for i, v in enumerate(values)
                    ]
                })
        
        return charts

