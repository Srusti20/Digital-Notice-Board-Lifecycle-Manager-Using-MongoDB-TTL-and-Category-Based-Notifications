# Smart Notice Board System

A web-based Notice Management System that allows administrators to post notices and students to view them in real-time. The system supports category-based filtering, expiry management, and dynamic updates.

---

## Features

- Admin can post notices with title, content, category, department, and year
- Expiry date and time for automatic notice removal
- Real-time notice display on dashboard
- Category-based organization (Exams, Events, Placements, General)
- Department and Year targeting
- Delete notices functionality for admin
- Auto-refresh of notices
- Frontend validation to prevent past expiry dates
- REST API integration with backend

---

## Advantages

- Reduces manual effort in managing notice boards
- Eliminates outdated notices automatically
- Improves communication efficiency in institutions
- User-friendly and responsive interface
- Centralized system accessible from anywhere
- Scalable for large institutions

---

## Future Enhancements (Scope)

- Real-time notifications using WebSockets or Firebase
- Email and SMS alerts for important notices
- User authentication for Admin and Students
- Mobile application support
- Analytics dashboard for tracking notice engagement
- AI-based priority notice highlighting
- Multi-language support

---

## Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- FastAPI (Python)

### Database
- MongoDB

---
## Results
# Home Page (User View)

Displays all active notices for students in a clean and structured format.
<img width="901" height="469" alt="image" src="https://github.com/user-attachments/assets/6d1dd9ab-9982-4ab3-b287-f109400315f7" />


# Admin Dashboard (Post Notice)

Allows the admin to create and publish notices with category, department, year, and expiry time.
<img width="477" height="555" alt="image" src="https://github.com/user-attachments/assets/cc23167c-e17d-4e0d-a711-fada13c320dd" />


# Database Storage (MongoDB)

Confirms that notice data is correctly stored with all required fields in MongoDB.
<img width="518" height="427" alt="image" src="https://github.com/user-attachments/assets/01c81702-8099-45a1-a22b-57c03bad6f0e" />


# Email Notification

Demonstrates that email notifications are successfully sent to registered students.
<img width="696" height="643" alt="image" src="https://github.com/user-attachments/assets/9c03c1e4-9c15-4c5d-97f0-607ebbfded11" />

# Automatic Expiry (TTL Feature)

Shows that expired notices are automatically removed from the system using MongoDB TTL.
<img width="403" height="220" alt="image" src="https://github.com/user-attachments/assets/fe0df492-0d01-4cf9-a5b6-72c88f92ad10" />

-----

## How to Run the Project

Follow the steps below to run the project on your local machine.

# Step 1: Run Backend (FastAPI)

Open terminal and navigate to the backend folder:

cd backend

# Install required dependencies (if not installed):

pip install -r requirements.txt

# Start the backend server:

python -m uvicorn main:app --reload

# Backend will be available at:
http://127.0.0.1:8000

## Step 2: Run Frontend

# Open a new terminal and navigate to the frontend folder:

cd frontend

# Start the frontend server:

python -m http.server 5500

# Open your browser and go to:

http://localhost:5500

------

## Important Notes

-Make sure the backend server is running before opening the frontend.

-Ensure MongoDB is running and connected properly.

-Check API URLs in frontend (should point to http://127.0.0.1:8000).
