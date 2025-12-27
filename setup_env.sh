#!/bin/bash
# Setup script for environment configuration files

echo "Charlie Robin Trading Bot - Environment Setup"
echo "=============================================="
echo ""

# Function to copy example file if it doesn't exist
setup_env_file() {
    local env_name=$1
    local example_file="env.${env_name}.example"
    local env_file=".env.${env_name}"
    
    if [ -f "$env_file" ]; then
        echo "⚠️  $env_file already exists. Skipping..."
    else
        if [ -f "$example_file" ]; then
            cp "$example_file" "$env_file"
            echo "✅ Created $env_file from $example_file"
            echo "   Please edit $env_file and add your credentials"
        else
            echo "❌ Example file $example_file not found"
        fi
    fi
}

# Setup all environment files
echo "Setting up environment files..."
echo ""

setup_env_file "local"
setup_env_file "sandbox"
setup_env_file "production"

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env.local, .env.sandbox, or .env.production with your credentials"
echo "2. Set ENVIRONMENT variable when running:"
echo "   ENVIRONMENT=local python trading_bot.py"
echo "   ENVIRONMENT=sandbox python trading_bot.py"
echo "   ENVIRONMENT=production python trading_bot.py"
echo ""
echo "⚠️  Remember: Never commit .env.* files to version control!"

