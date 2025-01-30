# Image-Processing

1. Create an S3 bucket to store original images.
2. Set up a Lambda function to automatically trigger on image uploads, add metadata to include artist name, copyright and image description, and save processed images back to S3.
3. Create a DynamoDB table to store metadata about processed images.
4. Expose REST APIs using API Gateway to retrieve processed image metadata and URLs.
5. Implement Python Lambda functions and pytest tests for image processing and DynamoDB interactions.
6. Implement automated builds using AWS CodeBuild.
7. Develop a React web application that fetches and displays processed images' information.
8. Deploy the React application to an S3 bucket and secure it with Amazon Cognito for user authentication.


#Git Commands
git config --global http.sslVerify false
