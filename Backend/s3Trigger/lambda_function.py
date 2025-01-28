import boto3
import numpy as np
from io import BytesIO
import piexif
import imageio

# Initialize the S3 client
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        print(event)

        # Get the bucket name and object key from the event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']
        print(bucket_name)
        
        # Get the image object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        image_bytes = response['Body'].read()
        
        # Decode the image array to get the image
        image = imageio.imread(BytesIO(image_bytes))

        # Process the image (example: convert to grayscale)
        gray_image = np.dot(image[...,:3], [0.2989, 0.5870, 0.1140])  # Convert to grayscale
        gray_image = (gray_image * 255).astype(np.uint8)  # Convert to uint8 format

        # Extract existing metadata using piexif
        exif_dict = piexif.load(BytesIO(image_bytes).getvalue())
        artist = exif_dict['0th'].get(piexif.ImageIFD.Artist, "Unknown Artist")
        copyright = exif_dict['0th'].get(piexif.ImageIFD.Copyright, "Unknown Copyright")
        description = exif_dict['0th'].get(piexif.ImageIFD.ImageDescription, "No Description")
        
        # Print or log extracted metadata (example: print to CloudWatch logs)
        print(f"Artist: {artist}")
        print(f"Copyright: {copyright}")
        print(f"Description: {description}")
        
        print("Processing Image")
        # Save the processed image with existing metadata
        exif_bytes = piexif.dump(exif_dict)
        output_buffer = BytesIO()
        imageio.imwrite(output_buffer, gray_image, format='jpeg')
        image_with_metadata = piexif.insert(exif_bytes, output_buffer.getvalue())

        print("Save image in s3")
        s3_response = s3_client.put_object(Bucket='processed-images-metadata', Key='processed-' + object_key, Body=image_with_metadata)
        print("S3 Response :: "+s3_response)

        print("Save image details in dynamodb")
        # Store metadata in DynamoDB
        table = dynamodb.Table('image-metadata')
        response = table.put_item(
            Item={
                'ImageKey': 'processed-' + object_key,
                'Artist': artist,
                'Copyright': copyright,
                'Description': description
            }
        )
        print("DynamoDB response :: "+response)
        
        return {
            'statusCode': 200,
            'body': 'Image processed, metadata extracted, and saved to S3. Metadata stored in DynamoDB.'
        }
    except Exception as ex:
        return {
            'statusCode': 500,
            'body': f'Exception: {ex}'
        }