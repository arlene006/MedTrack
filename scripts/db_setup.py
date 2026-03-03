import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def create_internship_tables():
    # Use local DynamoDB if specified, otherwise AWS
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'eu-north-1')
    
    if aws_access_key and aws_secret_key:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
    else:
        dynamodb = boto3.resource('dynamodb', region_name=region)

    # 1. UsersTable (Partition Key: email)
    try:
        print("Creating UsersTable...")
        table = dynamodb.create_table(
            TableName='UsersTable',
            KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        table.wait_until_exists()
        print("UsersTable created successfully.")
    except Exception as e:
        print(f"Error creating UsersTable: {e}")

    # 2. AppointmentsTable (Partition Key: appointment_id)
    try:
        print("Creating AppointmentsTable...")
        table = dynamodb.create_table(
            TableName='AppointmentsTable',
            KeySchema=[{'AttributeName': 'appointment_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[
                {'AttributeName': 'appointment_id', 'AttributeType': 'S'},
                {'AttributeName': 'patient_email', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'PatientIndex',
                    'KeySchema': [{'AttributeName': 'patient_email', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        table.wait_until_exists()
        print("AppointmentsTable created successfully.")
    except Exception as e:
        print(f"Error creating AppointmentsTable: {e}")

if __name__ == "__main__":
    create_internship_tables()
