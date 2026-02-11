# User Log API with Auth0 Authentication

This API provides user management functionality with Auth0 authentication and activity logging.

## Features

- User signup/signin (local authentication)
- Auth0 JWT token authentication for protected endpoints
- Activity logging for all API access
- User profile management
- Password change functionality

## Setup

### 1. Install Dependencies

```bash
# Activate virtual environment
.\env\Scripts\activate

# Install required packages
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] auth0-python requests
```

### 2. Configure Auth0

1. Create an Auth0 account at https://auth0.com
2. Create a new API application in Auth0 dashboard
3. Update your `.env` file with your Auth0 configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=user_data
DB_USER=postgres
DB_PASS=your_password
DB_SCHEMA=public

# Auth0 Configuration
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_API_AUDIENCE=your-api-identifier
```

### 3. Database Setup

The application will automatically create the required tables:
- `user_data` - User information
- `user_activity` - Activity logs

### 4. Run the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Public Endpoints (No Authentication Required)

- `GET /health` - Health check
- `POST /signin` - User signin
- `POST /signup` - User signup
- `POST /profile` - View profile (with email/password)
- `POST /update` - Update profile
- `POST /change-password` - Change password
- `GET /api/docs` - API documentation

### Protected Endpoints (Auth0 Token Required)

- `GET /api/protected` - Example protected endpoint
- `GET /api/user/activities` - Get current user's activity logs
- `GET /api/admin/activities` - Get all user activities
- `GET /api/user/profile` - Get profile from Auth0 token

## Usage Examples

### 1. User Signup (Local)

```bash
curl -X POST "http://localhost:8000/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-01",
    "age": 30,
    "blood_group": "O+"
  }'
```

### 2. Access Protected Endpoint

First, get a JWT token from Auth0, then:

```bash
curl -X GET "http://localhost:8000/api/protected" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. Get User Activities

```bash
curl -X GET "http://localhost:8000/api/user/activities" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Activity Logging

The system automatically logs:
- User ID and email
- Action performed (LOGIN, API_ACCESS, etc.)
- Endpoint accessed
- IP address and user agent
- Timestamp
- Status (SUCCESS/FAILED)
- Additional details

## Database Schema

### user_data Table
- `id` - UUID (Primary Key)
- `name` - String
- `email` - String (Unique)
- `password` - String (Hashed)
- `phone_number` - String (Optional)
- `date_of_birth` - Date (Optional)
- `age` - Integer (Optional)
- `blood_group` - String (Optional)
- Timestamp fields for tracking

### user_activity Table
- `id` - UUID (Primary Key)
- `user_id` - String (Auth0 User ID)
- `user_email` - String
- `action` - String
- `endpoint` - String
- `ip_address` - String
- `user_agent` - String
- `timestamp` - DateTime
- `status` - String
- `details` - String

## Development

The application uses:
- FastAPI for the web framework
- SQLAlchemy for ORM
- PostgreSQL for database
- Auth0 for authentication
- JWT tokens for API security
