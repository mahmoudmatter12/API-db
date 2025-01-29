from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from flask_cors import CORS
import pprint
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database connection URI
# Load environment variables from .env file
load_dotenv()

# Database connection URI
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
# Create database engine
engine = create_engine(DATABASE_URL)

# Middleware to check API key
def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("Authorization")  # Get API key from headers
        if api_key != f"Bearer {API_KEY}":
            return jsonify({"error": "Unauthorized. Invalid API key"}), 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Test database connection
@app.route("/api/test_connection", methods=["GET"])
@require_api_key
def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).fetchone()
        return jsonify(
            {"message": "Database connection successful!", "result": result[0]}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get all users (example)
@app.route("/api/users", methods=["GET"])
@require_api_key
def get_users():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM users")).fetchall()
        # Convert SQLAlchemy Row objects to dictionaries
        users = [
            dict(row._mapping) for row in result
        ]  # Use `row._mapping` for compatibility
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Add a user (example)
@app.route("/api/add-user", methods=["POST"])
@require_api_key
def add_user():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    student_name = data.get("StudentName")
    email = data.get("Email")
    committee = data.get("Committee")
    phone_number = data.get("PhoneNumber") 
    is_accepted = data.get("IsAccepted") or "false"
    community_id = data.get("CommuintyID", "None")

    if not student_name or not email or not committee:
        return jsonify({"error": "StudentName, Email, and Committee are required"}), 400

    try:
        with engine.connect() as connection:
            connection.execute(
                text(
                    "INSERT INTO users (StudentName, Email, Committee, PhoneNumber, IsAccepted, CommuintyID,whatspplink) "
                    "VALUES (:student_name, :email, :committee, :phone_number, :is_accepted, :community_id, :whatsapp_link)"
                ),
                {
                    "student_name": student_name,
                    "email": email,
                    "committee": committee,
                    "phone_number": phone_number,
                    "is_accepted": is_accepted,
                    "community_id": community_id,
                    "whatsapp_link": f"https://wa.me/{phone_number}"
                },
            )
            connection.commit()
        return jsonify({"message": "User added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get-user/<string:student_name>", methods=["GET"])
@require_api_key
def get_user(student_name):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM users WHERE StudentName = :student_name"), {"student_name": student_name}
            ).fetchone()
        if not result:
            return jsonify({"error": "User not found"}), 404
        return jsonify(dict(result._mapping))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/get-user-by-email/<string:email>", methods=["GET"])
@require_api_key
def get_user_by_email(email):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM users WHERE Email = :email"), {"email": email}
            ).fetchone()
        if not result:
            return jsonify({"error": "User not found"}), 404
        return jsonify(dict(result._mapping))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update a user (example)
@app.route("/api/update-user/<string:student_name>", methods=["PATCH"])
@require_api_key
def update_user(student_name):
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    email = data.get("Email")
    committee = data.get("Committee")
    phone_number = data.get("PhoneNumber")
    is_accepted = data.get("IsAccepted")
    community_id = data.get("CommuintyID")

    if not email and not committee and not phone_number and not is_accepted and not community_id:
        return jsonify({"error": "At least one field is required"}), 400

    try:
        with engine.connect() as connection:
            update_fields = []
            update_values = {"student_name": student_name}
            if email:
                update_fields.append("Email = :email")
                update_values["email"] = email
            if committee:
                update_fields.append("Committee = :committee")
                update_values["committee"] = committee
            if phone_number:
                update_fields.append("PhoneNumber = :phone_number")
                update_values["phone_number"] = phone_number
            if is_accepted:
                update_fields.append("IsAccepted = :is_accepted")
                update_values["is_accepted"] = is_accepted
            if community_id:
                update_fields.append("CommuintyID = :community_id")
                update_values["community_id"] = community_id

            update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE StudentName = :student_name"
            connection.execute(text(update_query), update_values)
            connection.commit()
        return jsonify({"message": "User updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a user (example)
@app.route("/api/delete-user/<int:student_ID>", methods=["DELETE"])
@require_api_key
def delete_user(student_ID):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("DELETE FROM users WHERE id = :student_ID"), {"student_ID": student_ID}
            )
            connection.commit()
            if result.rowcount == 0:  # No rows were deleted
                return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get-user-id/<int:student_ID>", methods=["GET"])
@require_api_key
def get_user_id(student_ID):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM users WHERE id = :student_ID"), {"student_ID": student_ID}
            ).fetchone()
        if not result:
            return jsonify({"error": "User not found"}), 404
        return jsonify(dict(result._mapping))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the server
if __name__ == "__main__":
    app.run(debug=True)

