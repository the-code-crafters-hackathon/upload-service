import json
import logging
import os
from typing import Dict, Any
import boto3

logger = logging.getLogger(__name__)


class SQSProducer:
    def __init__(self):
        self.queue_url = os.getenv("SQS_VIDEO_PROCESSING_QUEUE")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        
        # Initialize SQS client
        self.client = boto3.client(
            'sqs',
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            endpoint_url=os.getenv("AWS_ENDPOINT_URL")  # For LocalStack in development
        )
        
        logger.info(f"SQS Producer inicializado - Queue: {self.queue_url}")

    def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send a message to SQS queue
        
        Args:
            message: Dictionary with video processing instructions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message)
            )
            
            logger.info(f"Mensagem enviada ao SQS: {response['MessageId']}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem ao SQS: {str(e)}")
            return False
