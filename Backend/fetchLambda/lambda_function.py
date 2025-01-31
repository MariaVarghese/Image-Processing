import json
import boto3 # type: ignore
from io import BytesIO
import base64

s3_client = boto3.client('s3')
bucket_name = 'processed-images-metadata'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('image-metadata')

def lambda_handler(event, context):
    try:
        # List objects in the bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        # Filter out image files (e.g., .jpg, .png)
        image_files = [obj['Key'] for obj in response.get('Contents', [])]
        
        # Retrieve metadata for each image
        images_info = []
        for key in image_files:
            print(key)
            response = s3_client.get_object(Bucket=bucket_name, Key=key)
            image_bytes = response['Body'].read()

            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            image_url = f'https://{bucket_name}.s3.amazonaws.com/{key}'

            # Retrieve metadata
            pk = key.replace('processed-', '')
            print(pk)
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('image_name').eq(pk)
            )
        
            # Construct the response
            metadata = response['Items'][0]
            print(response['Items'][0])

            images_info.append({
                'image': image_base64,
                'image_url': image_url,
                'metadata': metadata
            })
        
        print(images_info)
        # Construct the response
        result = {
            'result': images_info
        }
        print(result)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
            },
            'body': json.dumps(result)
        }
    
    except s3_client.exceptions.NoSuchKey:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Image not found'})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }