# C-Q-T Steel Heat Treatment Simulator - Frontend

Professional React TypeScript application for the C-Q-T (Carburizing-Quenching-Tempering) Steel Heat Treatment Simulator. This frontend provides a sophisticated user interface for metallurgical process simulation, analysis, and optimization.

## 🚀 Features

### Core Functionality
- **Complete Heat Treatment Simulation** - Input parameters for carburizing, quenching, and tempering processes
- **Interactive Results Dashboard** - Real-time visualization of case depth profiles, hardness distributions, and carbon profiles
- **Material Comparison** - Side-by-side analysis of multiple steel grades
- **Process Optimization** - Target-driven optimization for specific case depth requirements
- **Thermal Analysis** - Comprehensive thermal history and cooling rate analysis
- **Quality Assessment** - Professional quality reports with recommendations

### Technical Features
- **Professional UI/UX** - Material-UI design system with responsive layout
- **Interactive Charts** - Plotly.js for scientific-grade data visualization
- **Real-time Validation** - Form validation with immediate feedback
- **Export Capabilities** - JSON, Excel, and PDF export options
- **Error Handling** - Comprehensive error boundaries and user feedback
- **PWA Support** - Progressive Web App capabilities for offline use

## 📋 Prerequisites

- **Node.js** >= 16.0.0
- **npm** >= 8.0.0 or **yarn** >= 1.22.0
- **Backend API** running on http://localhost:8000

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd zed\ AI/web_application/frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Environment Configuration
Create a `.env` file in the frontend root directory:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=C-Q-T Steel Heat Treatment Simulator
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=development
```

### 4. Start Development Server
```bash
npm start
# or
yarn start
```

The application will open at `http://localhost:3000`

## 📂 Project Structure

```
src/
├── components/              # React components
│   ├── InputForm.tsx       # Main simulation input form
│   ├── ResultsDashboard.tsx # Results visualization
│   ├── MaterialComparison.tsx # Multi-steel comparison
│   ├── ProcessOptimization.tsx # Target optimization
│   ├── ThermalAnalysis.tsx # Thermal history analysis
│   ├── QualityReport.tsx   # Quality assessment
│   ├── ErrorBoundary.tsx   # Error handling
│   └── LoadingOverlay.tsx  # Loading states
├── services/               # API integration
│   └── api.ts             # Complete API service layer
├── types/                 # TypeScript definitions
│   └── simulation.ts      # All simulation type definitions
├── hooks/                 # Custom React hooks
│   └── useNotification.tsx # Toast notifications
├── App.tsx               # Main application component
├── index.tsx            # Application entry point
├── index.css           # Global styles
└── reportWebVitals.ts  # Performance monitoring
```

## 🔧 Available Scripts

### Development
```bash
npm start          # Start development server
npm run dev        # Alternative development command
npm test           # Run test suite
npm run test:watch # Run tests in watch mode
```

### Build & Deployment
```bash
npm run build         # Create production build
npm run build:analyze # Build with bundle analyzer
npm run preview       # Preview production build locally
```

### Code Quality
```bash
npm run lint          # Run ESLint
npm run lint:fix      # Fix ESLint issues automatically
npm run format        # Format code with Prettier
npm run type-check    # TypeScript type checking
```

### Maintenance
```bash
npm run clean         # Clean build artifacts and node_modules
npm audit             # Security audit
npm run update-deps   # Update dependencies
```

## 🔌 API Integration

### Backend Connection
The frontend connects to the FastAPI backend via the API service layer (`src/services/api.ts`). Key endpoints:

- `POST /api/simulate` - Run complete C-Q-T simulation
- `GET /api/steel-grades` - Fetch available steel grades
- `POST /api/compare-materials` - Material comparison
- `POST /api/optimize-process` - Process optimization
- `GET /api/health` - Health check

### Environment Variables
```env
REACT_APP_API_URL=http://localhost:8000  # Backend API URL
REACT_APP_TIMEOUT=300000                 # Request timeout (5 minutes)
```

## 📊 Key Components

### InputForm Component
Comprehensive form for simulation parameters:
- Steel composition (14 chemical elements)
- Carburizing conditions (temperature, time, carbon potential)
- Quenching conditions (medium, temperature, heat transfer)
- Tempering conditions (temperature, time, cycles)
- Part geometry (cylinder, slab, sphere)
- Advanced simulation parameters

### ResultsDashboard Component
Interactive visualization of simulation results:
- **Case Depth Profile** - Primary chart showing hardness vs distance
- **Carbon Profile** - Carbon concentration distribution
- **Thermal History** - Temperature vs time during processing
- **Quality Metrics** - Key performance indicators
- **Export Options** - JSON, Excel, PDF formats

