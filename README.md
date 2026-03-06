# MedTrack: AWS Cloud-Enabled Healthcare Management System

MedTrack is a high-performance healthcare management platform built on a serverless-first AWS architecture. It provides a seamless experience for doctors to manage appointments and for patients to control their health records—all powered by real-time cloud notifications.

[![GitHub Repository](https://img.shields.io/badge/GitHub-MedTrack-blue?logo=github)](https://github.com/arlene006/MedTrack)

## 🚀 Key Features

- **Dual-Role Access Control**: 
  - **Patient Dashboard**: Book appointments, view medical history, and receive real-time updates.
  - **Doctor Dashboard**: Manage patient schedules, submit diagnoses, and track treatment plans.
- **Real-Time Cloud Notifications**: 
  - Automated **AWS SNS** alerts sent via email for registration, booking confirmations, and cancellations.
  - Automatic SNS subscription during user registration.
- **Smart Appointment Management**:
  - Global search functionality to filter appointments by patient name.
  - Seamless booking system with detailed reason-of-visit tracking.
  - One-click cancellation for both doctors and patients.
- **Digital Health Records**: 
  - Persistent storage of medical history utilizing **Amazon DynamoDB**.
  - Track diagnoses, observations, and treatments over time.
- **Secure Authentication**: 
  - Role-based login system with securely hashed credentials (Werkzeug).
- **Premium UI**: 
  - Modern, glassmorphic design built with Vanilla CSS and Tailwind-inspired layouts for maximum clarity.

## 🏗️ AWS Architecture

- **Amazon EC2**: High-availability hosting on Ubuntu with Gunicorn/Nginx.
- **Amazon DynamoDB**: Scalable NoSQL storage for `UsersTable` and `AppointmentsTable`.
- **Amazon SNS**: Automated messaging service for instant healthcare updates.
- **AWS IAM**: Secure resource access using specialized instance profiles (`flaskdynamodbsns`).

## 🛠️ Tech Stack

- **Backend**: Flask (Python 3.11)
- **AWS SDK**: Boto3 for DynamoDB and SNS integration.
- **Frontend**: Jinja2 Templates + Vanilla CSS (Modern UI).
- **Security**: Werkzeug Security for password hashing.
- **Deployment**: Gunicorn + Nginx + SystemD.

## 🔧 Installation & Setup

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/arlene006/MedTrack.git
   cd MedTrack
   ```

2. **Setup environment variables**:
   Create a `.env` file with your AWS credentials:
   ```env
   AWS_REGION=eu-north-1
   SECRET_KEY=your_secret_key
   SNS_TOPIC_ARN=your_sns_arn
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

### Cloud Deployment

- Deploy on **AWS EC2** using the provided `medtrack.service` and `medtrack.nginx.conf` files.
- Ensure the EC2 instance is attached to the `flaskdynamodbsns` IAM role for secure database access.

## 👥 Contributors
- **Arlene** - *Lead Developer & Cloud Architect*
- **Ravi Teja** - *Original Cloud Contributor*

---
© 2026 MedTrack Healthcare Cloud.
