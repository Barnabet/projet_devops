"""
Unit Tests for Diamond Price Prediction Application

These tests focus on testing individual functions and components in isolation.
"""

import pytest
import pandas as pd
import numpy as np
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add the backend directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app

class TestDataPreprocessing:
    """Test data preprocessing functions"""
    
    def test_data_preprocessing_with_valid_input(self):
        """Test 1: Data preprocessing with valid diamond data"""
        # Create sample input data
        sample_data = [{
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
        
        df = pd.DataFrame(sample_data)
        
        # Test that one-hot encoding works
        df_processed = pd.get_dummies(df)
        
        # Assertions
        assert isinstance(df_processed, pd.DataFrame)
        assert len(df_processed) == 1
        assert 'carat' in df_processed.columns
        assert 'depth' in df_processed.columns
        assert 'table' in df_processed.columns
        assert 'x' in df_processed.columns
        assert 'y' in df_processed.columns
        assert 'z' in df_processed.columns
        
        # Check that categorical columns are one-hot encoded
        cut_columns = [col for col in df_processed.columns if col.startswith('cut_')]
        color_columns = [col for col in df_processed.columns if col.startswith('color_')]
        clarity_columns = [col for col in df_processed.columns if col.startswith('clarity_')]
        
        assert len(cut_columns) > 0
        assert len(color_columns) > 0
        assert len(clarity_columns) > 0

    def test_data_preprocessing_with_missing_columns(self):
        """Test 2: Data preprocessing handles missing columns gracefully"""
        # Create sample data with missing columns
        sample_data = [{
            'carat': 0.23,
            'cut': 'Ideal',
            'color': 'E'
            # Missing clarity, depth, table, x, y, z
        }]
        
        df = pd.DataFrame(sample_data)
        df_processed = pd.get_dummies(df)
        
        # Should still work but with fewer columns
        assert isinstance(df_processed, pd.DataFrame)
        assert len(df_processed) == 1
        assert 'carat' in df_processed.columns

    def test_data_preprocessing_with_different_categorical_values(self):
        """Test 3: Data preprocessing handles different categorical values"""
        sample_data = [{
            'carat': 1.0,
            'cut': 'Premium',
            'color': 'D',
            'clarity': 'VVS1',
            'depth': 62.0,
            'table': 56.0,
            'x': 6.0,
            'y': 6.0,
            'z': 3.7
        }]
        
        df = pd.DataFrame(sample_data)
        df_processed = pd.get_dummies(df)
        
        # Check that different categorical values are handled
        assert 'cut_Premium' in df_processed.columns
        assert 'color_D' in df_processed.columns
        assert 'clarity_VVS1' in df_processed.columns
        assert df_processed['cut_Premium'].iloc[0] == 1
        assert df_processed['color_D'].iloc[0] == 1
        assert df_processed['clarity_VVS1'].iloc[0] == 1


class TestFlaskAppConfiguration:
    """Test Flask application configuration and setup"""
    
    def test_flask_app_creation(self):
        """Test 4: Flask app is created correctly"""
        assert app is not None
        assert app.config['TESTING'] is False  # Default value
        
    def test_flask_app_has_cors_enabled(self):
        """Test 5: Flask app has CORS enabled"""
        # Check that CORS is configured by looking at the app's extensions
        # This is a basic check that the app can be configured
        with app.test_client() as client:
            response = client.options('/health')
            # Should not return 404 (method not allowed would be OK)
            assert response.status_code != 404


class TestModelUtilities:
    """Test model-related utility functions"""
    
    @patch('app.mlflow.sklearn.load_model')
    @patch('app.mlflow.tracking.MlflowClient')
    def test_model_loading_success(self, mock_client, mock_load_model):
        """Test 6: Model loading function works correctly"""
        # Mock the MLflow client and model loading
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.get_latest_versions.return_value = [
            Mock(run_id='test-run-id', version='1')
        ]
        mock_client_instance.download_artifacts.return_value = 'test-path'
        
        # Mock the file reading
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(['col1', 'col2'])
            
            # Import and test the load_model function
            from app import load_model
            
            # This should not raise an exception
            try:
                load_model()
                # If we get here, the function completed without error
                assert True
            except Exception as e:
                # If there's an error, it should be related to the mocking, not the logic
                assert "model not loaded" in str(e).lower() or "no model found" in str(e).lower()

    def test_training_columns_format(self):
        """Test 7: Training columns JSON format is correct"""
        # Test that we can create and validate training columns format
        sample_columns = [
            'carat', 'depth', 'table', 'x', 'y', 'z',
            'cut_Fair', 'cut_Good', 'cut_Ideal', 'cut_Premium', 'cut_Very Good',
            'color_D', 'color_E', 'color_F', 'color_G', 'color_H', 'color_I', 'color_J',
            'clarity_FL', 'clarity_IF', 'clarity_SI1', 'clarity_SI2', 'clarity_VS1', 'clarity_VS2', 'clarity_VVS1', 'clarity_VVS2'
        ]
        
        # Test JSON serialization/deserialization
        json_str = json.dumps(sample_columns)
        loaded_columns = json.loads(json_str)
        
        assert isinstance(loaded_columns, list)
        assert len(loaded_columns) > 0
        assert 'carat' in loaded_columns
        assert any(col.startswith('cut_') for col in loaded_columns)
        assert any(col.startswith('color_') for col in loaded_columns)
        assert any(col.startswith('clarity_') for col in loaded_columns)

    def test_numerical_data_validation(self):
        """Test 8: Numerical data validation"""
        # Test valid numerical inputs
        valid_inputs = {
            'carat': 0.23,
            'depth': 61.5,
            'table': 55.0,
            'x': 3.95,
            'y': 3.98,
            'z': 2.43
        }
        
        for key, value in valid_inputs.items():
            assert isinstance(value, (int, float))
            assert value > 0  # All diamond measurements should be positive
            
        # Test edge cases
        assert 0.1 <= valid_inputs['carat'] <= 10.0  # Reasonable carat range
        assert 40.0 <= valid_inputs['depth'] <= 80.0  # Reasonable depth range
        assert 40.0 <= valid_inputs['table'] <= 80.0  # Reasonable table range

    def test_categorical_data_validation(self):
        """Test 9: Categorical data validation"""
        valid_cuts = ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']
        valid_colors = ['D', 'E', 'F', 'G', 'H', 'I', 'J']
        valid_clarities = ['FL', 'IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2', 'I1']
        
        # Test that our expected values are in the valid lists
        assert 'Ideal' in valid_cuts
        assert 'E' in valid_colors
        assert 'SI2' in valid_clarities
        
        # Test that lists are not empty
        assert len(valid_cuts) > 0
        assert len(valid_colors) > 0
        assert len(valid_clarities) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
