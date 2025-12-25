# Medication Dosage Tracking App - Planning Document

## Overview
An app where doctors (or potential doctors) can log in and view medication dosage information including:
- Number of dosages
- Frequency of medications

## Core Features

### 1. User Authentication & Authorization
- **Login System**: Secure authentication for doctors/users
- **User Roles**: 
  - Doctor/Admin (full access)
  - Potential Doctor/Student (view-only or limited access)
- **Session Management**: Secure session handling

### 2. Medication Management
- **View Medications**: List all medications with dosage information
- **Dosage Details**: 
  - Number of dosages per medication
  - Frequency (e.g., "3 times daily", "every 8 hours", "once weekly")
  - Dosage amount (e.g., "500mg", "2 tablets")
- **Patient Association** (if multi-patient):
  - Link medications to specific patients
  - View patient medication history

### 3. Dashboard/Overview
- **Summary View**: 
  - Total medications tracked
  - Medications by frequency category
  - Recent medication additions/changes
- **Visualizations**: 
  - Charts showing dosage frequency distribution
  - Medication schedule timeline

### 4. Search & Filter
- Search medications by name
- Filter by frequency (daily, weekly, etc.)
- Filter by dosage count
- Sort by various criteria

## Data Model

### Users Table
```
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash (Hashed password)
- role (doctor/student)
- created_at
- last_login
```

### Medications Table
```
- id (Primary Key)
- name (e.g., "Aspirin", "Metformin")
- dosage_amount (e.g., "500mg", "2 tablets")
- dosage_count (Integer - number of times)
- frequency (e.g., "daily", "twice daily", "every 8 hours")
- frequency_type (enum: 'daily', 'weekly', 'as_needed', 'custom')
- frequency_value (Integer - e.g., 3 for "3 times")
- frequency_unit (e.g., "per day", "per week", "hours")
- notes (Optional text field)
- created_at
- updated_at
- created_by (Foreign Key to Users)
```

### Patients Table (Optional - if multi-patient)
```
- id (Primary Key)
- patient_id (Unique identifier)
- first_name
- last_name
- date_of_birth
- created_at
```

### Patient_Medications Table (Optional - if multi-patient)
```
- id (Primary Key)
- patient_id (Foreign Key)
- medication_id (Foreign Key)
- prescribed_date
- end_date (Optional)
- active (Boolean)
```

## User Interface Design

### Pages/Routes Needed

1. **Login Page** (`/login`)
   - Username/email and password fields
   - "Remember me" option
   - Link to registration (if applicable)

2. **Dashboard** (`/`)
   - Overview statistics
   - Recent medications
   - Quick actions
   - Charts/visualizations

3. **Medications List** (`/medications`)
   - Table/list view of all medications
   - Search and filter options
   - Add new medication button
   - Edit/Delete actions

4. **Add/Edit Medication** (`/medications/new`, `/medications/<id>/edit`)
   - Form fields:
     - Medication name
     - Dosage amount
     - Number of dosages
     - Frequency selection (dropdown or custom input)
     - Notes (optional)
   - Save/Cancel buttons

5. **Medication Details** (`/medications/<id>`)
   - Full medication information
   - Dosage schedule visualization
   - Edit/Delete options

6. **Reports/Analytics** (`/reports`) - Optional
   - Frequency distribution charts
   - Medication usage statistics
   - Export capabilities

## Technology Stack Recommendations

### Backend
- **Framework**: Flask (you already have Flask experience)
- **Database**: SQLite (for development) or PostgreSQL (for production)
- **ORM**: SQLAlchemy (already in your stack)
- **Authentication**: Flask-Login for session management
- **Password Hashing**: Werkzeug's security utilities (already available)

### Frontend
- **Templates**: Jinja2 (Flask default)
- **CSS Framework**: Bootstrap 5 (you're already using Bootstrap)
- **JavaScript**: Vanilla JS or lightweight framework
- **Charts**: Chart.js or Plotly for visualizations

### Additional Libraries
- `flask-login` - User session management
- `werkzeug` - Password hashing (already installed)
- `chart.js` or `plotly` - For data visualization

## Implementation Phases

### Phase 1: Foundation (MVP)
1. Set up user authentication system
2. Create database models (Users, Medications)
3. Build login/logout functionality
4. Create basic medication CRUD operations
5. Simple list view of medications

### Phase 2: Core Features
1. Add dosage and frequency fields
2. Implement search and filtering
3. Create dashboard with basic statistics
4. Add medication detail view
5. Improve UI/UX

### Phase 3: Enhanced Features
1. Add data visualization (charts)
2. Implement medication scheduling view
3. Add export functionality (CSV/PDF)
4. Advanced filtering and sorting
5. Medication history/audit log

### Phase 4: Multi-Patient Support (Optional)
1. Add Patients table
2. Link medications to patients
3. Patient-specific views
4. Patient medication history

## Security Considerations

1. **Password Security**: Use Werkzeug's password hashing (PBKDF2)
2. **Session Security**: Secure session cookies, CSRF protection
3. **Input Validation**: Validate all user inputs
4. **SQL Injection**: Use SQLAlchemy ORM (parameterized queries)
5. **Access Control**: Role-based access control (RBAC)
6. **HTTPS**: Use HTTPS in production

## Example Medication Frequency Formats

- "3 times daily" → frequency_value: 3, frequency_unit: "per day"
- "Every 8 hours" → frequency_value: 1, frequency_unit: "every 8 hours"
- "Once weekly" → frequency_value: 1, frequency_unit: "per week"
- "As needed" → frequency_type: "as_needed"
- "Twice daily" → frequency_value: 2, frequency_unit: "per day"

## Questions to Consider

1. **Single-user or multi-user?**
   - Will each doctor have their own account with separate data?
   - Or shared system with multiple doctors?

2. **Patient association?**
   - Do you need to track which patient takes which medication?
   - Or just general medication dosage information?

3. **Medication source?**
   - Will doctors manually enter medications?
   - Or import from a database/API?

4. **Dosage tracking over time?**
   - Track historical changes?
   - Or just current dosages?

5. **Notifications/Reminders?**
   - Do you need to send reminders for medication schedules?
   - Or just viewing/analytics?

## Next Steps

1. **Clarify Requirements**: Answer the questions above
2. **Choose Database**: SQLite for MVP, PostgreSQL for production
3. **Set Up Project Structure**: Create new Flask app or modify existing
4. **Implement Authentication**: Start with user login system
5. **Build Core Models**: Create database schema
6. **Create Basic UI**: Start with medication list view
7. **Iterate**: Add features incrementally

## Sample Data Structure Example

```python
# Example medication entry
{
    "name": "Metformin",
    "dosage_amount": "500mg",
    "dosage_count": 2,
    "frequency_type": "daily",
    "frequency_value": 2,
    "frequency_unit": "per day",
    "display": "500mg, 2 times daily"
}
```

---

**Ready to start building?** Let me know which phase you'd like to begin with, or if you'd like me to help clarify any of the requirements above!
