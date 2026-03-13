#!/bin/bash
echo "📊 Setting up monitoring and logging..."

# Create Prometheus configuration
mkdir -p monitoring
cat > monitoring/prometheus.yml << 'PROMETHEUS'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'zero2hacker-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
PROMETHEUS

# Create Grafana dashboards directory
mkdir -p monitoring/grafana/dashboards

echo "✅ Monitoring configuration created"
