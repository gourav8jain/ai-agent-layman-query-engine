#!/bin/bash

echo "🚀 Setting up AI Query Engine..."

# Setup Backend
echo "📦 Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Setup Frontend
echo "📦 Setting up frontend..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "Backend:"
echo "  cd backend && source venv/bin/activate && python main.py"
echo ""
echo "Frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"

