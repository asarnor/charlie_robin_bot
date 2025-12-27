# Dockerfile for JavaScript Trading Bot
FROM node:18-slim

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application files
COPY trading_bot.js test_connection.js ./

# Create logs directory
RUN mkdir -p /app/logs && \
    chmod 755 /app/logs

# Create non-root user
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

USER botuser

# Default to production environment
ENV ENVIRONMENT=production

# Run the bot
CMD ["node", "trading_bot.js"]

