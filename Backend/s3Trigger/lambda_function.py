import boto3
import cv2
import numpy as np
from io import BytesIO
import piexif

# Initialize the S3 client
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        print(event)

        # Get the bucket name and object key from the event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']
        
        # Get the image object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        image_bytes = response['Body'].read()
        
        # Convert bytes to a NumPy array
        image_array = np.frombuffer(image_bytes, np.uint8)
        
        # Decode the image array to get the image
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Process the image (example: convert to grayscale)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Extract existing metadata using piexif
        exif_dict = piexif.load(BytesIO(image_bytes).getvalue())
        artist = exif_dict['0th'].get(piexif.ImageIFD.Artist, "Unknown Artist")
        copyright = exif_dict['0th'].get(piexif.ImageIFD.Copyright, "Unknown Copyright")
        description = exif_dict['0th'].get(piexif.ImageIFD.ImageDescription, "No Description")
        
        # Print or log extracted metadata (example: print to CloudWatch logs)
        print(f"Artist: {artist}")
        print(f"Copyright: {copyright}")
        print(f"Description: {description}")
        
        # Save the processed image with existing metadata
        exif_bytes = piexif.dump(exif_dict)
        _, buffer = cv2.imencode('.jpg', gray_image)
        image_with_metadata = piexif.insert(exif_bytes, buffer.tobytes())
        s3_client.put_object(Bucket='processed-images-metadata', Key='processed-' + object_key, Body=image_with_metadata)
        
        # Store metadata in DynamoDB
        table = dynamodb.Table('image-metadata')
        table.put_item(
            Item={
                'ImageKey': 'processed-' + object_key,
                'Artist': "Artist Name",
                'Copyright': "© 2025 Artist Name",
                'Description': "Image Description"
            }
        )
        
        return {
            'statusCode': 200,
            'body': 'Image processed, metadata added, and saved to S3. Metadata stored in DynamoDB.'
        }
    except Exception as ex:
        return {
            'statusCode': 500,
            'body': f'Error : {ex}'
        }