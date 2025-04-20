import boto3
import logging
import os
from datetime import datetime

class BackupManager:
    def __init__(self, aws_access_key, aws_secret_key, aws_bucket_name, aws_region):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_bucket_name = aws_bucket_name
        self.aws_region = aws_region
        
    def get_s3_client(self):
        """Get an S3 client"""
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            return s3_client
        except Exception as e:
            logging.error(f"Error creating S3 client: {str(e)}")
            raise
    
    def list_s3_backups(self):
        """List all backups in the S3 bucket"""
        try:
            s3_client = self.get_s3_client()
            response = s3_client.list_objects_v2(Bucket=self.aws_bucket_name)
            
            if 'Contents' not in response:
                return []
            
            backups = []
            for obj in response['Contents']:
                backups.append({
                    'name': obj['Key'],
                    'size': round(obj['Size'] / (1024**2), 2),  # MB
                    'date': obj['LastModified']
                })
            
            # Sort by date, newest first
            return sorted(backups, key=lambda x: x['date'], reverse=True)
        except Exception as e:
            logging.error(f"Error listing S3 backups: {str(e)}")
            raise
    
    def upload_to_s3(self, file_path, object_name=None):
        """Upload a file to S3 bucket"""
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        try:
            s3_client = self.get_s3_client()
            s3_client.upload_file(file_path, self.aws_bucket_name, object_name)
            return True
        except Exception as e:
            logging.error(f"Error uploading to S3: {str(e)}")
            raise
    
    def download_from_s3(self, object_name, file_path):
        """Download a file from S3 bucket"""
        try:
            s3_client = self.get_s3_client()
            s3_client.download_file(self.aws_bucket_name, object_name, file_path)
            return True
        except Exception as e:
            logging.error(f"Error downloading from S3: {str(e)}")
            raise
    
    def delete_from_s3(self, object_name):
        """Delete a file from S3 bucket"""
        try:
            s3_client = self.get_s3_client()
            s3_client.delete_object(Bucket=self.aws_bucket_name, Key=object_name)
            return True
        except Exception as e:
            logging.error(f"Error deleting from S3: {str(e)}")
            raise 