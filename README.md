# Reconciliation Api

A Django project with a REST API using Django REST Framework (DRF) to
handle file uploads and reconciliation processing.

## Getting Started

### Prerequisites

- Python 3.x
- Virtualenv (optional but recommended)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Hudeh/credrails.git
    cd credrails
    ```

2. **Create a virtual environment (optional but recommended):**

    ```bash
    virtualenv venv
    ```

3. **Activate the virtual environment:**

    - **Windows**

        ```bash
        venv\Scripts\activate
        ```

    - **Linux/macOS**

        ```bash
        source venv/bin/activate
        ```

4. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Database Setup

1. **Run migrations to set up the database:**

    ```bash
    python manage.py migrate
    ```

### Running the Server

Start the development server:

```bash
python manage.py runserver
```

### Dashboard Visualization

1. **Set React Project:**

    ```bash
    cd reconciliation-frontend
    ```

2. **Install Required Dependencies:**

    ```bash
    npm install
    ```

3. **Run Your Application:**

    Finally, start your React application

    ```bash
    npm start
    ```
