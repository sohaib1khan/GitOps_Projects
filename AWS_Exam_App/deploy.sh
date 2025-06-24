#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  AWS Study App Deployment Script ${NC}"
echo -e "${GREEN}========================================${NC}"

# Ensure we're in the correct directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
echo -e "${YELLOW}Working directory: $(pwd)${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Use docker compose or docker-compose based on what's available
DOCKER_COMPOSE_CMD="docker compose"
if ! command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo -e "${YELLOW}Creating Docker configuration files...${NC}"

# Create Dockerfile
cat > Dockerfile << 'EOF'
# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and assets
COPY main.py .
COPY questions.json .
COPY users.json .
COPY progress.json .
COPY flashcards.json .
COPY flashcard_progress.json .
COPY templates/ ./templates/
COPY static/ ./static/

# Expose the port the app runs on
EXPOSE 5019

# Command to run the application
CMD ["python", "main.py"]
EOF
echo -e "${GREEN}✓ Created Dockerfile${NC}"

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3'

services:
  aws-study-app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5019:5019"
    volumes:
      # Persist data files between container restarts
      - ./questions.json:/app/questions.json
      - ./users.json:/app/users.json
      - ./progress.json:/app/progress.json
      - ./flashcards.json:/app/flashcards.json
      - ./flashcard_progress.json:/app/flashcard_progress.json
    restart: unless-stopped
EOF
echo -e "${GREEN}✓ Created docker-compose.yml${NC}"

# Create .dockerignore
cat > .dockerignore << 'EOF'
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.git/
README.md
deploy.sh
.dockerignore
EOF
echo -e "${GREEN}✓ Created .dockerignore${NC}"

# Update requirements.txt with all necessary packages
echo -e "${YELLOW}Updating requirements.txt...${NC}"
cat > requirements.txt << 'EOF'
Flask==2.3.3
Markdown==3.5.1
Flask-Session==0.5.0
EOF
echo -e "${GREEN}✓ Updated requirements.txt with all dependencies${NC}"

# Ensure directories exist
mkdir -p templates static
echo -e "${GREEN}✓ Ensured templates and static directories exist${NC}"

# Check for users.json and create if missing
if [ ! -f users.json ]; then
    echo -e "${YELLOW}Creating default users.json file...${NC}"
    
    cat > users.json << 'EOF'
{
  "admin": "admin123",
  "student1": "password1",
  "student2": "password2",
  "instructor": "teach123",
  "demo": "demo"
}
EOF
    echo -e "${GREEN}✓ Created default users.json${NC}"
else
    echo -e "${GREEN}✓ users.json already exists${NC}"
fi

# Check for progress.json and create if missing
if [ ! -f progress.json ]; then
    echo -e "${YELLOW}Creating empty progress.json file...${NC}"
    
    cat > progress.json << 'EOF'
{}
EOF
    echo -e "${GREEN}✓ Created empty progress.json${NC}"
else
    echo -e "${GREEN}✓ progress.json already exists${NC}"
fi

# Check for questions.json and create if missing
if [ ! -f questions.json ]; then
    echo -e "${YELLOW}Creating default questions.json file...${NC}"
    
    cat > questions.json << 'EOF'
[
    {
        "id": 1,
        "question": "Which AWS service is primarily used for storing static files?",
        "options": ["EC2", "S3", "DynamoDB", "RDS"],
        "correct_answer": "S3",
        "explanation": "Amazon S3 (Simple Storage Service) is an object storage service that offers industry-leading scalability, data availability, security, and performance for storing static files."
    },
    {
        "id": 2,
        "question": "Which AWS service would you use to run containers?",
        "options": ["EC2", "S3", "ECS/EKS", "Lambda"],
        "correct_answer": "ECS/EKS",
        "explanation": "Amazon ECS (Elastic Container Service) and EKS (Elastic Kubernetes Service) are services designed specifically for running containers in AWS."
    }
]
EOF
    echo -e "${GREEN}✓ Created default questions.json${NC}"
else
    echo -e "${GREEN}✓ questions.json already exists${NC}"
fi

# Check for flashcards.json and create if missing
if [ ! -f flashcards.json ]; then
    echo -e "${YELLOW}Creating default flashcards.json file...${NC}"
    
    cat > flashcards.json << 'EOF'
