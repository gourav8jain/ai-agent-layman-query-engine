# Quick Start Guide

Get your AI Query Engine up and running in minutes!

## Option 1: Using Docker (Recommended)

```bash
# Start everything with one command
docker-compose up

# The application will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
```

## Option 2: Manual Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The backend will run on `http://localhost:8000`

### 2. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will run on `http://localhost:3000`

## 3. Configure Your First Database

1. Open `http://localhost:3000` in your browser
2. Click "+ Add Database" in the sidebar
3. Fill in your database details:
   - **Connection Name**: Give it a friendly name
   - **Database Type**: Choose PostgreSQL, MySQL, or SQLite
   - **Host**: Your database host (e.g., localhost)
   - **Port**: Database port (e.g., 5432 for PostgreSQL)
   - **Username**: Database username
   - **Password**: Database password
   - **Database Name**: The database name
4. Click "Test Connection" to verify
5. Click "Add Database" to save

## 4. Start Querying!

Once your database is connected:

1. Select the database from the sidebar
2. Type your question in plain English:
   - "Show me all customers"
   - "How many orders are there?"
   - "What are the top 10 products?"
   - "Find users where status is active"
3. View results in tables, charts, or summaries!

## Example Database Setup

If you don't have a database yet, you can quickly create a test PostgreSQL database:

```sql
-- Create a test database
CREATE DATABASE test_db;

-- Connect to it
\c test_db

-- Create a sample table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    status VARCHAR(20)
);

-- Insert sample data
INSERT INTO customers (name, email, status) VALUES
    ('John Doe', 'john@example.com', 'active'),
    ('Jane Smith', 'jane@example.com', 'active'),
    ('Bob Johnson', 'bob@example.com', 'inactive'),
    ('Alice Brown', 'alice@example.com', 'active');

-- Create an orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    product_name VARCHAR(100),
    amount DECIMAL(10, 2),
    order_date DATE
);

-- Insert sample orders
INSERT INTO orders (customer_id, product_name, amount, order_date) VALUES
    (1, 'Laptop', 1299.99, '2024-01-15'),
    (1, 'Mouse', 25.50, '2024-01-16'),
    (2, 'Keyboard', 75.00, '2024-01-17'),
    (3, 'Monitor', 299.99, '2024-01-18'),
    (4, 'Headphones', 150.00, '2024-01-19');
```

## Troubleshooting

### Backend won't start
- Make sure Python 3.8+ is installed
- Check that all dependencies installed correctly
- Look for error messages in the terminal

### Frontend won't start
- Make sure Node.js 16+ is installed
- Try deleting `node_modules` and running `npm install` again
- Check that port 3000 is not in use

### Connection errors
- Verify database credentials are correct
- Check that the database server is running
- Ensure network/firewall allows connections
- For PostgreSQL, check pg_hba.conf settings

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API endpoints at `http://localhost:8000/docs`
- Try different query types and visualizations
- Check out example queries in the chat interface

## Support

If you encounter any issues, check the console for error messages or open an issue on GitHub.

