# Event Registration System
### CodeAlpha Backend Development Internship — Task 2

A backend system for managing events and attendee registrations, built using **Python**, **Django**, and **Django REST Framework (DRF)**.

The system handles event creation, capacity limits, real-time seat availability, unique ticket generation, duplicate registration prevention, and cancellation workflows. It includes both RESTful API endpoints and a web interface for demonstrations.

---

## Features

- **Event Management**: Create, list, search, and filter events by category (Tech, Workshops, Seminars, Hackathons).
- **Seat Availability Tracking**: Tracks capacity dynamically (`registered_count` and `available_seats`). Prevents overbooking once an event reaches its limit.
- **Registration & Ticket Generation**: Generates unique ticket codes (e.g., `EVT-4A7B2C1D`) for attendees.
- **Duplicate Prevention**: Prevents duplicate active registrations for the same event using the same email address.
- **Cancellation & Seat Release**: Allows attendees to cancel their booking, which automatically frees up the seat for other users.
- **Admin Panel**: Django Admin dashboard for organizers to manage events, view attendees, and update booking statuses.
- **REST API & Interactive Docs**: Fully documented REST endpoints accessible at `/docs/`.

---

## Tech Stack

- **Backend**: Python 3.12, Django 6.1
- **API Framework**: Django REST Framework (DRF)
- **Database**: SQLite (default for development)
- **Frontend**: HTML5, Bootstrap 5, Custom CSS

---

## Database Architecture

- **Event**:
  - `title`, `description`, `category`, `location`, `date`, `capacity`, `organizer`, `image_url`, `is_active`
- **Registration**:
  - `event` (ForeignKey), `user` (ForeignKey, optional), `full_name`, `email`, `phone`, `notes`, `status` (CONFIRMED / CANCELLED), `ticket_code`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/events/` | List all active events (supports `?search=` and `?category=`) |
| `GET` | `/api/events/<id>/` | Retrieve event details and seat count |
| `POST` | `/api/events/` | Create a new event (Authenticated) |
| `POST` | `/api/events/<id>/register/` | Register for an event |
| `GET` | `/api/my-registrations/` | View registrations by logged-in user or `?email=` |
| `POST` | `/api/registrations/<id>/cancel/` | Cancel a registration and free up the seat |
| `GET` | `/api/events/<id>/attendees/` | View attendee list (Organizer/Staff only) |
| `POST` | `/api/auth/register/` | User registration |
| `POST` | `/api/auth/login/` | User login session |
| `POST` | `/api/auth/logout/` | User logout |

---

## How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/xosmanova/CodeAlpha_EventRegistrationSystem.git
cd CodeAlpha_EventRegistrationSystem
```

### 2. Activate virtual environment
- **Windows:**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install requirements
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Seed sample data
Populates test events, superuser, and sample attendees:
```bash
python manage.py seed_data
```

### 6. Start development server
```bash
python manage.py runserver
```

Open your browser at:
- Web App: `http://127.0.0.1:8000/`
- API Documentation: `http://127.0.0.1:8000/docs/`
- Admin Panel: `http://127.0.0.1:8000/admin/`

---

## Default Credentials

- **Admin Account**: `admin` / `admin123`
- **Test User**: `john_doe` / `password123`

---

## Automated Tests

Run the test suite (10 test cases covering APIs, model constraints, and edge cases):
```bash
python manage.py test
```

---

## Author
Developed by **xosmanova** for the **CodeAlpha Backend Development Internship Program**.
