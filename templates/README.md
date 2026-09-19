# Xtreme Car Parking Management System

A lightweight, modern web application built with **Python**, **Flask**, **SQLite**, and **Tailwind CSS** for managing parking lot allocations, driver registrations, duration based fee calculations, and receipt generation.

---

## Key Features

* **Realtime Parking Space Grid**: Visual indicators showing available vs. occupied parking slots (10 slots default).
* **Driver & Vehicle Registration**: Captures driver details, phone numbers, license plates, and vehicle models.
* **Flexible Slot Allocation**: Allows drivers to choose an open slot or auto-assigns the next available one.
* **Automated Duration & Fee Billing**:
  * **1 – 30 Minutes**: Ksh. 200
  * **31 – 60 Minutes**: Ksh. 300
  * **Above 1 Hour**: Ksh. 300 per hour (or fraction thereof)
* **Digital Receipt Generation**: Displays formatted start time, end time, calculated duration, and total amount in Kenya Shillings (Ksh.).

---

## Tech Stack

* **Backend**: Python 3, Flask
* **Database**: SQLite (local embedded database)
* **Frontend**: HTML5, Tailwind CSS (via CDN), Jinja2 Templating

---

## Project Structure

```text
Xtreme Parking Lot/
│
├── app.py              # Main Flask server and application routes
├── parking.db          # Local SQLite database (created automatically)
└── templates/          # HTML templates rendered by Flask
    ├── index.html      # Main dashboard with occupancy grid
    ├── register.html   # Vehicle registration form
    └── receipt.html    # Formatted billing receipt