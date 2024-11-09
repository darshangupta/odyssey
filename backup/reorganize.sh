#!/bin/bash

# Create backup
echo "Creating backup..."
mkdir -p backup
cp -r * backup/

# Create new directory structure
echo "Creating directory structure..."
mkdir -p odyssey/api
mkdir -p odyssey/config
mkdir -p tests
mkdir -p scripts

# Move API files to correct location
echo "Moving API files..."
mv odyssey/api/* odyssey/api/ 2>/dev/null
mv api/* odyssey/api/ 2>/dev/null

# Move core Django files
echo "Moving core Django files..."
mv odyssey/settings.py odyssey/odyssey/settings.py 2>/dev/null
mv odyssey/urls.py odyssey/odyssey/urls.py 2>/dev/null
mv odyssey/wsgi.py odyssey/odyssey/wsgi.py 2>/dev/null
mv odyssey/asgi.py odyssey/odyssey/asgi.py 2>/dev/null

# Create necessary __init__.py files
echo "Creating __init__.py files..."
touch odyssey/__init__.py
touch odyssey/api/__init__.py
touch odyssey/odyssey/__init__.py
touch tests/__init__.py
touch scripts/__init__.py

# Move test files
echo "Moving test files..."
mv odyssey/api/tests.py tests/test_api.py 2>/dev/null
mv api/tests.py tests/test_api.py 2>/dev/null

# Move scripts
echo "Moving scripts..."
mv *.py scripts/ 2>/dev/null
mv manage.py ./ 2>/dev/null

# Clean up
echo "Cleaning up..."
rm -rf api 2>/dev/null
rm -rf config 2>/dev/null

echo "Done! New structure created." 