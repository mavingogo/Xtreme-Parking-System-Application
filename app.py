import math
import sqlite3
from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DB_NAME = "parking.db"
HOURLY_RATE = 5.0


def get_db():
  return sqlite3.connect(DB_NAME)


def init_db():
  with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS slots (
                slot_id INTEGER PRIMARY KEY,
                is_occupied INTEGER DEFAULT 0
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_name TEXT,
                phone TEXT,
                license_plate TEXT,
                vehicle_model TEXT,
                slot_id INTEGER,
                entry_time TEXT,
                exit_time TEXT,
                total_fee REAL
            )
        """)
    cursor.execute("SELECT COUNT(*) FROM slots")
    if cursor.fetchone()[0] == 0:
      cursor.executemany(
          "INSERT INTO slots (slot_id) VALUES (?)", [(i,) for i in range(1, 11)]
      )
    conn.commit()


@app.route("/")
def home():
  with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("""
            SELECT s.slot_id, s.is_occupied, se.driver_name, se.license_plate, se.vehicle_model, se.entry_time
            FROM slots s
            LEFT JOIN sessions se ON s.slot_id = se.slot_id AND se.exit_time IS NULL
        """)
    slots = cursor.fetchall()
  return render_template("index.html", slots=slots)


@app.route("/register", methods=["GET", "POST"])
def register():
  with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT slot_id FROM slots WHERE is_occupied = 0")
    available_slots = [row[0] for row in cursor.fetchall()]

    if request.method == "POST":
      driver_name = request.form["driver_name"]
      phone = request.form["phone"]
      license_plate = request.form["license_plate"]
      vehicle_model = request.form["vehicle_model"]
      slot_choice = request.form.get("slot_id")

      if not available_slots:
        return "Parking Lot is Full!", 400

      selected_slot = (
          int(slot_choice)
          if slot_choice and int(slot_choice) in available_slots
          else available_slots[0]
      )
      entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      cursor.execute(
          "UPDATE slots SET is_occupied = 1 WHERE slot_id = ?",
          (selected_slot,),
      )
      cursor.execute(
          """
                INSERT INTO sessions (driver_name, phone, license_plate, vehicle_model, slot_id, entry_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
          (
              driver_name,
              phone,
              license_plate,
              vehicle_model,
              selected_slot,
              entry_time,
          ),
      )
      conn.commit()
      return redirect(url_for("home"))

  return render_template("register.html", available_slots=available_slots)


# @app.route("/checkout", methods=["POST"])
# def checkout():
#   plate = request.form["license_plate"]

#   with get_db() as conn:
#     cursor = conn.cursor()
#     cursor.execute(
#         """
#             SELECT session_id, slot_id, entry_time, driver_name, vehicle_model 
#             FROM sessions WHERE license_plate = ? AND exit_time IS NULL
#         """,
#         (plate,),
#     )
#     session = cursor.fetchone()

#     if not session:
#       return "No active session found for this license plate.", 404

#     session_id, slot_id, entry_str, driver_name, vehicle_model = session
#     entry_time = datetime.strptime(entry_str, "%Y-%m-%d %H:%M:%S")
#     exit_time = datetime.now()

#     duration_seconds = (exit_time - entry_time).total_seconds()
#     hours_parked = max(1, math.ceil(duration_seconds / 3600))
#     total_fee = hours_parked * HOURLY_RATE
#     exit_str = exit_time.strftime("%Y-%m-%d %H:%M:%S")

#     cursor.execute(
#         "UPDATE slots SET is_occupied = 0 WHERE slot_id = ?", (slot_id,)
#     )
#     cursor.execute(
#         """
#             UPDATE sessions 
#             SET exit_time = ?, total_fee = ? 
#             WHERE session_id = ?
#         """,
#         (exit_str, total_fee, session_id),
#     )
#     conn.commit()

#   receipt = {
#       "driver_name": driver_name,
#       "vehicle_model": vehicle_model,
#       "license_plate": plate,
#       "slot_id": slot_id,
#       "entry_time": entry_str,
#       "exit_time": exit_str,
#       "hours": hours_parked,
#       "fee": total_fee,
#   }
#   return render_template("receipt.html", receipt=receipt)

import math
from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for


@app.route("/checkout", methods=["POST"])
def checkout():
  plate = request.form["license_plate"].strip()

  with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute(
        """
            SELECT session_id, slot_id, entry_time, driver_name, vehicle_model 
            FROM sessions WHERE license_plate = ? AND exit_time IS NULL
        """,
        (plate,),
    )
    session = cursor.fetchone()

    if not session:
      return "No active session found for this license plate.", 404

    session_id, slot_id, entry_str, driver_name, vehicle_model = session
    entry_time = datetime.strptime(entry_str, "%Y-%m-%d %H:%M:%S")
    exit_time = datetime.now()

    # Calculate exact duration
    duration_seconds = (exit_time - entry_time).total_seconds()
    minutes_parked = math.ceil(duration_seconds / 60)

    # Pricing logic: 1-30 mins = Ksh 200, up to 60 mins = Ksh 300
    if minutes_parked <= 30:
      total_fee = 200.0
      duration_text = f"{minutes_parked} Minute(s)"
    elif minutes_parked <= 60:
      total_fee = 300.0
      duration_text = "1 Hour"
    else:
      hours_parked = math.ceil(minutes_parked / 60)
      total_fee = hours_parked * 300.0
      duration_text = f"{hours_parked} Hours ({minutes_parked} mins)"

    exit_str = exit_time.strftime("%Y-%m-%d %H:%M:%S")

    # Free up slot and save completion record
    cursor.execute(
        "UPDATE slots SET is_occupied = 0 WHERE slot_id = ?", (slot_id,)
    )
    cursor.execute(
        """
            UPDATE sessions 
            SET exit_time = ?, total_fee = ? 
            WHERE session_id = ?
        """,
        (exit_str, total_fee, session_id),
    )
    conn.commit()

  receipt = {
      "driver_name": driver_name,
      "vehicle_model": vehicle_model,
      "license_plate": plate,
      "slot_id": slot_id,
      "entry_time": entry_time.strftime("%d %b %Y, %I:%M %p"),  # e.g., 20 Sep 2026, 12:15 AM
      "exit_time": exit_time.strftime("%d %b %Y, %I:%M %p"),
      "duration": duration_text,
      "fee": total_fee,
  }
  return render_template("receipt.html", receipt=receipt)


if __name__ == "__main__":
  init_db()
  app.run(debug=True)