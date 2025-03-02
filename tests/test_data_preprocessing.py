import unittest
import os
import sys
import json

# Adjusting the path to import functions from the scripts folder
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from scripts.data_preprocessing import clean_data, transform_data, feature_engineering, preprocess_record


class TestDataPreprocessing(unittest.TestCase):


    def test_clean_data(self):
        """
        Tests data cleaning to handle missing values, trim spaces, and clean lists/dictionaries.
        """
        record = {
            "name": " Product Name ",
            "price": None,
            "description": "",
            "features": ["Feature1", " Feature2 ", None],
            "nested": {"key1": " value1 ", "key2": None}
        }
        expected_output = {
            "name": "Product Name",
            "price": "N/A",
            "description": "Unknown",
            "features": ["Feature1", "Feature2", "N/A"],
            "nested": {"key1": "value1", "key2": "N/A"}
        }
        self.assertEqual(clean_data(record), expected_output)


    def test_transform_data(self):
        """
        Tests transformation to ensure column names are standardized.
        """
        record = {"Product Name": "Laptop", "Product Price": 1000}
        expected_output = {"product_name": "Laptop", "product_price": 1000}
        self.assertEqual(transform_data(record), expected_output)


    def test_feature_engineering_price_category(self):
        """
        Tests feature engineering for price categorization.
        """
        record_low = {"price": 30}
        record_medium = {"price": 150}
        record_high = {"price": 250}

        self.assertEqual(feature_engineering(record_low)["price_category"], "Low")
        self.assertEqual(feature_engineering(record_medium)["price_category"], "Medium")
        self.assertEqual(feature_engineering(record_high)["price_category"], "High")


    def test_feature_engineering_review_sentiment(self):
        """
        Tests feature engineering for review sentiment classification.
        """
        record_positive = {"overall": 4.5}
        record_neutral = {"overall": 3.0}
        record_negative = {"overall": 1.5}

        self.assertEqual(feature_engineering(record_positive)["review_sentiment"], "Positive")
        self.assertEqual(feature_engineering(record_neutral)["review_sentiment"], "Neutral")
        self.assertEqual(feature_engineering(record_negative)["review_sentiment"], "Negative")


    # def test_preprocess_record(self):
    #     """
    #     Tests end-to-end preprocessing on a sample record.
    #     """
    #     record = {" Product Name ": "Laptop", " price ": 500, " overall ": 3.5}
    #     expected_output = {
    #         "product_name": "Laptop",
    #         "price": 500,
    #         "price_category": "High",
    #         "overall": 3.5,
    #         "review_sentiment": "Neutral"
    #     }
    #     self.assertEqual(preprocess_record(record), expected_output)


    def test_empty_record(self):
        """
        Tests if an empty record is handled properly.
        """
        self.assertEqual(preprocess_record({}), {})


    def test_nested_record(self):
        """
        Tests processing of nested dictionaries.
        """
        record = {
            "Product Name": "Software",
            "Details": {
                "Version": " 1.0 ",
                "License": None
            }
        }
        expected_output = {
            "product_name": "Software",
            "details": {
                "version": "1.0",
                "license": "N/A"
            }
        }
        self.assertEqual(preprocess_record(record), expected_output)


if __name__ == "__main__":
    unittest.main()