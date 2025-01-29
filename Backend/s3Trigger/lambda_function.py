import boto3
import piexif
import imageio
import numpy as np
from io import BytesIO
from scipy.ndimage import zoom, gaussian_filter

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

        # Enhance resolution by upscaling the image
        image = zoom(image, (2, 2, 1))  # Upscale by a factor of 2

        # Apply a Gaussian blur to smooth out pixelation
        image = gaussian_filter(image, sigma=1)

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
        imageio.imwrite(output_buffer, gray_image, format='jpg')
        output_buffer.seek(0)  # Reset buffer position to the beginning
        piexif.insert(exif_bytes, output_buffer.getvalue(), output_buffer)
        output_buffer.seek(0)  # Reset buffer position to the beginning again after insertion
        print(output_buffer.getvalue())

        print("Save image in s3")
        s3_client.put_object(Bucket='processed-images-metadata', Key='processed-' + object_key, Body=output_buffer.getvalue())

        print("Save image details in dynamodb")
        # Store metadata in DynamoDB
        table = dynamodb.Table('image-metadata')
        table.put_item(
            Item={
                'image_name': object_key,
                'artist_name': artist,
                'copyright': copyright,
                'description': description
            }
        )
    
        print("Done")
        return {
            'statusCode': 200,
            'body': 'Image processed, metadata extracted, and saved to S3. Metadata stored in DynamoDB.'
        }
            
    except Exception as ex:
        return {
            'statusCode': 500,
            'body': f'Exception: {ex}'
        }