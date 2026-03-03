import boto3
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

def seed_doctors():
    # Use credentials and region from .env
    region = os.getenv('AWS_REGION', 'eu-north-1')
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if aws_access_key and aws_secret_key:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
    else:
        dynamodb = boto3.resource('dynamodb', region_name=region)
        
    table = dynamodb.Table('UsersTable')
    
    doctors = [
        {
            'email': 'sarah@medtrack.com',
            'Name': 'Dr. Sarah Connor',
            'PasswordHash': generate_password_hash('doctor123'),
            'Specialization': 'Cardiology',
            'Role': 'doctor',
            'Phone': '9876543210'
        },
        {
            'email': 'james@medtrack.com',
            'Name': 'Dr. James Smith',
            'PasswordHash': generate_password_hash('doctor123'),
            'Specialization': 'Neurology',
            'Role': 'doctor',
            'Phone': '9876543211'
        }
    ]
    
    for doc in doctors:
        try:
            print(f"Seeding doctor: {doc['Name']}...")
            table.put_item(Item=doc)
            print("Done.")
        except Exception as e:
            print(f"Error seeding {doc['Name']}: {e}")

if __name__ == "__main__":
    seed_doctors()
