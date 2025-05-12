# 🧠 LangGraph Agent Project

This is a full-stack LLMOps deployment-ready project using LangChain and LangGraph, packaged in Docker and deployable to AWS EC2.

## 📦 Features
- Modular agent architecture with LangGraph
- Dockerized app for portable deployments
- AWS EC2 deployment-ready
- .env support for secure secrets
- GitHub Actions for CI/CD
- LangSmith/CloudWatch integration-ready

## 🚀 Deployment Instructions

### Docker (Local)
```bash
docker build -t langgraph-agent .
docker run -p 8000:8000 --env-file .env langgraph-agent
```

### AWS EC2 (Free Tier)
1. Launch an EC2 Ubuntu instance.
2. SSH and install Docker:
   ```bash
   sudo apt update && sudo apt install docker.io -y
   ```
3. SCP or clone this repo, then:
   ```bash
   docker build -t langgraph-agent .
   docker run -d -p 80:8000 --env-file .env langgraph-agent
   ```

## 🔐 Environment Variables
Create a `.env` file from `.env.example` with your OpenAI and AWS credentials.

## 📈 CI/CD
Push to GitHub auto-triggers a Docker build & test via GitHub Actions.

## 🎥 Showcase
- Add a Loom video link here to explain your architecture and demo the app.

## 🤝 Recruiter Notes
This project showcases:
- Full LLM agent orchestration
- Real-world MLOps and DevOps skills
- Cloud deployment practices
