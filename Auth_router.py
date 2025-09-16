# from flask import Blueprint, request
# from bcrypt import hashpw,checkpw,gensalt
# import jwt
# from dotenv import load_dotenv
# from dbConnection import user_collection
# import os
# load_dotenv()
# router = Blueprint()

# @router.route("/register", methods=['POST'])
# def register():
#     # print(request.json)
#     createuser = request.json
#     isUser = user_collection.find_one({"email": createuser.get("email")})
#     if isUser:
#         return {"err": "User already exists"},401
#     createuser["password"] = hashpw(createuser.get("password").encode("utf-8"), gensalt()).decode("utf-8")

#     # print(createuser.get("password").encode("utf-8"))
#     # print(createuser)
#     new_user = user_collection.insert_one(createuser)
#     # print(new_user)
#     return {"msg": "account registration successful"}, 201


# @router.route("/login", methods=["POST"])
# def login():
#     existinguser = request.json
#     isUser = user_collection.find_one({"email": existinguser.get("email")})
#     if not isUser:
#         return {"msg": "User not found"}, 401
#     # print(isUser.get("password"))
#     isPass = checkpw(existinguser.get("password").encode("utf-8"), isUser.get("password").encode("utf-8"))
#     if not isPass:
#         return {"err": "Inavlid User Details"}, 400
#     # print(isUser.get("_id"))
#     payload = { "id":str(isUser.get("_id")),"email":isUser.get("email")}
#     jwt_token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
    
#     return {"msg": "login successful","jwt_token": jwt_token}
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


@router.route("/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = user_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 401

    if not checkpw(password.encode("utf-8"), user.get("password", "").encode("utf-8")):
        return jsonify({"error": "Invalid credentials"}), 401

    jwt_secret = os.getenv("SECRET_KEY")
    if not jwt_secret:
        return jsonify({"error": "Server misconfiguration: SECRET_KEY missing"}), 500

    token = jwt.encode({"id": str(user.get("_id")), "email": user.get("email")}, jwt_secret, algorithm="HS256")
    return jsonify({"message": "login successful", "token": token}), 200


