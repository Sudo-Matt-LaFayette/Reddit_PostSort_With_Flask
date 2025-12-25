# Quick Start Guide - Medication Tracking App

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   python3 medication_app.py
   ```

3. **Access the app:**
   - Open your browser to: `http://localhost:5001`
   - **Developer login**: `developer` / `dev123` (recommended for development)
   - **Admin login**: `admin` / `admin123`

## First Steps

1. **Login** with the default admin credentials
2. **Register a new account** (optional) at `/register`
3. **Add your first medication** by clicking "Add Medication"
4. **View your dashboard** to see statistics and recent medications

## Key Features

✅ **User Authentication** - Secure login/registration  
✅ **Medication CRUD** - Create, read, update, delete medications  
✅ **Dashboard** - Statistics and overview  
✅ **Search & Filter** - Find medications easily  
✅ **Frequency Tracking** - Track dosage count and frequency  

## Example Medication Entry

- **Name**: Metformin
- **Dosage Amount**: 500mg
- **Number of Dosages**: 2
- **Frequency Type**: Daily
- **Frequency Value**: 2
- **Frequency Unit**: Per Day
- **Result**: "500mg, 2 times daily"

## Database

The database (`medication_tracker.db`) is automatically created on first run. All data is stored locally.

## Troubleshooting

- **Port already in use**: Change port in `medication_app.py` (line 285)
- **Import errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`
- **Database errors**: Delete `medication_tracker.db` to reset

## Next Steps

- Add more medications
- Explore the dashboard statistics
- Use search and filters to organize medications
- Edit or delete medications as needed

For more details, see `MEDICATION_APP_README.md`
