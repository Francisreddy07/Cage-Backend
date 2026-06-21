
from flask import Blueprint, request, jsonify
from bcrypt import hashpw, checkpw, gensalt
import jwt
import os
from dotenv import load_dotenv

from dbConnection import user_collection


load_dotenv()

router = Blueprint("auth", __name__)


@router.route("/register", methods=["POST"])
def register():
    # try:
        payload = request.get_json(silent=True) or {}
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""
        name = payload.get("name")

        if not email or not password:
            return jsonify({"error": "email and password are required"}), 400

        existing = user_collection.find_one({"email": email})
        if existing:
            return jsonify({"error": "User already exists"}), 409

        hashed = hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")
        user_doc = {"email": email, "password": hashed}
        if name:
            user_doc["name"] = name

        user_collection.insert_one(user_doc)
        return jsonify({"message": "account registration successful"}), 201
    # except Exception as e:
    #     print("Registration error:", e)
    #     return jsonify({"error": "Internal server error", "details": str(e)}), 500

@router.route("/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = user_collection.find_one({"email": email})
    print(user)
    if not user:
        return jsonify({"error": "User not found"}), 401

    if not checkpw(password.encode("utf-8"), user.get("password", "").encode("utf-8")):
        return jsonify({"error": "Invalid credentials"}), 401

    jwt_secret = os.getenv("SECRET_KEY")
    if not jwt_secret:
        return jsonify({"error": "Server misconfiguration: SECRET_KEY missing"}), 500

    token = jwt.encode({"id": str(user.get("_id")), "email": user.get("email")}, jwt_secret, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return jsonify({"message": "login successful", "token": token, "user": str(user.get("_id"))}), 200


