# Testing Suite for Diamond Price Prediction Application

This directory contains comprehensive tests for the Diamond Price Prediction MLOps application, covering unit tests, integration tests, and end-to-end tests as required by the project specifications.

## Test Structure

### 📋 Test Requirements
- **3 Unit Tests**: Testing individual functions and components in isolation
- **3 Integration Tests**: Testing interaction between different components
- **3 End-to-End Tests**: Testing complete user workflows

### 🧪 Test Categories

#### Unit Tests (`test_unit.py`)
Tests individual functions and components in isolation:

1. **Data Preprocessing Tests**
   - Valid input data processing
   - Missing columns handling
   - Different categorical values handling

2. **Flask App Configuration Tests**
   - Flask app creation
   - CORS configuration

3. **Model Utilities Tests**
   - Model loading functionality
   - Training columns format validation
   - Numerical and categorical data validation

#### Integration Tests (`test_integration.py`)
Tests interaction between different components:

1. **API Endpoints Integration**
   - Health endpoint JSON response
   - Predict endpoint with valid data
   - Predict endpoint with invalid data

2. **Data Flow Integration**
   - Complete data preprocessing pipeline
   - Model prediction pipeline with mocks
   - Column alignment between training and inference

3. **External Service Integration**
   - Live backend health check
   - Live backend prediction
   - CORS integration

#### End-to-End Tests (`test_e2e.py`)
Tests complete user workflows:

1. **Complete User Workflow**
   - Prediction workflow with default values
   - Form input validation and submission
   - Error handling with backend down

2. **API Workflow Integration**
   - Complete API workflow with valid data
   - API workflow with multiple diamonds
   - API response time performance

3. **Data Persistence and Consistency**
   - Model consistency across requests
   - Health endpoint reliability
   - Complete user journey simulation

## 🚀 How to Run Tests

### Prerequisites
```bash
# Install test dependencies
cd tests
pip install -r requirements.txt
```

### Running Tests

#### Option 1: Using the Test Runner (Recommended)
```bash
# Run all tests
python run_tests.py

# Install dependencies and run all tests
python run_tests.py --install-deps

# Run specific test suites
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --e2e

# Run with coverage report
python run_tests.py --coverage
```

#### Option 2: Using pytest directly
```bash
# Run all tests
pytest -v

# Run specific test files
pytest test_unit.py -v
pytest test_integration.py -v
pytest test_e2e.py -v

# Run with coverage
pytest --cov=../backend --cov-report=html --cov-report=term
```

## 🔧 Test Configuration

### Backend Server Requirements
- For integration and E2E tests, the backend server should be running on `http://127.0.0.1:5000`
- Tests will automatically skip if the backend is not available
- Some tests require the ML model to be loaded and promoted to "Production" stage

### Browser Requirements (E2E Tests)
- Chrome browser is required for end-to-end tests
- Tests run in headless mode by default
- Chrome WebDriver is automatically managed via `webdriver-manager`

## 📊 Test Coverage

### Unit Tests Coverage
- **Data preprocessing functions**: Input validation, one-hot encoding, column handling
- **Flask app configuration**: App creation, CORS setup
- **Model utilities**: Model loading logic, data validation, JSON serialization

### Integration Tests Coverage
- **API endpoints**: Health check, prediction endpoint, error handling
- **Data flow**: Preprocessing pipeline, model prediction, column alignment
- **External services**: Live backend testing, CORS validation

### End-to-End Tests Coverage
- **Frontend interaction**: Form submission, input validation, error display
- **Complete workflows**: User journey simulation, API integration
- **Performance**: Response time testing, consistency validation

## 🎯 Test Scenarios

### Positive Test Cases
- Valid diamond data prediction
- Multiple diamond predictions
- Form submission with custom values
- Health check functionality
- Model consistency across requests

### Negative Test Cases
- Invalid input data handling
- Backend unavailable scenarios
- Model not loaded situations
- Network timeout handling
- Form validation errors

### Edge Cases
- Missing data columns
- Extreme diamond values
- Multiple simultaneous requests
- Browser compatibility
- Network interruptions

## 📈 Test Metrics

### Success Criteria
- All unit tests pass (9 tests)
- All integration tests pass (9 tests)
- All end-to-end tests pass (9 tests)
- Code coverage > 80%
- No critical security vulnerabilities

### Performance Benchmarks
- API response time < 5 seconds (with loaded model)
- Health check response time < 1 second
- Frontend form submission < 10 seconds
- Model prediction consistency: 100%

## 🛠️ Troubleshooting

### Common Issues

#### Backend Not Running
```bash
# Start the backend server
cd ../backend
python app.py
```

#### Model Not Loaded
```bash
# Train and promote model
cd ../backend
python train.py
```

#### Chrome WebDriver Issues
```bash
# Update Chrome and WebDriver
pip install --upgrade selenium webdriver-manager
```

#### Port Conflicts
```bash
# Kill processes on port 5000
lsof -ti:5000 | xargs kill -9
```

### Test Debugging
```bash
# Run tests with verbose output
pytest -v -s

# Run specific test
pytest test_unit.py::TestDataPreprocessing::test_data_preprocessing_with_valid_input -v

# Run tests with pdb debugger
pytest --pdb
```

## 📋 Test Checklist

Before running tests, ensure:
- [ ] Backend dependencies installed (`pip install -r ../backend/requirements.txt`)
- [ ] Test dependencies installed (`pip install -r requirements.txt`)
- [ ] Data is available (`dvc pull` if needed)
- [ ] Model is trained and promoted to Production
- [ ] Backend server is running (for integration/E2E tests)
- [ ] Chrome browser is installed (for E2E tests)

## 🔍 Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Unit tests run on every commit
- Integration tests run on pull requests
- E2E tests run on staging deployments
- Coverage reports are generated automatically

## 📝 Test Documentation

Each test includes:
- Clear test name and description
- Expected behavior documentation
- Input/output specifications
- Error handling verification
- Performance expectations

## 🚨 Known Limitations

- E2E tests require Chrome browser
- Some tests may be skipped if backend is not available
- Network-dependent tests may be flaky in CI environments
- Browser tests may fail on headless systems without proper display setup 