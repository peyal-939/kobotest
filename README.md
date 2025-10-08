# KoboToolbox Django Integration

A Django REST Framework project for collecting survey responses directly in your app using KoboToolbox forms, with automatic sync and beautiful web interface.

## Features

- **📝 Embed Kobo Forms** – Users submit surveys directly from your app (no redirect to KoboToolbox website)
- **🔄 Automatic Sync** – Submissions are automatically synced to your MySQL database
- **📊 View Submissions** – Beautiful web interface to browse all responses
- **🔍 Search & Filter** – Find specific submissions quickly
- **📱 Mobile Responsive** – Works perfectly on all devices
- **🎯 One-Click Sync** – Manual refresh button for instant updates
- **🛠️ REST API** – Full DRF API for programmatic access
- **⚡ Real-time Webhook** – Optional webhook for instant notifications

## Prerequisites

- Python 3.13 (matches the existing `.venv`)
- MySQL 8.x server (or compatible MariaDB) with a database/user ready
- KoboToolbox account with API token ([Get yours here](https://kf.kobotoolbox.org/token/))
- A published Kobo form with shareable link
- An activated virtual environment (already provided at `.venv/`)

## Quick start

1. **Create your environment file**
   ```powershell
   Copy-Item .\.env.example .\.env
   ```
   Edit `.env` to set:
   - MySQL credentials (`MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, etc.)
   - KoboToolbox API token (`KOBO_TOKEN`)
   - Your form UID (`KOBO_FORM_UID` - e.g., `dxT6aOXp`)
   - Your form embed URL (`KOBO_FORM_URL` - e.g., `https://ee.kobotoolbox.org/x/dxT6aOXp`)
   - Django secret key (`DJANGO_SECRET_KEY`)

2. **Install dependencies**
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. **Apply migrations**
   ```powershell
   .\.venv\Scripts\python.exe manage.py migrate
   ```

4. **Create admin user (optional)**
   ```powershell
   .\.venv\Scripts\python.exe manage.py createsuperuser
   ```

5. **Run the development server**
   ```powershell
   .\.venv\Scripts\python.exe manage.py runserver
   ```

6. **Open your browser**
   - Visit: **http://localhost:8000/**
   - Click "Submit a Survey" to fill out the form
   - Click "View Submissions" to see all responses

## 🎯 How It Works

### The Complete Flow:

1. **User visits your app** → Goes to http://localhost:8000/
2. **Clicks "Submit a Survey"** → Kobo form is embedded in your page (iframe)
3. **User fills out and submits** → Data goes to KoboToolbox servers
4. **Automatic sync** → Click "Sync Now" button or happens automatically when viewing submissions
5. **View in your app** → All responses appear in "View Submissions" page
6. **Click any submission** → See detailed breakdown of all answers

**Key Advantage:** Users never leave your app! They submit via the embedded Kobo form, and view results in your custom interface.

## 📚 Web Interface Pages

### Home Page (`/`)
- Overview of the system
- Quick navigation to Submit Survey and View Submissions

### Submit Survey (`/submit/`)
- **Embedded Kobo Form** – Your form loads directly in the page
- Users fill out and submit without leaving your app
- Responsive iframe that works on mobile and desktop

### View Submissions (`/submissions/`)
- **All Responses** – Card-based layout showing all submissions
- **Search Box** – Filter by form UID or submission content
- **Sync Now Button** – Manually refresh data from KoboToolbox
- **Auto-Sync** – Automatically syncs on page load
- **Preview Data** – See first few fields of each response
- **Click to Detail** – View full submission details

### Submission Detail (`/submissions/<id>/`)
- **Full Response Data** – All form answers displayed
- **Metadata** – Submission date, sync date, form UID
- **Raw JSON** – Expandable view of the complete data structure

## 🔌 API Endpoints

All API endpoints are available at:

| Method | Path                       | Description                              |
| ------ | -------------------------- | ---------------------------------------- |
| GET    | `/health/`                 | Health check returning status            |
| GET    | `/meta/`                   | Basic project metadata payload           |
| POST   | `/kobo/webhook/`           | Webhook for real-time Kobo submissions   |
| GET    | `/api/submissions/`        | List all synced submissions (paginated)  |
| GET    | `/api/submissions/<id>/`   | Retrieve a specific submission by ID     |
| GET    | `/admin/`                  | Django admin interface                   |

**Query Parameters for `/api/submissions/`:**
- `?form_uid=dxT6aOXp` – Filter by form UID
- `?search=keyword` – Search in submission data
- `?ordering=-date_submitted` – Sort by date (newest first)

## 🛠️ Manual Sync Commands

Fetch all submissions from a specific form:
```powershell
.\.venv\Scripts\python.exe manage.py fetch_kobo_data <form_uid>
```

Or set `KOBO_FORM_UID` in `.env` and run:
```powershell
.\.venv\Scripts\python.exe manage.py fetch_kobo_data
```

**Options:**
- `--limit 100` – Fetch only the first 100 submissions
- `--force-update` – Update existing submissions even if already synced

## ⚡ Real-time Webhook Setup (Optional)

For instant submission sync without manual refresh:

1. Deploy your app to a public URL (or use [ngrok](https://ngrok.com/) for testing)
2. Go to your Kobo project → **Settings** → **REST Services**
3. Add a new REST endpoint:
   - **URL:** `https://yourdomain.com/kobo/webhook/`
   - **Method:** `POST`
4. Save and test — new submissions will sync automatically

## Configuration

Configuration is managed through environment variables loaded from `.env` (ignored by Git). Start from `.env.example` and adjust as needed.

### Core Django variables

- `DJANGO_SECRET_KEY` – set to a strong, unique value for production.
- `DJANGO_DEBUG` – set to `0`, `false`, or `off` to disable debug mode.
- `DJANGO_ALLOWED_HOSTS` – comma-separated hostnames (default `localhost,127.0.0.1`).

### Database variables (MySQL)

- `MYSQL_DATABASE` – database schema name (default: `aps`).
- `MYSQL_USER` / `MYSQL_PASSWORD` – credentials for the database user.
- `MYSQL_HOST` / `MYSQL_PORT` – MySQL host and port (defaults `localhost:3306`).

### KoboToolbox variables

- `KOBO_TOKEN` – Your KoboToolbox API token (required).
- `KOBO_BASE_URL` – Kobo server URL (default: `https://kf.kobotoolbox.org`).
- `KOBO_FORM_UID` – Your form UID for the sync command (e.g., `dxT6aOXp`).
- `KOBO_FORM_URL` – Shareable form link for embedding (e.g., `https://ee.kobotoolbox.org/x/dxT6aOXp`).

## 📁 Project Structure

```
├── manage.py
├── requirements.txt
├── .env.example
├── config/
│   ├── settings.py         # MySQL config, REST framework
│   ├── urls.py
│   └── wsgi.py
└── api/
    ├── models.py           # KoboSubmission model
    ├── views.py            # API + Web views
    ├── urls.py
    ├── serializers.py
    ├── admin.py            # Django admin interface
    ├── tests.py            # Test suite (9 tests)
    ├── templates/api/      # Bootstrap templates
    │   ├── base.html
    │   ├── home.html
    │   ├── submit_survey.html
    │   ├── view_submissions.html
    │   └── submission_detail.html
    ├── services/
    │   └── kobo_client.py  # KoboToolbox API client
    └── management/commands/
        └── fetch_kobo_data.py
```

## 🧪 Testing

Run the test suite:
```powershell
.\.venv\Scripts\python.exe manage.py test
```

All 9 tests should pass:
- Health check endpoint
- Metadata endpoint
- Webhook create/update/validation
- Model functionality
- API list/detail/filtering

## 🔒 Security Notes

- Never commit `.env` file to version control
- Use strong `DJANGO_SECRET_KEY` in production
- Set `DJANGO_DEBUG=False` in production
- Configure `DJANGO_ALLOWED_HOSTS` for your domain
- Use HTTPS for webhook endpoints in production
- Restrict MySQL user permissions to only what's needed

## 📝 Environment Variables Reference

See `.env.example` for all required variables:

- **Django Settings:** `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
- **MySQL Config:** `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`
- **Kobo Integration:** `KOBO_TOKEN`, `KOBO_BASE_URL`, `KOBO_FORM_UID`, `KOBO_FORM_URL`

## 🚀 Next Steps

1. ✅ **Test the Web Interface**
   - Visit http://localhost:8000/
   - Submit a test survey via the embedded form
   - Click "Sync Now" and view submissions

2. **Customize the Design**
   - Edit templates in `api/templates/api/`
   - Modify Bootstrap classes or add custom CSS

3. **Set Up Webhook** (Optional)
   - Deploy to production or use ngrok
   - Configure REST Services in KoboToolbox

4. **Add Authentication**
   - Protect submission views with login
   - Use Django's built-in auth or DRF TokenAuth

5. **Schedule Automatic Sync**
   - Use Windows Task Scheduler or Celery
   - Run `fetch_kobo_data` command periodically

## 📖 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [KoboToolbox API Docs](https://support.kobotoolbox.org/api.html)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)

## 🐛 Troubleshooting

**Form not displaying in iframe?**
- Check that `KOBO_FORM_URL` in `.env` points to the shareable link (not the edit link)
- Ensure your form is deployed in KoboToolbox

**Sync button not working?**
- Verify `KOBO_TOKEN` and `KOBO_FORM_UID` in `.env`
- Check Django logs for API errors
- Test the management command: `python manage.py fetch_kobo_data`

**MySQL connection error?**
- Confirm MySQL server is running
- Check credentials in `.env`
- Ensure database exists and user has proper permissions

---

**Built with Django 5.2.7 + DRF 3.16.1 + Bootstrap 5.3.0**
