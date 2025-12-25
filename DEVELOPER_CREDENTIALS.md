# Developer Credentials

## Quick Access

For development and testing, use the **Developer** account:

```
Username: developer
Password: dev123
```

## All Default Accounts

### Developer Account (Recommended)
- **Username**: `developer`
- **Password**: `dev123`
- **Role**: Doctor
- **Purpose**: Development and testing

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Doctor
- **Purpose**: Administrative access

## Account Creation

These accounts are automatically created when you first run the application. If you delete the database (`medication_tracker.db`), they will be recreated on the next run.

## Security Notes

⚠️ **For Production:**
- Change all default passwords
- Use strong, unique passwords
- Consider implementing password complexity requirements
- Enable additional security measures (2FA, etc.)

## Creating Additional Accounts

You can create new accounts through the registration page at `/register` or by adding them programmatically in the initialization code.

## Developer Features

The developer account has full access to:
- ✅ Create, edit, and delete medications
- ✅ View dashboard and statistics
- ✅ Search and filter medications
- ✅ All standard user features

## Resetting Developer Password

If you need to reset the developer password, you can:

1. Delete the database file: `medication_tracker.db`
2. Restart the application (developer account will be recreated)
3. Or modify the password in `medication_app.py` initialization code
