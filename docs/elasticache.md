# AWS Valkey ElastiCache Setup Guide

This guide explains how to set up and configure the Mint Server application to use AWS Valkey ElastiCache instead of a local Redis instance.

## What is Valkey ElastiCache?

Valkey is a compatible fork of Redis that is officially supported by AWS ElastiCache. It provides the same features as Redis with additional performance improvements and enterprise features.

## AWS ElastiCache Setup

### 1. Create a Valkey ElastiCache Cluster

1. Go to the AWS Management Console and navigate to ElastiCache
2. Click "Create cluster"
3. Select "Valkey" as the engine
4. Configure your cluster:
   - **Name**: Choose a meaningful name for your cluster
   - **Description**: Optional description
   - **Location**: Choose "Regional" for standard deployments
   - **Engine version compatibility**: Select the latest version
   - **Port**: Default is 6379
   - **Parameter group**: Default unless you need specific configurations
   - **Node type**: Choose based on your performance and memory requirements
   - **Number of replicas**: Choose based on your high availability requirements
5. Configure advanced settings:
   - **Security**:
     - Create a new security group or select an existing one
     - Ensure your EC2 instances or containers can connect to the ElastiCache cluster
   - **Encryption**:
     - Enable encryption in transit for additional security (recommended)
     - Configure authentication if needed
6. Create the cluster

### 2. Update Environment Variables

For development environments, you can keep using your local Redis:

```
ENVIRONMENT=development
CACHE_PROVIDER=redis

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

REDIS_CONNECTION_POOL_SIZE=10
REDIS_CONNECTION_TIMEOUT=5
```

Update your environment variables in `.env` file or in your deployment configuration:

```
ENVIRONMENT=production
CACHE_PROVIDER=valkey

REDIS_HOST=my-valkey-cluster.abc123.ap-south-1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=           # or an auth token

REDIS_CONNECTION_POOL_SIZE=30        # bump if you have heavy traffic
REDIS_CONNECTION_TIMEOUT=5
```

### 3. Connection Pool Settings

Adjust these based on your application's needs:

```
REDIS_CONNECTION_POOL_SIZE=10
REDIS_CONNECTION_TIMEOUT=5
```

## Docker Compose Setup

For local development, you can still use the Redis container by running:

```bash
docker-compose --profile local-dev up
```

For production deployments using ElastiCache, just run:

```bash
docker-compose up
```

This will start the application without the local Redis container, connecting instead to your ElastiCache instance.

## Security Considerations

1. **Network Security**:

   - Configure security groups to allow your application to connect to ElastiCache
   - ElastiCache nodes should typically not be exposed to the public internet

2. **Authentication**:

   - Set a strong password for your ElastiCache instance
   - Store credentials securely, preferably using AWS Secrets Manager or similar service

3. **Encryption**:
   - Enable TLS for encryption in transit
   - Configure proper certificate verification

## Troubleshooting

### Connection Issues

- Verify network connectivity between your application and ElastiCache
- Check security group rules to ensure proper access
- Verify the endpoint, port, and authentication settings

### SSL/TLS Issues

If you encounter SSL/TLS errors:

1. Check if your application has the proper CA certificates
2. Try setting `ELASTICACHE_SSL_CERT_REQS=none` temporarily for testing
3. Ensure your application can reach the AWS Certificate Authority

### Latency Issues

If you experience high latency:

1. Check if your application and ElastiCache are in the same AWS region
2. Monitor CloudWatch metrics for ElastiCache performance
3. Consider using a larger node type if CPU utilization is high

## Monitoring

Set up CloudWatch alarms for your ElastiCache cluster to monitor:

- CPU utilization
- Memory usage
- Cache hit rate
- Connection count

## Costs

Be mindful of costs when setting up ElastiCache:

- Node type significantly impacts cost
- Multi-AZ deployments cost more but provide better availability
- Reserved nodes can provide significant savings for long-term use
