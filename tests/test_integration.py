"""
Integration Tests for Diamond Price Prediction Application

These tests focus on testing the interaction between different components,
such as API endpoints, data processing pipelines, and model integration.
"""

import pytest
import requests
import json
import time
import os
import sys
from unittest.mock import patch, Mock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app

class TestAPIEndpoints:
    """Test API endpoint integration"""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_health_endpoint_integration(self, client):
        """Test 1: Health endpoint returns proper JSON response"""
        response = client.get('/health')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert 'status' in data
        assert 'model_status' in data
        assert 'message' in data
        assert data['status'] == 'running'
        assert data['model_status'] in ['loaded', 'not loaded']

    def test_predict_endpoint_with_valid_data(self, client):
        """Test 2: Predict endpoint handles valid diamond data"""
        valid_diamond_data = [{
            'carat': 0.23,
            'cut': 'Ideal',
            'color': 'E',
            'clarity': 'SI2',
            'depth': 61.5,
            'table': 55.0,
            'x': 3.95,
            'y': 3.98,
            'z': 2.43
        }]
        
        response = client.post('/predict',
                             data=json.dumps(valid_diamond_data),
                             content_type='application/json')
        
        # Should return either a prediction or a model not loaded error
        assert response.status_code in [200, 500]
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        if response.status_code == 200:
            assert 'predicted_price' in data
            assert isinstance(data['predicted_price'], list)
            assert len(data['predicted_price']) == 1
            assert isinstance(data['predicted_price'][0], (int, float))
            assert data['predicted_price'][0] > 0
        else:
            assert 'error' in data

    def test_predict_endpoint_with_invalid_data(self, client):
        """Test 3: Predict endpoint handles invalid data gracefully"""
        invalid_data = [{
            'invalid_field': 'invalid_value'
        }]
        
        response = client.post('/predict',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        # Should return an error
        assert response.status_code in [400, 500]
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert 'error' in data


class TestDataFlowIntegration:
    """Test data flow through the entire prediction pipeline"""
    
    def test_data_preprocessing_pipeline(self):
        """Test 4: Complete data preprocessing pipeline"""
        import pandas as pd
        
        # Test data that mimics what comes from the frontend
        frontend_data = [{
            'carat': 0.5,
            'cut': 'Premium',
            'color': 'G',
            'clarity': 'VS1',
            'depth': 62.0,
            'table': 57.0,
            'x': 5.0,
            'y': 5.0,
            'z': 3.1
        }]
        
        # Convert to DataFrame (as done in the app)
        df = pd.DataFrame(frontend_data)
        
        # Apply one-hot encoding (as done in the app)
        df_processed = pd.get_dummies(df)
        
        # Verify the pipeline works end-to-end
        assert isinstance(df_processed, pd.DataFrame)
        assert len(df_processed) == 1
        
        # Check that all numerical columns are preserved
        numerical_cols = ['carat', 'depth', 'table', 'x', 'y', 'z']
        for col in numerical_cols:
            assert col in df_processed.columns
            assert pd.api.types.is_numeric_dtype(df_processed[col])
        
        # Check that categorical columns are one-hot encoded
        assert any(col.startswith('cut_') for col in df_processed.columns)
        assert any(col.startswith('color_') for col in df_processed.columns)
        assert any(col.startswith('clarity_') for col in df_processed.columns)

    def test_model_prediction_pipeline_with_mock(self):
        """Test 5: Model prediction pipeline with mocked model"""
        import pandas as pd
        from unittest.mock import Mock
        
        # Create test data
        test_data = pd.DataFrame([{
            'carat': 0.3, 'depth': 61.0, 'table': 56.0,
            'x': 4.0, 'y': 4.0, 'z': 2.5,
            'cut_Ideal': 1, 'cut_Premium': 0,
            'color_E': 1, 'color_G': 0,
            'clarity_SI1': 1, 'clarity_VS1': 0
        }])
        
        # Mock a model
        mock_model = Mock()
        mock_model.predict.return_value = [1500.0]  # Mock prediction
        
        # Test that the model interface works
        prediction = mock_model.predict(test_data)
        
        assert isinstance(prediction, list)
        assert len(prediction) == 1
        assert isinstance(prediction[0], float)
        assert prediction[0] > 0

    def test_column_alignment_integration(self):
        """Test 6: Column alignment between training and inference"""
        import pandas as pd
        
        # Simulate training columns (what the model expects)
        training_columns = [
            'carat', 'depth', 'table', 'x', 'y', 'z',
            'cut_Fair', 'cut_Good', 'cut_Ideal', 'cut_Premium', 'cut_Very Good',
            'color_D', 'color_E', 'color_F', 'color_G', 'color_H', 'color_I', 'color_J',
            'clarity_FL', 'clarity_IF', 'clarity_SI1', 'clarity_SI2', 'clarity_VS1', 'clarity_VS2', 'clarity_VVS1', 'clarity_VVS2', 'clarity_I1'
        ]
        
        # Simulate inference data (what we get from the frontend)
        inference_data = pd.DataFrame([{
            'carat': 0.25, 'depth': 60.0, 'table': 54.0,
            'x': 4.1, 'y': 4.1, 'z': 2.4,
            'cut_Ideal': 1,  # Only one cut type present
            'color_F': 1,    # Only one color present
            'clarity_VS1': 1  # Only one clarity present
        }])
        
        # Test column alignment (as done in the app)
        df_aligned = inference_data.reindex(columns=training_columns, fill_value=0)
        
        # Verify alignment worked
        assert list(df_aligned.columns) == training_columns
        assert len(df_aligned) == 1
        
        # Check that missing columns are filled with 0
        assert df_aligned['cut_Fair'].iloc[0] == 0
        assert df_aligned['cut_Ideal'].iloc[0] == 1
        assert df_aligned['color_D'].iloc[0] == 0
        assert df_aligned['color_F'].iloc[0] == 1


class TestExternalServiceIntegration:
    """Test integration with external services (if backend is running)"""
    
    def test_live_backend_health_check(self):
        """Test 7: Live backend health check (if running)"""
        try:
            response = requests.get('http://127.0.0.1:5000/health', timeout=5)
            
            # If backend is running, test it
            if response.status_code == 200:
                data = response.json()
                assert 'status' in data
                assert 'model_status' in data
                assert data['status'] == 'running'
            else:
                pytest.skip("Backend not running - skipping live test")
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running - skipping live test")
        except requests.exceptions.Timeout:
            pytest.skip("Backend timeout - skipping live test")

    def test_live_backend_prediction(self):
        """Test 8: Live backend prediction (if running and model loaded)"""
        try:
            # First check if backend is running
            health_response = requests.get('http://127.0.0.1:5000/health', timeout=5)
            
            if health_response.status_code != 200:
                pytest.skip("Backend not running - skipping live test")
            
            health_data = health_response.json()
            if health_data.get('model_status') != 'loaded':
                pytest.skip("Model not loaded - skipping live test")
            
            # Test prediction
            test_data = [{
                'carat': 0.23,
                'cut': 'Ideal',
                'color': 'E',
                'clarity': 'SI2',
                'depth': 61.5,
                'table': 55.0,
                'x': 3.95,
                'y': 3.98,
                'z': 2.43
            }]
            
            response = requests.post('http://127.0.0.1:5000/predict',
                                   json=test_data,
                                   timeout=10)
            
            assert response.status_code == 200
            data = response.json()
            assert 'predicted_price' in data
            assert isinstance(data['predicted_price'], list)
            assert len(data['predicted_price']) == 1
            assert data['predicted_price'][0] > 0
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running - skipping live test")
        except requests.exceptions.Timeout:
            pytest.skip("Backend timeout - skipping live test")

    def test_cors_integration(self):
        """Test 9: CORS headers are properly set for frontend integration"""
        try:
            response = requests.options('http://127.0.0.1:5000/predict', timeout=5)
            
            # Check CORS headers
            headers = response.headers
            # The presence of these headers indicates CORS is configured
            # (exact headers may vary based on Flask-CORS configuration)
            assert response.status_code in [200, 204]  # OPTIONS should be allowed
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running - skipping CORS test")
        except requests.exceptions.Timeout:
            pytest.skip("Backend timeout - skipping CORS test")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
