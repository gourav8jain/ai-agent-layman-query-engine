# AI Query Engine

An intelligent query engine that allows users to query databases using natural language, with a ChatGPT-like interface and multiple visualization options.

## Features

- 🤖 **Natural Language to SQL**: Convert plain English queries to SQL automatically
- 💬 **Chat Interface**: Interactive ChatGPT-like interface for querying databases
- 🔌 **Multiple Database Support**: Connect to PostgreSQL, MySQL, and SQLite
- 📊 **Rich Visualizations**: View results as tables, charts, bar graphs, pie charts, and line charts
- ⚙️ **Easy Configuration**: Simple database connection setup via UI
- 🎨 **Modern UI**: Beautiful, intuitive interface inspired by ChatGPT

## Architecture

```
ai-agent-layman-query-engine/
├── backend/          # FastAPI backend
│   ├── main.py                    # API endpoints
│   ├── database_manager.py        # Database connection management
│   ├── query_generator.py         # Natural language to SQL conversion
│   └── result_visualizer.py       # Data visualization generation
└── frontend/        # React frontend
    ├── src/
    │   ├── components/            # React components
    │   └── App.jsx                # Main app component
    └── package.json
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
python main.py
```

The backend will be running on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be running on `http://localhost:3000`

## Usage

### 1. Add Database Connection

1. Open the application in your browser
2. Click "+ Add Database" in the sidebar
3. Fill in the database connection details:
   - Connection Name
   - Host
   - Port
   - Username
   - Password
   - Database Name
   - Database Type (PostgreSQL, MySQL, or SQLite)
4. Click "Test Connection" to verify the connection
5. Click "Add Database" to save the connection

### 2. Query Your Database

1. Select a database connection from the sidebar
2. Type your question in plain English, for example:
   - "Show me all customers"
   - "How many orders are there?"
   - "What are the top 10 products by sales?"
   - "Find users where status is active"
3. The AI will generate SQL and execute the query
4. View results in multiple formats:
   - **Table**: Raw data view
   - **Charts**: Bar graphs, pie charts, line charts
   - **Summary**: Statistical summaries

## API Endpoints

### POST `/api/databases`
Add a new database connection.

**Request Body:**
```json
{
  "name": "Production DB",
  "host": "localhost",
  "port": 5432,
  "username": "user",
  "password": "password",
  "database": "mydb",
  "db_type": "postgresql"
}
```

### GET `/api/databases`
List all configured database connections.

### DELETE `/api/databases/{connection_id}`
Remove a database connection.

### POST `/api/chat`
Send a query message.

**Request Body:**
```json
{
  "message": "Show me all customers",
  "db_connection_id": "connection_id"
}
```

**Response:**
```json
{
  "sql_query": "SELECT * FROM customers LIMIT 100;",
  "results": {
    "columns": ["id", "name", "email"],
    "rows": [...],
    "count": 150
  },
  "visualizations": {
    "table": {...},
    "charts": [...],
    "summary": {...}
  },
  "explanation": "Query explanation..."
}
```

### POST `/api/validate-connection`
Test a database connection without saving it.

## Supported Query Types

The AI can understand various query patterns:

- **List queries**: "Show me all X", "List all Y"
- **Count queries**: "How many X?"
- **Filter queries**: "Find X where Y", "Show X with Y = Z"
- **Join queries**: "Combine X and Y", "Join X with Y"
- **Sort queries**: "Sort X by Y", "Order X by Y descending"
- **Aggregate queries**: "Group X by Y", "Show X aggregate"

## Project Structure

```
ai-agent-layman-query-engine/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database_manager.py     # Database connection and query execution
│   ├── query_generator.py      # Natural language to SQL conversion
│   ├── result_visualizer.py    # Data visualization generation
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx   # Main chat UI
│   │   │   ├── ChatInput.jsx      # Input component
│   │   │   ├── MessageList.jsx    # Message display
│   │   │   ├── QueryResult.jsx    # Results display
│   │   │   ├── DataTable.jsx      # Table visualization
│   │   │   ├── Chart.jsx          # Chart visualization
│   │   │   └── DatabaseConfig.jsx # DB configuration UI
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- asyncpg - PostgreSQL async client
- pymysql - MySQL client

**Frontend:**
- React 18 - UI framework
- Vite - Build tool
- Recharts - Chart library
- Axios - HTTP client

## Future Enhancements

- Integration with OpenAI GPT or local LLMs for better SQL generation
- Support for more database types (Oracle, MongoDB, etc.)
- Query history and favorites
- Export results to CSV, Excel, PDF
- User authentication and permissions
- Multi-user support with query sharing
- Advanced visualizations (heatmaps, scatter plots, etc.)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

