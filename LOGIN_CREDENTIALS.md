# Login Credentials - Development Mode

## How to Login (Development Mode)

Since you're in **Development Mode**, you **DON'T need a password**!
Just enter the email address and click "Sign in".

## Available Accounts

### Admin Account
- **Email**: `admin@zero2hacker.com`
- **Username**: admin
- **Role**: Admin (full access)
- **Password**: Not required in dev mode

### Test User Account
- **Email**: `testuser@example.com`
- **Username**: testuser
- **Role**: Student
- **Password**: Not required in dev mode

## How to Use

### Login Steps:
1. Open http://localhost:3000 in your browser
2. Click "Sign in" or go to the login page
3. Enter one of the emails above (e.g., `admin@zero2hacker.com`)
4. **Skip the password field** (it won't be shown in dev mode)
5. Click "Sign in"

### Create a New Account:
1. Go to the registration page
2. Fill in:
   - Email: any valid email (e.g., `yourname@example.com`)
   - Username: any unique username
   - Display Name: your name
   - Skill Level: beginner/intermediate/advanced/expert
3. Click "Create account"
4. **No password required** in development mode!

## Important Notes

- Password field is **hidden** in development mode
- You'll see a yellow banner saying "Development Mode: Password not required"
- This only works because `REACT_APP_DEV_MODE=true` in your `.env` file
- For production, you'll need to set up Firebase and use real passwords

## Backend API (for testing)

If you want to test the API directly:

### Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/dev-login?email=admin@zero2hacker.com"
```

### Register:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/dev-register?email=newuser@example.com&username=newuser&display_name=New%20User"
```

## Troubleshooting

**Can't login?**
- Make sure backend is running on port 8000
- Make sure frontend is running on port 3000
- Check that `REACT_APP_DEV_MODE=true` in `frontend/.env`
- Try refreshing the page

**Want to create admin account?**
```bash
cd backend
python create_admin.py
```

**Reset everything?**
```bash
cd backend
rm zero2hacker.db
python create_admin.py
```
