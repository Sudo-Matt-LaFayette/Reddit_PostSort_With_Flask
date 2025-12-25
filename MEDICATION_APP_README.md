# Medication Dosage Tracking App

A Flask-based web application for doctors and medical students to track medication dosages and frequencies.

## Features

- 🔐 **User Authentication**: Secure login and registration system
- 💊 **Medication Management**: Add, edit, delete, and view medications
- 📊 **Dashboard**: Overview with statistics and recent medications
- 🔍 **Search & Filter**: Find medications by name or frequency type
- 📈 **Frequency Tracking**: Track dosage count and frequency (daily, weekly, as needed, custom)
- 👤 **User Roles**: Support for doctors and students

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python medication_app.py
```

The application will be available at `http://localhost:5001`

### 3. Default Login Credentials

On first run, a default admin user is created:
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ Important**: Change the default password in production!

## Usage

### Registration

1. Navigate to `/register` to create a new account
2. Choose your role (Doctor or Student)
3. Fill in username, email, and password
4. Login with your credentials

### Adding Medications

1. Click "Add Medication" from the dashboard or medications page
2. Fill in:
   - Medication name (required)
   - Dosage amount (e.g., "500mg", "2 tablets")
   - Number of dosages
   - Frequency type (Daily, Weekly, As Needed, Custom)
   - Frequency value and unit
   - Optional notes
3. Click "Add Medication"

### Viewing Medications

- **Dashboard**: Overview with statistics and recent medications
- **Medications List**: All medications with search and filter options
- **Medication Detail**: Full information about a specific medication

### Searching and Filtering

- Use the search box to find medications by name
- Filter by frequency type (Daily, Weekly, As Needed, Custom)
- Results update in real-time

## Database

The app uses SQLite (`medication_tracker.db`) for data storage. The database is automatically created on first run.

### Database Schema

**Users Table**:
- id, username, email, password_hash, role, created_at, last_login

**Medications Table**:
- id, name, dosage_amount, dosage_count, frequency_type, frequency_value, frequency_unit, notes, created_at, updated_at, created_by

## Routes

- `/` - Dashboard (requires login)
- `/login` - Login page
- `/register` - Registration page
- `/logout` - Logout
- `/medications` - List all medications
- `/medications/new` - Add new medication
- `/medications/<id>` - View medication details
- `/medications/<id>/edit` - Edit medication
- `/medications/<id>/delete` - Delete medication (POST)

## Security Features

- Password hashing using Werkzeug's PBKDF2
- Session management with Flask-Login
- User authentication required for all medication operations
- Users can only access their own medications

## Technology Stack

- **Backend**: Flask 2.2.5
- **Database**: SQLite with SQLAlchemy
- **Authentication**: Flask-Login
- **Frontend**: Bootstrap 5, Font Awesome
- **Password Security**: Werkzeug

## Development Notes

- The app runs on port 5001 to avoid conflicts with other Flask apps
- Debug mode is enabled by default (disable in production)
- Secret key should be changed in production (set via environment variable `SECRET_KEY`)

## Future Enhancements

- Patient association (link medications to patients)
- Medication history/audit log
- Export functionality (CSV/PDF)
- Charts and visualizations
- Medication reminders/notifications
- Multi-user collaboration

## License

This project is open source and available under the MIT License.