### MaterialComparison Component
Multi-steel grade comparison tool:
- Select multiple steel grades for comparison
- Unified process conditions
- Side-by-side results visualization
- Performance ranking system

### ProcessOptimization Component
Target-driven process optimization:
- Specify target case depth
- Define process constraints
- Multiple optimization objectives
- Predicted results validation

## 🎨 Styling & Theming

### Material-UI Theme
The application uses a professional Material-UI theme with:
- Primary color: `#1976d2` (Professional blue)
- Secondary color: `#f57c00` (Engineering orange)
- Typography: Roboto font family
- Consistent spacing and elevation

### Responsive Design
- Mobile-first approach
- Breakpoints: xs(0), sm(600), md(900), lg(1200), xl(1536)
- Adaptive navigation and layout
- Touch-friendly interface

## 📈 Data Visualization

### Plotly.js Integration
Scientific-grade charts for:
- Case depth profiles (HRC vs distance)
- Carbon concentration profiles
- Thermal history visualization
- Cooling rate analysis
- Quality assessment radar charts

### Chart Features
- Interactive zooming and panning
- Data export capabilities
- Professional styling
- Responsive sizing
- Accessibility support

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Docker Deployment
```dockerfile
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment-Specific Builds
```bash
# Development
npm run build:dev

# Staging
npm run build:staging

# Production
npm run build:prod
```

## 🔧 Configuration

### Webpack Configuration
The application uses Create React App's webpack configuration with customizations for:
- TypeScript support
- Path aliases (@/components, @/services, etc.)
- Bundle optimization
- Source map generation

### ESLint & Prettier
Code quality tools configured for:
- TypeScript best practices
- React hooks rules
- Material-UI guidelines
- Consistent formatting

## 🐛 Troubleshooting

### Common Issues

#### 1. API Connection Failed
```bash
# Check backend is running
curl http://localhost:8000/api/health

# Verify environment variables
echo $REACT_APP_API_URL
```

#### 2. TypeScript Errors
```bash
# Clear TypeScript cache
rm -rf node_modules/.cache
npm run type-check
```

#### 3. Build Failures
```bash
# Clear all caches
npm run clean
npm install
npm run build
```

#### 4. Performance Issues
```bash
# Analyze bundle size
npm run build:analyze

# Check for memory leaks
npm run test -- --detectOpenHandles
```

### Debug Mode
Enable debug logging:
```env
REACT_APP_DEBUG=true
REACT_APP_LOG_LEVEL=debug
```

## 🧪 Testing

### Test Structure
```
src/
├── __tests__/              # Test files
├── components/__tests__/   # Component tests
└── services/__tests__/     # Service tests
```

### Running Tests
```bash
npm test                    # Run all tests
npm run test:coverage      # Run with coverage report
npm run test:ci           # CI/CD test command
```

### Test Categories
- **Unit Tests** - Individual component testing
- **Integration Tests** - API integration testing
- **E2E Tests** - End-to-end user workflows
- **Performance Tests** - Loading and rendering performance

## 🤝 Contributing

### Development Workflow
1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes following coding standards
3. Add tests for new functionality
4. Run quality checks: `npm run lint && npm test`
5. Submit pull request

### Coding Standards
- **TypeScript** - Strict mode enabled
- **ESLint** - Airbnb configuration
- **Prettier** - Consistent formatting
- **Conventional Commits** - Commit message format
- **Component Structure** - Functional components with hooks

### Code Review Checklist
- [ ] TypeScript compilation without errors
- [ ] All tests passing
- [ ] ESLint warnings resolved
- [ ] Responsive design verified
- [ ] Accessibility standards met
- [ ] Performance impact assessed

## 📝 License

MIT License - See LICENSE file for details

## 🆘 Support

### Documentation
- API Documentation: `/api/docs` (when backend is running)
- Component Storybook: `npm run storybook`
- Type Definitions: `src/types/`

### Getting Help
1. Check troubleshooting section above
2. Review GitHub issues for similar problems
3. Contact development team for technical support

### Performance Monitoring
The application includes built-in performance monitoring:
- Web Vitals integration
- Bundle size tracking
- API response time monitoring
- Error tracking and reporting

---

## 🎯 Quick Start Checklist

- [ ] Node.js 16+ installed
- [ ] Backend API running on port 8000
- [ ] Dependencies installed (`npm install`)
- [ ] Environment variables configured
- [ ] Development server started (`npm start`)
- [ ] Application accessible at http://localhost:3000

**Ready to simulate! 🔬⚙️**