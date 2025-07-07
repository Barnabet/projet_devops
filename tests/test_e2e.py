"""
End-to-End Tests for Diamond Price Prediction Application

These tests simulate complete user workflows from frontend interaction
through backend processing to final results.
"""

import pytest
import requests
import json
import time
import os
import subprocess
import signal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

class TestCompleteUserWorkflow:
    """Test complete user workflows end-to-end"""
    
    @pytest.fixture(scope="class")
    def backend_server(self):
        """Start backend server for E2E tests"""
        backend_process = None
        try:
            # Check if backend is already running
            response = requests.get('http://127.0.0.1:5000/health', timeout=2)
            if response.status_code == 200:
                yield "already_running"
                return
        except:
            pass
        
        # Start backend server
        backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
        backend_process = subprocess.Popen(
            ['python', 'app.py'],
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        for _ in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get('http://127.0.0.1:5000/health', timeout=1)
                if response.status_code == 200:
                    break
            except:
                time.sleep(1)
        else:
            if backend_process:
                backend_process.terminate()
            pytest.skip("Could not start backend server for E2E tests")
        
        yield backend_process
        
        # Cleanup
        if backend_process:
            backend_process.terminate()
            backend_process.wait()

    @pytest.fixture(scope="class")
    def web_driver(self):
        """Set up Chrome WebDriver for E2E tests"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            
            yield driver
            
        except Exception as e:
            pytest.skip(f"Could not set up Chrome WebDriver: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass

    def test_complete_prediction_workflow_with_default_values(self, backend_server, web_driver):
        """Test 1: Complete prediction workflow using default form values"""
        # Open the frontend HTML file
        frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')
        frontend_url = f"file://{os.path.abspath(frontend_path)}"
        
        web_driver.get(frontend_url)
        
        # Wait for page to load
        WebDriverWait(web_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Verify page title and main heading
        assert "Diamond Price Prediction" in web_driver.title
        heading = web_driver.find_element(By.TAG_NAME, "h1")
        assert "Diamond Price Prediction" in heading.text
        
        # Find and click the predict button (form should have default values)
        predict_button = web_driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        assert predict_button.is_enabled()
        
        # Click predict button
        predict_button.click()
        
        # Wait for result (either success or error)
        try:
            WebDriverWait(web_driver, 15).until(
                EC.presence_of_element_located((By.ID, "result"))
            )
            
            result_div = web_driver.find_element(By.ID, "result")
            assert result_div.is_displayed()
            
            # Check if we got a prediction or an error
            result_text = result_div.text
            assert len(result_text) > 0
            
            # Should contain either "Predicted Price" or "Prediction Failed"
            assert any(phrase in result_text for phrase in [
                "Estimated Diamond Price", "Prediction Failed", "Model not loaded"
            ])
            
        except TimeoutException:
            pytest.fail("Prediction request timed out")

    def test_form_input_validation_and_submission(self, backend_server, web_driver):
        """Test 2: Form input validation and custom value submission"""
        frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')
        frontend_url = f"file://{os.path.abspath(frontend_path)}"
        
        web_driver.get(frontend_url)
        
        # Wait for form to load
        WebDriverWait(web_driver, 10).until(
            EC.presence_of_element_located((By.ID, "predictionForm"))
        )
        
        # Test form inputs with custom values
        test_values = {
            'carat': '1.5',
            'depth': '62.0',
            'table': '58.0',
            'x': '7.5',
            'y': '7.5',
            'z': '4.6'
        }
        
        # Fill in numerical inputs
        for field_name, value in test_values.items():
            field = web_driver.find_element(By.CSS_SELECTOR, f"input[name='{field_name}']")
            field.clear()
            field.send_keys(value)
        
        # Test dropdown selections
        cut_select = Select(web_driver.find_element(By.CSS_SELECTOR, "select[name='cut']"))
        cut_select.select_by_value("Premium")
        
        color_select = Select(web_driver.find_element(By.CSS_SELECTOR, "select[name='color']"))
        color_select.select_by_value("G")
        
        clarity_select = Select(web_driver.find_element(By.CSS_SELECTOR, "select[name='clarity']"))
        clarity_select.select_by_value("VS1")
        
        # Verify values were set
        assert web_driver.find_element(By.CSS_SELECTOR, "input[name='carat']").get_attribute('value') == '1.5'
        assert cut_select.first_selected_option.get_attribute('value') == 'Premium'
        assert color_select.first_selected_option.get_attribute('value') == 'G'
        assert clarity_select.first_selected_option.get_attribute('value') == 'VS1'
        
        # Submit form
        predict_button = web_driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        predict_button.click()
        
        # Wait for button text to change to "Predicting..."
        WebDriverWait(web_driver, 5).until(
            lambda driver: "Predicting" in predict_button.text or predict_button.is_enabled()
        )
        
        # Wait for result
        try:
            WebDriverWait(web_driver, 15).until(
                EC.presence_of_element_located((By.ID, "result"))
            )
            
            result_div = web_driver.find_element(By.ID, "result")
            assert result_div.is_displayed()
            
        except TimeoutException:
            pytest.fail("Form submission timed out")

    def test_error_handling_with_backend_down(self, web_driver):
        """Test 3: Error handling when backend is not available"""
        frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')
        frontend_url = f"file://{os.path.abspath(frontend_path)}"
        
        web_driver.get(frontend_url)
        
        # Wait for form to load
        WebDriverWait(web_driver, 10).until(
            EC.presence_of_element_located((By.ID, "predictionForm"))
        )
        
        # Modify the frontend to point to a non-existent backend
        web_driver.execute_script("""
            // Override the axios request to point to a non-existent port
            const originalPost = axios.post;
            axios.post = function(url, data) {
                return originalPost('http://127.0.0.1:9999/predict', data);
            };
        """)
        
        # Submit form
        predict_button = web_driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        predict_button.click()
        
        # Wait for error message
        try:
            WebDriverWait(web_driver, 10).until(
                EC.presence_of_element_located((By.ID, "result"))
            )
            
            result_div = web_driver.find_element(By.ID, "result")
            assert result_div.is_displayed()
            
            # Should show error message
            result_text = result_div.text
            assert "Prediction Failed" in result_text or "Failed to get prediction" in result_text
            
        except TimeoutException:
            pytest.fail("Error handling test timed out")


class TestAPIWorkflowIntegration:
    """Test API workflow integration without browser"""
    
    def test_complete_api_workflow_with_valid_data(self):
        """Test 4: Complete API workflow with valid diamond data"""
        # Test data representing a high-quality diamond
        test_diamond = {
            'carat': 2.0,
            'cut': 'Ideal',
            'color': 'D',
            'clarity': 'IF',
            'depth': 61.0,
            'table': 55.0,
            'x': 8.0,
            'y': 8.0,
            'z': 4.9
        }
        
        try:
            # First, check if backend is running
            health_response = requests.get('http://127.0.0.1:5000/health', timeout=5)
            
            if health_response.status_code != 200:
                pytest.skip("Backend not running - skipping API workflow test")
            
            # Test the complete workflow
            prediction_response = requests.post(
                'http://127.0.0.1:5000/predict',
                json=[test_diamond],
                timeout=15
            )
            
            # Verify response
            assert prediction_response.status_code in [200, 500]  # 500 if model not loaded
            
            response_data = prediction_response.json()
            
            if prediction_response.status_code == 200:
                # Successful prediction
                assert 'predicted_price' in response_data
                assert isinstance(response_data['predicted_price'], list)
                assert len(response_data['predicted_price']) == 1
                
                predicted_price = response_data['predicted_price'][0]
                assert isinstance(predicted_price, (int, float))
                assert predicted_price > 0
                
                # High-quality 2-carat diamond should be expensive
                # This is a reasonable range for such a diamond
                assert 5000 <= predicted_price <= 50000
                
            else:
                # Model not loaded error
                assert 'error' in response_data
                assert 'model not loaded' in response_data['error'].lower()
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running - skipping API workflow test")
        except requests.exceptions.Timeout:
            pytest.fail("API workflow test timed out")

    def test_api_workflow_with_multiple_diamonds(self):
        """Test 5: API workflow with multiple diamond predictions"""
        # Test data with multiple diamonds of different qualities
        test_diamonds = [
            {  # Low-quality small diamond
                'carat': 0.3,
                'cut': 'Fair',
                'color': 'J',
                'clarity': 'I1',
                'depth': 65.0,
                'table': 60.0,
                'x': 4.0,
                'y': 4.0,
                'z': 2.6
            },
            {  # High-quality medium diamond
                'carat': 1.0,
                'cut': 'Ideal',
                'color': 'E',
                'clarity': 'VVS1',
                'depth': 61.5,
                'table': 55.0,
                'x': 6.5,
                'y': 6.5,
                'z': 4.0
            }
        ]
        
        try:
            # Check if backend is running
            health_response = requests.get('http://127.0.0.1:5000/health', timeout=5)
            
            if health_response.status_code != 200:
                pytest.skip("Backend not running - skipping multiple diamonds test")
            
            # Test multiple predictions
            prediction_response = requests.post(
                'http://127.0.0.1:5000/predict',
                json=test_diamonds,
                timeout=15
            )
            
            if prediction_response.status_code == 200:
                response_data = prediction_response.json()
                assert 'predicted_price' in response_data
                assert isinstance(response_data['predicted_price'], list)
                assert len(response_data['predicted_price']) == 2
                
                # Both predictions should be positive numbers
                for price in response_data['predicted_price']:
                    assert isinstance(price, (int, float))
                    assert price > 0
                
                # The high-quality diamond should be more expensive than the low-quality one
                low_quality_price = response_data['predicted_price'][0]
                high_quality_price = response_data['predicted_price'][1]
                assert high_quality_price > low_quality_price
                
            else:
                # Model not loaded - this is acceptable for this test
                response_data = prediction_response.json()
                assert 'error' in response_data
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running - skipping multiple diamonds test")
        except requests.exceptions.Timeout:
            pytest.fail("Multiple diamonds test timed out")

    def test_api_response_time_performance(self):
        """Test 6: API response time performance"""
        test_diamond = {
            'carat': 0.5,
            'cut': 'Very Good',
            'color': 'F',
            'clarity': 'VS2',
            'depth': 62.0,
            'table': 56.0,
            'x': 5.0,
            'y': 5.0,
            'z': 3.1
        }
        
        try:
            # Check if backend is running
            health_response = requests.get('http://127.0.0.1:5000/health', timeout=5)
            
            if health_response.status_code != 200:
                pytest.skip("Backend not running - skipping performance test")
            
            # Measure response time
            start_time = time.time()
            prediction_response = requests.post(
                'http://127.0.0.1:5000/predict',
                json=[test_diamond],
                timeout=10
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # API should respond within reasonable time (10 seconds max)
            assert response_time < 10.0
            
            # For a loaded model, response should be quite fast (under 5 seconds)
            if prediction_response.status_code == 200:
                assert response_time < 5.0
            
            # Verify we got a valid response
            assert prediction_response.status_code in [200, 500]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running - skipping performance test")
        except requests.exceptions.Timeout:
            pytest.fail("Performance test timed out")


class TestDataPersistenceAndConsistency:
    """Test data persistence and consistency across requests"""
    
    def test_model_consistency_across_requests(self):
        """Test 7: Model predictions are consistent for identical inputs"""
        test_diamond = {
            'carat': 0.7,
            'cut': 'Premium',
            'color': 'G',
            'clarity': 'SI1',
            'depth': 61.8,
            'table': 56.5,
            'x': 5.7,
            'y': 5.7,
            'z': 3.5
        }
        
        try:
            # Check if backend is running and model is loaded
            health_response = requests.get('http://127.0.0.1:5000/health', timeout=5)
            
            if health_response.status_code != 200:
                pytest.skip("Backend not running - skipping consistency test")
            
            health_data = health_response.json()
            if health_data.get('model_status') != 'loaded':
                pytest.skip("Model not loaded - skipping consistency test")
            
            # Make multiple requests with identical data
            predictions = []
            for i in range(3):
                response = requests.post(
                    'http://127.0.0.1:5000/predict',
                    json=[test_diamond],
                    timeout=10
                )
                
                assert response.status_code == 200
                data = response.json()
                assert 'predicted_price' in data
                predictions.append(data['predicted_price'][0])
                
                # Small delay between requests
                time.sleep(0.1)
            
            # All predictions should be identical
            assert len(set(predictions)) == 1, f"Predictions not consistent: {predictions}"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running - skipping consistency test")
        except requests.exceptions.Timeout:
            pytest.fail("Consistency test timed out")

    def test_health_endpoint_reliability(self):
        """Test 8: Health endpoint reliability and information accuracy"""
        try:
            # Make multiple health check requests
            health_responses = []
            for i in range(5):
                response = requests.get('http://127.0.0.1:5000/health', timeout=5)
                health_responses.append(response)
                time.sleep(0.2)
            
            # All health checks should succeed
            for response in health_responses:
                assert response.status_code == 200
                data = response.json()
                
                # Verify required fields
                assert 'status' in data
                assert 'model_status' in data
                assert 'message' in data
                
                # Status should always be 'healthy'
                assert data['status'] == 'healthy'
                
                # Model status should be consistent
                assert data['model_status'] in ['loaded', 'not loaded']
            
            # Model status should be consistent across all requests
            model_statuses = [resp.json()['model_status'] for resp in health_responses]
            assert len(set(model_statuses)) == 1, f"Model status inconsistent: {model_statuses}"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running - skipping health reliability test")
        except requests.exceptions.Timeout:
            pytest.fail("Health reliability test timed out")

    def test_complete_user_journey_simulation(self):
        """Test 9: Complete user journey from start to finish"""
        # Simulate a complete user journey
        user_diamonds = [
            {  # User's first diamond query - engagement ring
                'carat': 1.0,
                'cut': 'Ideal',
                'color': 'F',
                'clarity': 'VS1',
                'depth': 61.5,
                'table': 55.0,
                'x': 6.4,
                'y': 6.4,
                'z': 3.9
            },
            {  # User's second query - comparing with different cut
                'carat': 1.0,
                'cut': 'Premium',
                'color': 'F',
                'clarity': 'VS1',
                'depth': 61.5,
                'table': 55.0,
                'x': 6.4,
                'y': 6.4,
                'z': 3.9
            },
            {  # User's third query - budget option
                'carat': 0.8,
                'cut': 'Very Good',
                'color': 'G',
                'clarity': 'SI1',
                'depth': 62.0,
                'table': 56.0,
                'x': 6.0,
                'y': 6.0,
                'z': 3.7
            }
        ]
        
        try:
            # Check if backend is running
            health_response = requests.get('http://127.0.0.1:5000/health', timeout=5)
            
            if health_response.status_code != 200:
                pytest.skip("Backend not running - skipping user journey test")
            
            predictions = []
            
            # Simulate user making multiple queries
            for i, diamond in enumerate(user_diamonds):
                response = requests.post(
                    'http://127.0.0.1:5000/predict',
                    json=[diamond],
                    timeout=10
                )
                
                # Each request should succeed (or fail consistently)
                assert response.status_code in [200, 500]
                
                if response.status_code == 200:
                    data = response.json()
                    assert 'predicted_price' in data
                    prediction = data['predicted_price'][0]
                    predictions.append(prediction)
                    
                    # Verify prediction is reasonable
                    assert isinstance(prediction, (int, float))
                    assert prediction > 0
                    assert 100 <= prediction <= 100000  # Reasonable price range
                
                # Simulate user thinking time between queries
                time.sleep(0.5)
            
            # If we got predictions, verify they make business sense
            if len(predictions) >= 2:
                # First two diamonds have same specs except cut (Ideal vs Premium)
                # Ideal cut should typically be more expensive than Premium
                if len(predictions) >= 2:
                    ideal_price = predictions[0]
                    premium_price = predictions[1]
                    # Allow some tolerance, but Ideal should generally be higher
                    assert ideal_price >= premium_price * 0.9
                
                # Budget option (third diamond) should be less expensive than first
                if len(predictions) >= 3:
                    engagement_price = predictions[0]
                    budget_price = predictions[2]
                    assert budget_price < engagement_price
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running - skipping user journey test")
        except requests.exceptions.Timeout:
            pytest.fail("User journey test timed out")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
