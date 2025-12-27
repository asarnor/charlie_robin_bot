module.exports = {
  apps: [{
    name: 'trading-bot',
    script: './trading_bot.js',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      ENVIRONMENT: 'production'
    },
    env_local: {
      NODE_ENV: 'development',
      ENVIRONMENT: 'local'
    },
    env_sandbox: {
      NODE_ENV: 'production',
      ENVIRONMENT: 'sandbox'
    },
    env_production: {
      NODE_ENV: 'production',
      ENVIRONMENT: 'production'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    time: true
  }]
};

