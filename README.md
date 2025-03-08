# Distributed Data Processing Infrastructure

A reusable infrastructure for distributed data processing using Apache Airflow, Docker, Terraform, and monitoring with Prometheus and Grafana.

## Architecture

```
graph TD
    subgraph S3["AWS S3"]
        S3Data["Data Dumps<br/>(Partitioned)"]
    end

    subgraph AirflowCluster["Airflow Cluster (Distributed)"]
        Scheduler["Airflow Scheduler"]
        WebServer["Airflow WebServer"]
        Workers["Airflow Workers<br/>(Multiple EC2 Instances)"]
        
        Scheduler --> WebServer
        Scheduler --> Workers
    end
    
    subgraph Storage["Storage Layer"]
        PostgreSQL["PostgreSQL<br/>(Metadata & Structured Data)"]
        ProcessedS3["Processed Data<br/>(S3)"]
    end
    
    subgraph Monitoring["Monitoring"]
        Prometheus["Prometheus"]
        Grafana["Grafana Dashboards"]
        
        Prometheus --> Grafana
    end
    
    S3Data --> Workers
    Workers --> PostgreSQL
    Workers --> ProcessedS3
    Workers --> Prometheus
```

## Project Structure

```
airflow-data-infra/
├── airflow/                  # Airflow configuration and DAGs
│   ├── dags/                 # DAG definitions
│   ├── plugins/              # Custom plugins
│   └── config/               # Airflow configuration files
├── docker/                   # Docker configuration
│   ├── airflow/              # Airflow Docker setup
│   ├── monitoring/           # Prometheus and Grafana setup
│   └── docker-compose.yml    # Local development setup
├── terraform/                # Infrastructure as Code
│   ├── modules/              # Reusable Terraform modules
│   ├── environments/         # Environment-specific configurations
│   └── main.tf               # Main Terraform configuration
└── monitoring/               # Monitoring configuration
    ├── prometheus/           # Prometheus configuration
    └── grafana/              # Grafana dashboards
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Terraform (for AWS deployment)
- AWS CLI configured with appropriate credentials

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/airflow-data-infra.git
   cd airflow-data-infra
   ```

2. Start the local development environment:
   ```
   docker-compose -f docker/docker-compose.yml up -d
   ```

3. Access the services:
   - Airflow: http://localhost:8080
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000

### AWS Deployment

1. Initialize Terraform:
   ```
   cd terraform
   terraform init
   ```

2. Create a terraform.tfvars file with your AWS configuration.

3. Apply the Terraform configuration:
   ```
   terraform apply
   ```

## Features

- **Distributed Processing**: Scale horizontally by adding more workers
- **Templated DAGs**: Reusable patterns for creating data processing workflows
- **Monitoring**: Prometheus and Grafana for observability
- **Infrastructure as Code**: Terraform for AWS deployment
- **Containerization**: Docker for consistent development and deployment

## License

MIT 