[
    {
        "id": 1,
        "front": "What does **S3** stand for?",
        "back": "**Simple Storage Service**\n\nS3 is Amazon's object storage service that offers industry-leading scalability, data availability, security, and performance.",
        "category": "Storage",
        "difficulty": "easy",
        "tags": ["aws", "storage", "s3", "fundamentals"],
        "created_date": "2025-05-28T12:00:00",
        "times_studied": 0,
        "last_studied": null
    },
    {
        "id": 2,
        "front": "What is the difference between **ECS** and **EKS**?",
        "back": "**ECS (Elastic Container Service):**\n- AWS-native container orchestration\n- Simpler to set up and manage\n- Tight integration with AWS services\n\n**EKS (Elastic Kubernetes Service):**\n- Managed Kubernetes service\n- More complex but industry standard\n- Better for multi-cloud strategies",
        "category": "Containers",
        "difficulty": "medium",
        "tags": ["aws", "containers", "ecs", "eks", "kubernetes"],
        "created_date": "2025-05-28T12:00:00",
        "times_studied": 0,
        "last_studied": null
    }
]
EOF
    echo -e "${GREEN}✓ Created default flashcards.json with sample flashcards${NC}"
else
    echo -e "${GREEN}✓ flashcards.json already exists${NC}"
fi

# Check for flashcard_progress.json and create if missing
if [ ! -f flashcard_progress.json ]; then
    echo -e "${YELLOW}Creating empty flashcard_progress.json file...${NC}"
    
    cat > flashcard_progress.json << 'EOF'
{}
EOF
    echo -e "${GREEN}✓ Created empty flashcard_progress.json${NC}"
else
    echo -e "${GREEN}✓ flashcard_progress.json already exists${NC}"
fi

echo -e "${YELLOW}Building and starting the Docker container...${NC}"

# Stop any existing container
$DOCKER_COMPOSE_CMD down

# Build and start the container
if $DOCKER_COMPOSE_CMD up -d --build; then
    echo -e "${GREEN}✓ Docker container started successfully!${NC}"
    echo -e "${GREEN}✓ Your AWS Study App is now available at http://localhost:5019${NC}"
    
    # Get the container IP address for accessing on the local network
    CONTAINER_IP=$(hostname -I | awk '{print $1}' 2>/dev/null)
    if [ ! -z "$CONTAINER_IP" ]; then
        echo -e "${GREEN}✓ You can also access it on your local network at http://${CONTAINER_IP}:5019${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}Default login credentials:${NC}"
    echo -e "  ${GREEN}admin${NC} / admin123"
    echo -e "  ${GREEN}student1${NC} / password1"
    echo -e "  ${GREEN}student2${NC} / password2"
    echo -e "  ${GREEN}instructor${NC} / teach123"
    echo -e "  ${GREEN}demo${NC} / demo"
    
    echo ""
    echo -e "${YELLOW}Features included:${NC}"
    echo -e "  ${GREEN}✓${NC} Quiz system with multiple question types"
    echo -e "  ${GREEN}✓${NC} Flashcard system with spaced repetition"
    echo -e "  ${GREEN}✓${NC} Progress tracking and statistics"
    echo -e "  ${GREEN}✓${NC} User management and authentication"
    echo -e "  ${GREEN}✓${NC} Markdown support for rich content"
    echo -e "  ${GREEN}✓${NC} Responsive design for mobile/desktop"
else
    echo -e "${RED}Error: Failed to start Docker container. Check the logs for more information.${NC}"
    echo -e "${YELLOW}You can check logs with: $DOCKER_COMPOSE_CMD logs${NC}"
    exit 1
fi

echo -e "${YELLOW}Deployment complete!${NC}"
echo ""
echo -e "${GREEN}Useful commands:${NC}"
echo -e "  ${YELLOW}$DOCKER_COMPOSE_CMD logs -f${NC}        # View logs"
echo -e "  ${YELLOW}$DOCKER_COMPOSE_CMD down${NC}           # Stop the app"
echo -e "  ${YELLOW}$DOCKER_COMPOSE_CMD up -d${NC}          # Start the app"
echo -e "  ${YELLOW}$DOCKER_COMPOSE_CMD restart${NC}        # Restart the app"
echo -e "  ${YELLOW}$DOCKER_COMPOSE_CMD up -d --build${NC}  # Rebuild and start"