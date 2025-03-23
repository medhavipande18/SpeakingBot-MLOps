"""
Test suite for RAG-based assistant.
"""
import os
import json
import numpy as np
import pytest
from unittest.mock import patch, MagicMock

# Import modules to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app as flask_app
from rag_helper import get_query_embedding, fetch_top_k_chunks

# Setup test data
@pytest.fixture
def test_metadata():
    return [
        {
            "parent_asin": "ABC123",
            "title": "Test Software 1",
            "chunk_text": "Title: Test Software 1\nRating: 4.5\nPrice: $49.99\nCategories: Productivity, Business"
        },
        {
            "parent_asin": "DEF456",
            "title": "Test Software 2",
            "chunk_text": "Title: Test Software 2\nRating: 3.8\nPrice: $29.99\nCategories: Graphics, Design"
        }
    ]

@pytest.fixture
def mock_faiss_index():
    mock_index = MagicMock()
    mock_index.search.return_value = (
        np.array([[0.85, 0.75]]),  # distances
        np.array([[0, 1]])         # indices
    )
    return mock_index

# Test app.py endpoints
class TestApp:
    @pytest.fixture
    def client(self):
        flask_app.config['TESTING'] = True
        with flask_app.test_client() as client:
            yield client
    
    @patch('app.fetch_top_k_chunks')
    @patch('app.client.chat.completions.create')
    def test_chat_endpoint(self, mock_openai, mock_fetch_chunks, client):
        # Mock the OpenAI response
        mock_message = MagicMock()
        mock_message.content = "This is a test response.\nProduct: Test Software 1"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_openai.return_value = mock_response
        
        # Mock the RAG retrieval
        mock_fetch_chunks.return_value = [
            {
                "parent_asin": "ABC123",
                "title": "Test Software 1",
                "chunk_text": "Title: Test Software 1\nRating: 4.5\nPrice: $49.99"
            }
        ]
        
        # Test the endpoint
        response = client.post('/chat', json={'message': 'Tell me about test software'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert "response" in data
        assert "product_name" in data
        assert data["product_name"] == "Test Software 1"

# Test rag_helper.py
class TestRagHelper:
    @patch('rag_helper.openai.embeddings.create')
    def test_get_query_embedding(self, mock_openai):
        # Mock the OpenAI embeddings response
        mock_data = MagicMock()
        mock_data.embedding = [0.1, 0.2, 0.3]
        mock_response = MagicMock()
        mock_response.data = [mock_data]
        mock_openai.return_value = mock_response
        
        # Test embedding generation
        embedding = get_query_embedding("test query")
        
        # Assert OpenAI was called
        mock_openai.assert_called_once()
        
        # Check embedding shape and normalization
        assert embedding.shape[1] == 3  # dimensions
        assert np.isclose(np.linalg.norm(embedding), 1.0)  # should be normalized
    
    @patch('rag_helper.faiss_index', new_callable=MagicMock)
    @patch('rag_helper.metadata_list')
    @patch('rag_helper.get_query_embedding')
    def test_fetch_top_k_chunks(self, mock_get_embedding, mock_metadata, mock_index, test_metadata):
        # Mock embeddings and metadata
        mock_get_embedding.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_metadata.__getitem__.side_effect = test_metadata.__getitem__
        mock_metadata.__len__.return_value = len(test_metadata)
        
        # Mock FAISS search
        mock_index.search.return_value = (
            np.array([[0.85, 0.75]]),  # distances
            np.array([[0, 1]])         # indices
        )
        
        # Test chunk retrieval
        results = fetch_top_k_chunks("test query", k=2)
        
        # Assertions
        assert len(results) == 2
        assert results[0]["parent_asin"] == "ABC123"
        assert results[1]["parent_asin"] == "DEF456"
        assert "similarity" in results[0]
        assert "similarity" in results[1]

# Test model_validation.py (placeholder tests)
def test_validation_thresholds():
    """Ensure validation thresholds are reasonable"""
    # Importing directly from the file to check constants
    import importlib.util
    spec = importlib.util.spec_from_file_location("model_validation", 
                                                 os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                             "model_validation.py"))
    model_validation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model_validation)
    
    # Check thresholds
    assert hasattr(model_validation, 'MIN_RECALL_THRESHOLD')
    assert hasattr(model_validation, 'MIN_MRR_THRESHOLD')
    assert 0 <= model_validation.MIN_RECALL_THRESHOLD <= 1
    assert 0 <= model_validation.MIN_MRR_THRESHOLD <= 1

# Test bias_detection.py (placeholder tests)
def test_bias_detection_thresholds():
    """Ensure bias detection thresholds are reasonable"""
    # Importing directly from the file to check constants
    import importlib.util
    spec = importlib.util.spec_from_file_location("bias_detection", 
                                                 os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                             "bias_detection.py"))
    bias_detection = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bias_detection)
    
    # Check thresholds
    assert hasattr(bias_detection, 'MAX_PRICE_DISPARITY')
    assert hasattr(bias_detection, 'MIN_CATEGORY_REPRESENTATION')
    assert hasattr(bias_detection, 'MAX_RATING_BIAS')
    assert 0 <= bias_detection.MAX_PRICE_DISPARITY <= 1
    assert 0 <= bias_detection.MIN_CATEGORY_REPRESENTATION <= 1
    assert 0 <= bias_detection.MAX_RATING_BIAS <= 1

# Run the tests
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])