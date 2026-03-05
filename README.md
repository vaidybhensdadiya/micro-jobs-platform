# MicroJobs Platform

A full-stack Web Application for a Micro Job platform where students can apply for small localized tasks posted by providers. Built with Python 3.11, Flask, MySQL, and Vanilla JS / TailwindCSS.

## Features

- **Role-Based Authentication**: Secure login and registration for Students and Providers using JWT (JSON Web Tokens).
- **Dashboard**: Role-specific dashboards outlining recent activity and quick actions.
- **Provider Capabilities**: Post jobs, manage received applications, accept students, mark jobs as completed, and leave reviews.
- **Student Capabilities**: Browse open jobs, submit applications with cover letters, update task status (In Progress, Submitted), and leave reviews.
- **Job Lifecycle**: Strict state transition logic ensuring jobs flow smoothly from `OPEN` to `ASSIGNED` to `IN_PROGRESS` to `SUBMITTED` to `COMPLETED`.
- **Aesthetic UI**: A modern, responsive, and robust frontend leveraging Vanilla JS and Tailwind CSS Glassmorphism aesthetic.
- **Swagger Documentation**: Interactive API testing natively built using Flask-RESTX.

## Tech Stack

- **Backend**: Python 3.11, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-RESTX (Swagger)
- **Database**: MySQL 8.0
- **Frontend**: HTML5, Vanilla JavaScript, Tailwind CSS (via CDN)
- **Deployment**: Docker, Docker Compose

---

## 🚀 Quick Setup & Run (Docker)

The easiest way to run the application is using Docker Compose, which spins up both the MySQL database and the Flask API.

1. **Start the Containers**:
   ```bash
   docker-compose up --build -d
   ```
   *Note: On the first run, MySQL might take a few seconds to fully initialize.*

2. **Run Database Migrations**:
   Once the containers are running, open a bash shell in the `app` container to set up the database schema:
   ```bash
   docker-compose exec app flask db init
   docker-compose exec app flask db migrate -m "Initial migration"
   docker-compose exec app flask db upgrade
   ```

3. **Access the Application**:
   - **Frontend UI**: Simply open `frontend/index.html` in your web browser. Everything communicates via the local REST API.
   - **Backend API Docs (Swagger)**: `http://localhost:5000/api/docs`

---

## Example User Flow

1. **Create Provider**: Open `frontend/register.html` and register as a "Provider". 
2. **Post Job**: Click "Post a Job" and complete the form.
3. **Create Student**: Open an incognito window or log out, register as a "Student".
4. **Apply**: Browse to the job you just posted and click "Apply Now".
5. **Accept**: Back on the Provider account, click "Manage Job" and Accept the application. 
6. **Complete Task**: Cycle the task status by having the student mark it "In-Progress" and "Submitted", and the provider mark it "Completed".
7. **Review**: Both parties can now leave a review.

---

## Environment Variables

These are handled automatically in `docker-compose.yml`, but for local non-Docker development, ensure you export:
- `FLASK_APP=backend.app:create_app`
- `FLASK_ENV=development`
- `DATABASE_URL=mysql+pymysql://micro_user:micro_pass@localhost:3306/micro_jobs`
- `JWT_SECRET_KEY=super-secret-key`

*(Ensure you have a MySQL server running matching these credentials if developing externally).*
