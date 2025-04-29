.PHONY: setup run dev clean

# Variables
PYTHON := python3
VENV := venv
APP := app.py

# Setup virtual environment and install dependencies
setup:
	@echo "Setting up virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Installing dependencies..."
	./$(VENV)/bin/pip install --upgrade pip
	./$(VENV)/bin/pip install -r requirements.txt
	@echo "Setup complete. Run 'make run' to start the application."

# Run the application
run:
	@echo "Starting CRISPR summary application..."
	./$(VENV)/bin/python $(APP)

# Run in development mode with hot reloading
dev:
	@echo "Starting application in development mode..."
	DASH_DEBUG=1 ./$(VENV)/bin/python $(APP)

# Clean up virtual environment and cache files
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete."

# Show help information
help:
	@echo "Available commands:"
	@echo "  make setup  - Create virtual environment and install dependencies"
	@echo "  make run    - Run the application"
	@echo "  make dev    - Run the application in development mode"
	@echo "  make clean  - Remove virtual environment and cache files"
	@echo "  make help   - Show this help message"
