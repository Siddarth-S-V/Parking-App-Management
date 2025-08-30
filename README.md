# 🚗 Vehicle Parking Management System

![Project Status](https://img.shields.io/badge/status-complete-green)
![Language](https://img.shields.io/badge/Python-3.8%2B-blue)
![Framework](https://img.shields.io/badge/Framework-Flask-orange)
![Database](https://img.shields.io/badge/Database-SQLite-lightgrey)

A full-stack web application built with Flask and SQLAlchemy that provides a complete solution for managing vehicle parking. The system caters to both regular users looking for parking spots and administrators managing the parking facilities.

---

## 📸 Screenshots

*(It's highly recommended to replace these placeholders with actual screenshots of your application)*

| User Dashboard | Find Parking | Admin Dashboard |
| :---: | :---: | :---: |
| ![User Dashboard](https://via.placeholder.com/300x200.png?text=User+Dashboard) | ![Find Parking](https://via.placeholder.com/300x200.png?text=Find+Parking+Page) | ![Admin Dashboard](https://via.placeholder.com/300x200.png?text=Admin+Dashboard) |

---

## ✨ Core Features

This application is divided into two main roles: **User** and **Admin**.

### 👤 User Features
* **Authentication**: Secure user registration and login functionality.
* **Dashboard**: A personalized dashboard displaying statistics like total registered vehicles and booking history.
* **Vehicle Management**: Users can register their vehicles (2-wheelers or 4-wheelers) before making a booking.
* **Find Parking**: Search for available parking lots using a pincode.
* **Real-time Availability**: View the number of available spots and the utilization percentage for each parking lot.
* **Booking System**: Book a parking spot by selecting a vehicle and specifying an entry and exit time.
* **Booking Confirmation**: Receive a detailed confirmation upon successful booking, including cost and duration.
* **My Bookings**: View a list of all active and past bookings.
* **Release Spot**: Manually "release" a spot after leaving, which marks the booking as complete and the spot as available.

### 🔒 Admin Features
* **Secure Admin Panel**: Separate dashboard and functionalities accessible only to administrators.
* **System-wide Statistics**: Admin dashboard with key metrics like total users, total parking lots, total revenue, and active bookings.
* **Parking Lot Management (CRUD)**:
    * **Create**: Add new parking lots with details like name, address, pincode, price per hour, and capacity.
    * **Read**: View all existing parking lots and their current utilization.
    * **Update**: Edit the details of any parking lot.
    * **Delete**: Remove parking lots (only if there are no active bookings).
* **Automatic Spot Creation**: Parking spots are automatically generated and numbered (e.g., P001, P002) based on the capacity provided when a new lot is created.
* **User Management**: View a list of all registered (non-admin) users.
* **Booking Oversight**: Monitor all bookings made across the entire system.

---

## 🛠️ Tech Stack & Architecture

* **Backend**: Flask (a lightweight WSGI web application framework in Python).
* **Database**: SQLite (via Flask-SQLAlchemy for ORM).
* **Frontend**: Jinja2 Templating, Bootstrap 5, Font Awesome.
* **Authentication**: Session-based authentication with password hashing (Werkzeug security).

---

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites
* Python 3.8+
* `pip` (Python package installer)

### Installation & Setup

1.  **Clone the repository**
    ```sh
    git clone [https://github.com/](https://github.com/)[YOUR_USERNAME]/[YOUR_REPOSITORY_NAME].git
    cd [YOUR_REPOSITORY_NAME]
    ```

2.  **Create and activate a virtual environment** (Recommended)
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages**
    ```sh
    pip install Flask Flask-SQLAlchemy Werkzeug
    ```
    *(You can also generate a `requirements.txt` file using `pip freeze > requirements.txt` and install from it using `pip install -r requirements.txt`)*

4.  **Run the application**
    ```sh
    python app.py
    ```
    The application will start on `http://127.0.0.1:5000`. The database file (`parking.db`) will be automatically created in a `database` folder.

5.  **Access the application**
    * Open your web browser and navigate to `http://127.0.0.1:5000`.
    * You can register as a new user or use the default admin credentials to log in.

---

## 🔑 Default Admin Credentials

A default administrator account is created automatically the first time you run the application.

* **Username**: `admin`
* **Password**: `Admin@123`

---

## 🗃️ Database Schema

The application uses five main database models defined in `app.py`:

* **User**: Stores user information, including credentials and admin status.
* **Vehicle**: Stores details of vehicles registered by users.
* **ParkingLot**: Stores information about each parking facility, including its capacity and price.
* **ParkingSpot**: Represents an individual spot within a `ParkingLot`.
* **Booking**: Contains details of each reservation, linking a `User`, `Vehicle`, and `ParkingSpot`.

---

## 💡 Future Enhancements

This project has a solid foundation that can be extended with more advanced features:
* **Payment Gateway Integration**: Integrate Stripe or Razorpay to handle payments for bookings.
* **Real-time Updates**: Use WebSockets (e.g., Flask-SocketIO) to update spot availability in real-time without needing a page refresh.
* **API Development**: Create a RESTful API to allow a mobile application to interact with the backend.
* **Advanced Reporting**: Generate PDF reports for admin analytics on revenue and occupancy.
* **Password Reset**: Implement a "Forgot Password" feature using email verification.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
