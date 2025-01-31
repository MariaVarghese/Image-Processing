import pytest
from unittest.mock import patch, MagicMock
import boto3
from botocore.stub import Stubber
from fetchLambda.lambda_function import lambda_handler # type: ignore

@pytest.fixture
def s3_event():
    return {
        'Records': [
            {
                's3': {
                    'bucket': {
                        'name': 'test-bucket'
                    },
                    'object': {
                        'key': 'test-image.jpg'
                    }
                }
            }
        ]
    }

@pytest.fixture
def s3_client_stub():
    s3 = boto3.client('s3')
    with Stubber(s3) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()

@pytest.fixture
def dynamodb_stub():
    dynamodb = boto3.resource('dynamodb')
    with patch('boto3.resource') as mock_dynamodb:
        mock_dynamodb.return_value = dynamodb
        yield mock_dynamodb

@patch('lambda_function.s3_client')
@patch('lambda_function.dynamodb')
def test_lambda_handler(mock_dynamodb, mock_s3_client, s3_event, s3_client_stub, dynamodb_stub):
    # Mock S3 list_objects_v2 response
    mock_s3_client.list_objects_v2.return_value = {
        'Contents': [{'Key': 'processed-test-image.jpg'}]
    }

    # Mock S3 get_object response
    mock_s3_client.get_object.return_value = {
        'Body': MagicMock(read=lambda: b'test-image-bytes')
    }

    # Mock DynamoDB table query response
    mock_table = MagicMock()
    mock_table.query.return_value = {
        'Items': [{
            'image_name': 'test-image.jpg',
            'artist_name': 'Test Artist',
            'copyright': 'Test Copyright',
            'description': 'Test Description'
        }]
    }
    mock_dynamodb.Table.return_value = mock_table

    # Call the lambda handler
    response = lambda_handler(s3_event, None)

    # Assertions
    assert response['statusCode'] == 200
    mock_s3_client.list_objects_v2.assert_called_once_with(Bucket='processed-images-metadata')
    mock_s3_client.get_object.assert_called_once_with(Bucket='processed-images-metadata', Key='processed-test-image.jpg')
    mock_table.query.assert_called_once()