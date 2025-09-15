---
page_type: sample
languages:
- azdevel
- python
- typescript
- html
products:
- azure
- azure-cosmos-db
- azure-functions
- azure-monitor
- azure-pipelines
urlFragment: theglobe-blog-platform
name: The Globe - Blog Platform with Python API and React Frontend
description: A modern blog and news platform with Python FastAPI backend, React frontend, and Azure cloud deployment
---

<!-- YAML front-matter schema: https://review.learn.microsoft.com/en-us/help/contribute/samples/process/onboarding?branch=main#supported-metadata-fields-for-readmemd -->

# The Globe - Blog Platform with Python API and React Frontend

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://codespaces.new/waritsan/theglobe)
[![Open in Dev Container](https://img.shields.io/static/v1?style=for-the-badge&label=Dev+Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/waritsan/theglobe)

**The Globe** is a modern, full-stack blog and news platform built with cutting-edge technologies. It features a React frontend with TypeScript, a Python FastAPI backend running on Azure Functions, and Azure Cosmos DB for data storage. Perfect for news websites, personal blogs, or content management systems.

## Features

- 📰 **Blog Management**: Create, edit, and publish blog posts with rich content
- 📝 **Comment System**: Interactive comments on blog posts
- 🏷️ **Categories & Tags**: Organize content with categories and tags
- 🔍 **Search Functionality**: Full-text search across blog content
- 📱 **Responsive Design**: Mobile-first React frontend with Tailwind CSS
- ☁️ **Cloud-Native**: Deployed on Azure with serverless architecture
- 🧪 **Automated Testing**: Playwright E2E tests with CI/CD pipeline
- 📊 **Monitoring**: Azure Application Insights for performance tracking

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Backend**: Python 3.13, FastAPI, Azure Functions
- **Database**: Azure Cosmos DB
- **Testing**: Playwright, pytest
- **Deployment**: Azure Developer CLI (azd), GitHub Actions
- **Monitoring**: Azure Application Insights

## Prerequisites

- [Azure Developer CLI](https://aka.ms/azd-install)
- [Azure Functions Core Tools (4+)](https://docs.microsoft.com/azure/azure-functions/functions-run-local)
- [Python (3.10+)](https://www.python.org/downloads/)
- [Node.js (18+)](https://nodejs.org/)
- [Git](https://git-scm.com/)

## Quickstart

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/waritsan/theglobe.git
   cd theglobe
   ```

2. **Install dependencies**
   ```bash
   # Install Python dependencies
   cd src/api
   pip install -r requirements.txt

   # Install frontend dependencies
   cd ../web
   npm install
   ```

3. **Start development servers**
   ```bash
   # Start API and Web servers
   npm run start-dev  # from project root
   ```

   Or use VS Code tasks:
   ```bash
   # Terminal Menu → Run Task → "Start API and Web"
   ```

4. **Access your application**
   - Frontend: http://localhost:5173
   - API: http://localhost:3100
   - API Documentation: http://localhost:3100/docs

### Azure Deployment

```bash
# Log in to azd
azd auth login

# Initialize project
azd init

# Provision and deploy to Azure
azd up
```

## Application Architecture

The Globe uses a modern serverless architecture:

- **Azure Static Web Apps**: Hosts the React frontend
- **Azure Functions**: Runs the Python FastAPI backend
- **Azure Cosmos DB**: NoSQL database for blog content and user data
- **Azure Monitor**: Application performance monitoring
- **Azure Key Vault**: Secure storage of connection strings

## Development Workflow

### Running Tests

```bash
# Run Playwright E2E tests
cd tests
npm install
npx playwright test

# Run with UI
npx playwright test --ui

# Generate test report
npx playwright show-report
```

### API Development

The API is built with FastAPI and includes:
- RESTful endpoints for blog management
- Automatic OpenAPI/Swagger documentation
- CORS middleware for frontend integration
- Azure Application Insights integration

### Frontend Development

The React frontend features:
- Modern hooks-based architecture
- Responsive design with Tailwind CSS
- Internationalization support
- Hot module replacement for fast development

## Project Structure

```
theglobe/
├── src/
│   ├── api/                 # Python FastAPI backend
│   │   ├── blog/           # Main API application
│   │   ├── catchAllFunction/  # Azure Functions entry point
│   │   └── openapi.yaml    # API specification
│   └── web/                # React frontend
│       ├── src/
│       ├── public/
│       └── package.json
├── infra/                  # Azure infrastructure (Bicep)
├── tests/                  # Playwright E2E tests
├── .github/workflows/      # CI/CD pipelines
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run tests: `npm test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## Security

This project implements several security best practices:
- Managed identity for Azure resource access
- Azure Key Vault for secrets management
- CORS configuration for frontend-backend communication
- Input validation and sanitization

## Monitoring

The application includes comprehensive monitoring:
- Azure Application Insights for performance metrics
- Structured logging with OpenTelemetry
- Error tracking and alerting
- Real-time dashboard monitoring

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](./docs/)
- 🐛 [Issues](https://github.com/waritsan/theglobe/issues)
- 💬 [Discussions](https://github.com/waritsan/theglobe/discussions)
- 📧 Contact: waritsan@gmail.com
