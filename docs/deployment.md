# AWS Deployment Guide

This document details the deployment architecture and setup for the Mint-Server application on AWS.

## Deployment Architecture

The Mint-Server is deployed with a multi-region architecture to achieve low latency access globally:

- Regions: `us-east-1` (N. Virginia) and `us-west-1` (N. California)
- DNS: Latency-based routing through Route53
- Caching: Redis through ElastiCache in each region
- Container Orchestration: Amazon ECS
- Load Balancing: Application Load Balancers

### Performance Targets

The architecture is designed to meet the following latency targets:
- `us-east-1`: 40ms p95 latency
- `us-west-1`: 50ms p95 latency

## Deployment Components

### 1. Docker Image

The application is containerized and pushed to Docker Hub:

```bash
# Build the Docker image
docker build -t username/mint-server:latest .

# Push to Docker Hub
docker push username/mint-server:latest
```

### 2. ElastiCache (Redis)

Redis clusters are set up in both regions:

1. **Create Subnet Groups**:
   - Select private subnets in each region
   - Group them into Redis subnet groups

2. **Security Groups**:
   - Create security groups allowing TCP 6379 (Redis port)
   - Ensure access from ECS task security groups

3. **Create ElastiCache Clusters**:
   - Engine: Redis
   - Node type: According to performance needs (e.g., cache.t3.small)
   - Multi-AZ: Enabled for high availability
   - Encryption in transit: Enabled
   - Authentication: Token required

### 3. Amazon ECS Clusters

1. **Create ECS Clusters**:
   - Create a cluster in each region (`us-east-1` and `us-west-1`)
   - Use Fargate launch type for serverless operation

2. **Task Definitions**:
   - Create task definitions with:
     - Container image: `username/mint-server:latest`
     - CPU/Memory: According to workload (e.g., 1 vCPU, 2GB)
     - Environment variables:
       ```
       REDIS_HOST=<region-specific-elasticache-endpoint>
       ```

3. **ECS Services**:
   - Create a service in each region with:
     - Desired count: Based on expected traffic
     - Load balancer: Application Load Balancer
     - Service Auto Scaling: CPU/Memory based

### 4. Load Balancing

1. **Application Load Balancers (ALB)**:
   - Create ALB in each region
   - Configure listeners: HTTP (port 80) and HTTPS (port 443)
   - Install SSL certificates

2. **Target Groups**:
   - Create target groups pointing to ECS services
   - Health check: `/health` endpoint
   - Protocol: HTTP
   - Success codes: 200

### 5. Route53 DNS Setup

1. **Create Records**:
   - Record type: A record
   - Routing policy: Latency
   - Configure endpoints for both regions
   - TTL: 60 seconds

2. **Alias Records**:
   - Create alias records pointing to the regional ALBs
   - This allows automatic routing to the lowest latency region

## Monitoring and Scaling

### CloudWatch Alarms

Set up CloudWatch alarms for:
- ECS service CPU/Memory utilization
- ElastiCache CPU/Memory usage
- ALB latency and request count
- 5XX error rates

### Auto Scaling

Configure auto scaling for ECS services based on:
- CPU utilization (e.g., scale up at 70%)
- Memory utilization
- Request count per target

## Troubleshooting

Common issues and solutions:

1. **High Latency**:
   - Check ElastiCache metrics
   - Verify network ACLs and security groups
   - Consider upgrading ElastiCache node types
   - Adjust ECS task CPU/Memory allocation

2. **Connection Issues**:
   - Verify security group rules
   - Check ElastiCache endpoint configuration
   - Confirm Redis password in environment variables
   - Validate TLS configuration

3. **Auto Scaling Problems**:
   - Review CloudWatch metrics
   - Check scaling policy thresholds
   - Verify service limits in the AWS account

## Security Best Practices

1. Use private subnets for ECS tasks and ElastiCache
2. Implement least privilege IAM roles
3. Enable encryption in transit for Redis connections
4. Store secrets in AWS Secrets Manager
5. Use security groups for network isolation

## Cost Optimization

1. Right-size ElastiCache instances based on usage patterns
2. Use Reserved Instances for predictable workloads
3. Set up detailed CloudWatch metrics for resource utilization
4. Configure auto-scaling to match demand
5. Monitor AWS Cost Explorer regularly