import json
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        print(event)
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        print("Bucket :: ",bucket)
        print("Key :: ", key)

        obj = s3.get_object(Bucket=bucket, Key=key)
        image_data = obj['Body'].read()
        print("Image Data :: ", image_data)

        response = s3.head_object(Bucket=bucket, Key=key)
        print("Response :: ", response)
        metadata = {}
        if 'Metadata' in response:
            metadata = response['Metadata']
        
        print("Metadata :: ", metadata)
        # TODO implement
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    except Exception as ex:
        print(ex)
        return {
            'statusCode': 500,
            'body': json.dumps('Error!')
        }