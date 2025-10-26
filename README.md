# Reddit Post Sorter

A Python Flask application that uses the PRAW (Python Reddit API Wrapper) to retrieve your saved Reddit posts and allows you to organize them into custom categories. All data is stored locally using SQLite.

## Features

- 🔄 **Fetch Saved Posts**: Retrieve your saved Reddit posts using PRAW API
- 🏷️ **Custom Categories**: Create and manage custom categories with colors
- 📊 **Local Database**: All data stored locally in SQLite (no cloud connection required)
- 🔍 **Search & Filter**: Search posts by title and filter by category
- 🎨 **Modern UI**: Clean, responsive Bootstrap interface
- 📱 **Mobile Friendly**: Works great on desktop and mobile devices

## Setup Instructions

### 1. Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

**Activate the virtual environment:**

Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

Windows Command Prompt:
```cmd
venv\Scripts\activate.bat
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Reddit API

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Note down your `client_id` and `client_secret`

### 4. Set Environment Variables

1. Copy `env_example.txt` to `.env` (Windows PowerShell command):
   ```powershell
   Copy-Item "env_example.txt" ".env"
   ```
   Or in Windows Command Prompt:
   ```cmd
   copy env_example.txt .env
   ```
2. Edit the `.env` file and fill in your Reddit API credentials:

```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=RedditSorter/1.0 by YourUsername
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
SECRET_KEY=your-secret-key-here-change-this-in-production
```

**Important**: 
- Replace `YourUsername` in `REDDIT_USER_AGENT` with your actual Reddit username
- Use a strong, random `SECRET_KEY` for production

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### First Time Setup

1. **Configure Reddit API**: Make sure your `.env` file is properly configured
2. **Fetch Posts**: Click "Fetch Saved Posts" to retrieve your saved Reddit posts
3. **Create Categories**: Go to Categories page and create custom categories
4. **Organize**: Assign posts to categories using the dropdown in each post

### Managing Categories

- **Create**: Use the "Create Category" button to add new categories
- **Edit**: Click the dropdown menu on any category to edit its name or color
- **Delete**: Delete categories (posts will be moved to "Uncategorized")
- **View Posts**: Click "View Posts" to see all posts in a specific category

### Organizing Posts

- **Assign Categories**: Use the "Category" dropdown on each post
- **Search**: Use the search box to find posts by title
- **Filter**: Filter posts by category using the sidebar

## Database Schema

The application uses SQLite with two main tables:

### Categories
- `id`: Primary key
- `name`: Category name (unique)
- `color`: Hex color code for the category
- `created_at`: Timestamp when category was created

### Reddit Posts
- `id`: Primary key
- `reddit_id`: Reddit post ID (unique)
- `title`: Post title
- `author`: Post author
- `subreddit`: Subreddit name
- `url`: Post URL
- `selftext`: Self-post text content
- `score`: Post score (upvotes - downvotes)
- `num_comments`: Number of comments
- `created_utc`: When the post was created on Reddit
- `saved_at`: When the post was saved locally
- `category_id`: Foreign key to categories table
- `permalink`: Reddit permalink
- `is_self`: Whether it's a self-post
- `thumbnail`: Thumbnail URL
- `preview_url`: Preview image URL

## API Endpoints

- `GET /`: Home page with recent posts
- `GET /fetch_saved_posts`: Fetch new saved posts from Reddit
- `GET /posts`: View all posts with filtering
- `GET /categories`: Manage categories
- `POST /create_category`: Create a new category
- `POST /update_category/<id>`: Update a category
- `GET /delete_category/<id>`: Delete a category
- `POST /assign_category/<post_id>`: Assign a post to a category
- `GET /api/posts`: JSON API for posts

## Security Notes

- Store your `.env` file securely and never commit it to version control
- Use a strong `SECRET_KEY` for production deployments
- Your Reddit credentials are only used for API access and stored locally

## Troubleshooting

### Common Issues

1. **"Error fetching saved posts"**
   - Check your Reddit API credentials in `.env`
   - Ensure your Reddit account has saved posts
   - Verify your Reddit app is configured as a "script" type

2. **Database errors**
   - Delete `reddit_sorter.db` to reset the database
   - Restart the application

3. **Permission errors**
   - Ensure the application has write permissions in the project directory
   - Check that SQLite can create the database file

### Getting Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - **Name**: Any name (e.g., "My Reddit Sorter")
   - **App type**: Select "script"
   - **Description**: Optional
   - **About URL**: Optional
   - **Redirect URI**: `http://localhost:8080` (required but not used)
