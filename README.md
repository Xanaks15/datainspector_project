# Data Inspector

This repository contains a lightweight data inspection dashboard built with Django and Django REST Framework. The application
allows you to upload CSV files and visualize key metrics such as missing values, data types distribution, histograms and
duplicate rows without permanently storing analysis results. It is designed to be easily adaptable to new datasets — you
can replace or upload a new CSV at any time and the visualizations will refresh automatically.

## Features

- Upload any CSV dataset via a simple form.
- Compute summary statistics: number of rows, columns, memory usage, total and percentage of missing values and duplicates.
- Visualize missing values by column as a bar chart (only columns with missing values are shown).
- Display the distribution of inferred data types with a pie chart.
- Inspect histograms for any column, with support for numeric, categorical and datetime data.
- View a sample of duplicate rows and the total count of duplicates.
- API-first architecture using Django REST Framework; the frontend uses the Fetch API and Chart.js.
- Stateless analysis: each API call reloads the CSV from disk, so the backend can be restarted or replaced without losing state.
- Self-contained: uses WhiteNoise to serve static files in development or simple deployments.

## Project structure

```
datainspector_project/
├── manage.py              # Django management script
├── datainspector/         # Project configuration (settings, URLs, WSGI)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inspector/             # Application containing the API views and services
│   ├── __init__.py
│   ├── apps.py
│   ├── services.py        # Data profiling logic using pandas
│   ├── urls.py            # API route definitions
│   └── views.py           # REST API views
├── templates/
│   └── index.html         # Dashboard UI
├── static/
│   └── js/
│       └── dashboard.js   # Frontend logic for fetching data and rendering charts
├── requirements.txt       # Python dependencies
└── README.md              # Project overview and setup instructions
```

## Setup instructions

1. **Clone the repository** (or copy these files into a new project directory).

2. **Create and activate a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\Activate.ps1`
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations** (uses SQLite by default):

   ```bash
   python manage.py migrate
   ```

5. **Collect static files** (optional in development):

   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Start the development server**:

   ```bash
   python manage.py runserver
   ```

7. **Open the dashboard** in your browser at http://127.0.0.1:8000/ and upload a CSV file.

## Notes

- Uploaded CSV files are saved in the `datasets/` directory at the project root. The API assigns a unique identifier to
  each upload and reads the file from disk on every request.
- The application does not persist analysis results or dataset metadata in a database; if you delete files from the
  `datasets/` directory, the corresponding dataset IDs will no longer be available.
- The API endpoints are documented implicitly by their URL paths; you can explore them via a REST client (e.g. curl or
  Postman) if needed.

## License

This example project is provided for educational purposes. You are free to modify and use it as a starting point for
your own data inspection tools.