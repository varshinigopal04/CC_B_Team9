# MFA (Multi-Factor Authentication) Microservice

A secure and efficient Flask-based microservice for implementing Multi-Factor Authentication using email-based One-Time Passwords (OTP).

## Features

- **OTP Generation**: Creates secure 6-digit one-time passwords
- **Email Delivery**: Automatically sends OTPs to the user's email
- **OTP Verification**: Validates OTPs with expiration handling
- **Rate Limiting**: Prevents abuse through built-in rate limiting
- **Security**: OTP expiration after 10 minutes
- **Clean-up**: Automatically removes used or expired OTPs

## Requirements

- Python 3.9+
- Flask 2.0.1
- Werkzeug 2.0.1
- Flask-Mail 0.9.1
- Supabase 0.5.8
- Docker & Docker Compose (for containerized deployment)

## Installation

### Using Docker (Recommended)

1. Clone the repository
2. Configure your `.env` file with your credentials
3. Run the application using Docker Compose:
   ```
   docker-compose up --build
   ```

### Manual Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up your `.env` file
5. Run the application:
   ```
   python run.py
   ```

## Environment Variables

Create a `.env` file with the following variables:

```
# Mail Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Supabase Configuration
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

## Database Setup

Create the `otp_table` in your Supabase database with the following structure:

```sql
CREATE TABLE IF NOT EXISTS public.otp_table (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    email text NOT NULL,
    otp text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_otp_table_email ON public.otp_table (email);
```

## API Endpoints

### Generate OTP

```
POST /generate-otp
```

Request body:
```json
{
  "email": "user@example.com"
}
```

Response:
```json
{
  "message": "OTP sent successfully"
}
```

### Verify OTP

```
POST /verify-otp
```

Request body:
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

Response:
```json
{
  "message": "OTP verified successfully"
}
```