4. Click "Create app"
5. Note the **client ID** (under the app name) and **secret** (in the app details)

## QA Testing & Bug Fixes

During quality assurance testing, the following issues were identified and resolved:

### Issue #1: Missing `.env` Configuration File
**Found By:** QA Testing  
**Description:** Application failed to start with error "Required configuration setting 'client_id' missing"  
**Root Cause:** The `.env` file was not created from the example template, and setup instructions were unclear about the Windows command needed  
**Resolution:**
- Created proper `.env` file with correct formatting (removed extra spaces after `=` signs)
- Updated `REDDIT_USER_AGENT` to include actual username
- Enhanced README.md Section 3 to include explicit Windows terminal commands:
  - PowerShell: `Copy-Item "env_example.txt" ".env"`
  - Command Prompt: `copy env_example.txt .env`

### Issue #2: Category Dropdown Menu Appearing Behind Post Cards
**Found By:** QA Testing  
**Description:** When clicking the category dropdown on a post card, the menu appeared behind adjacent post cards instead of on top  
**Root Cause:** CSS z-index stacking context not properly configured for dropdown menus  
**Resolution:**
- Added `position: relative` and proper `z-index` values to `.post-card`
- Set `.post-card .dropdown { position: static; }`
- Set `.post-card .dropdown-menu { z-index: 1050; }` to ensure dropdowns appear above all content
- Cards now properly elevate on hover with `z-index: 2`

### Issue #3: Color Scheme Not Modern
**Found By:** QA Testing  
**Description:** Initial color scheme was too generic and heavily Reddit-branded  
**Root Cause:** Default Bootstrap colors with heavy Reddit orange usage  
**Resolution:**
- Implemented modern design system with CSS variables
- Primary color: Indigo/Purple gradient (#6366f1 to #4f46e5) - professional and modern
- Accent color: Soft orange (#ff6b35) - subtle Reddit nod without copyright concerns
- Added Inter font family for clean, professional typography
- Implemented gradient backgrounds, smooth transitions, and modern shadows
- Enhanced all interactive elements with smooth animations

### Issue #4: Post Card Titles Overlapping
**Found By:** QA Testing  
**Description:** Long post titles were overlapping with other card content  
**Root Cause:** Insufficient spacing and lack of word-wrapping rules  
**Resolution:**
- Added proper padding to card bodies (1.5rem)
- Implemented `word-wrap: break-word` and `overflow-wrap: break-word` for titles
- Added proper line-height values (1.4 for titles, 1.6 for body text)
- Set `gap: 1rem` between flex columns
- Added consistent margin-bottom spacing between card elements

### Issue #5: Uncategorized Posts Page Not Working
**Found By:** QA Testing  
**Description:** Clicking on the "Uncategorized" category link showed no posts, even when uncategorized posts existed  
**Root Cause:** The `/posts` route only handled posts WITH a category_id, not posts where category_id is NULL  
**Resolution:**
- Added `uncategorized` parameter support to the `/posts` route
- Implemented filter for `category_id=None` when `uncategorized=true`
- Added "Uncategorized" link to sidebar with dynamic count
- Updated posts.html to display appropriate feedback message ("that are uncategorized")
- Posts without categories now properly display when filtering by Uncategorized

### Issue #6: Hide Categorized Toggle State Not Persisting
**Found By:** QA Testing  
**Description:** After assigning a post to a category (which triggers a page refresh), the "Hide Categorized Posts" toggle would reset to unchecked, forcing users to re-enable it every time  
**Root Cause:** Toggle state was only stored in DOM, not persisted across page reloads  
**Resolution:**
- Implemented browser localStorage to save toggle state
- Added `localStorage.setItem('hideCategorizedPosts', isHidden)` when toggle changes
- Added `localStorage.getItem('hideCategorizedPosts')` on page load to restore state
- Automatically reapplies filter if toggle was previously checked
- State persists across page refreshes, navigation, and category assignments
- Works seamlessly on both Home and All Posts pages

### Testing Metrics
- **Total Issues Found:** 6
- **Critical Issues:** 2 (Configuration, Uncategorized Filter)
- **UI/UX Issues:** 4 (Dropdown Z-index, Color Scheme, Title Overlap, Toggle State)
- **Resolution Rate:** 100%
- **All Issues Resolved:** ✓

## License

This project is open source and available under the MIT License.
