#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}   Mint Server Build Script      ${NC}"
echo -e "${GREEN}=======================================${NC}"

# Check if docker and docker compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

echo -e "${YELLOW}Stopping existing containers...${NC}"
sudo docker compose down

echo -e "${YELLOW}Cleaning up unused resources...${NC}"
echo -e "${YELLOW}- Removing unused containers${NC}"
sudo docker container prune -f

echo -e "${YELLOW}- Removing unused images${NC}"
sudo docker image prune -f

echo -e "${YELLOW}- Removing unused volumes${NC}"
sudo docker volume prune -f

echo -e "${YELLOW}- Removing unused networks${NC}"
sudo docker network prune -f

echo -e "${YELLOW}- Final system cleanup${NC}"
sudo docker system prune -f

echo -e "${YELLOW}Building and starting containers...${NC}"
sudo docker compose up --build -d

# Check if containers are running
if [ $? -eq 0 ]; then
    echo -e "${GREEN}=======================================${NC}"
    echo -e "${GREEN}   Server Built and Started Successfully   ${NC}"
    echo -e "${GREEN}=======================================${NC}"
    echo -e "You can access the API at: http://localhost/docs"
    echo -e "View logs with: docker compose logs -f"
else
    echo -e "${RED}=======================================${NC}"
    echo -e "${RED}   Server Build Failed   ${NC}"
    echo -e "${RED}=======================================${NC}"
    echo -e "Check the error messages above"
    exit 1
fi
