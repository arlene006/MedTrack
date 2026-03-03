# MedTrack: AWS Cloud-Enabled Healthcare Management System

MedTrack is a high-performance healthcare management platform built on a serverless-first AWS architecture. It provides a seamless experience for doctors to manage appointments and for patients to control their health records—all powered by real-time cloud notifications.

## 🚀 Key Features
- **Dual-Role Access Control**: Specialized dashboards for Patients and Medical Professionals.
- **Automated SNS Alerts**: Instant email notifications for registrations, bookings, and cancellations.
- **Dynamic Scheduling**: Real-time appointment management with searchable patient records.
- **Cloud-Native Database**: Scalable medical history storage utilizing Amazon DynamoDB.
- **Premium UI**: Modern, glassmorphic design optimized for clarity and ease of use.

## 🏗️ AWS Architecture
- **Amazon EC2**: Hosted on an Ubuntu-based instance with an Nginx reverse proxy.
- **Amazon DynamoDB**: NoSQL storage with `UsersTable` and `AppointmentsTable`.
- **Amazon SNS**: Automated messaging service for healthcare updates.
- **AWS IAM**: Secure resource access using specialized instance profiles (`flaskdynamodbsns`).

## 🛠️ Tech Stack
- **Backend**: Flask (Python 3.11)
- **Database**: Boto3 (AWS SDK for Python)
- **Frontend**: Tailwind-inspired Vanilla CSS + Jinja2 Templates
- **Deployment**: Gunicorn + Nginx + SystemD

## 🔧 Installation & Setup

### Local Development
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/medtrack_app.git
   cd medtrack_app
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

---
© 2026 MedTrack Healthcare Cloud.
