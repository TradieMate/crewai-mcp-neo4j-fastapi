#!/bin/bash

# Setup script for CrewAI Neo4j FastAPI Server

echo "🚀 Setting up CrewAI Neo4j FastAPI Server..."

# Initialize submodules if not already done
if [ ! -f "graph-data-science/README.adoc" ]; then
    echo "📦 Initializing Graph Data Science submodule..."
    git submodule update --init --recursive
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from sample..."
    cp sample.env .env
    echo "⚠️  Please edit .env file with your actual values before running the server"
else
    echo "✅ .env file already exists"
fi

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

# Check if uvx is available
if ! command -v uvx &> /dev/null; then
    echo "📦 Installing uv (includes uvx)..."
    poetry run pip install uv
fi

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your OpenAI API key and Neo4j credentials"
echo "2. Ensure Neo4j database is running with Graph Data Science plugin"
echo "3. Start the server with: poetry run uvicorn main:app --host 0.0.0.0 --port 12000 --reload"
echo "4. Or use Docker: docker-compose up"
echo ""
echo "🌐 Server will be available at:"
echo "   - API: http://localhost:12000"
echo "   - Docs: http://localhost:12000/docs"
echo "   - Health: http://localhost:12000/health"
echo ""
echo "📈 Graph Data Science:"
echo "   - See GRAPH_DATA_SCIENCE.md for detailed usage instructions"
echo "   - Build GDS plugin: cd graph-data-science && ./gradlew :open-packaging:shadowCopy"