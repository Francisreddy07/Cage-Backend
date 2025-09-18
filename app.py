from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId
from Auth_router import router as auth_router
from dbConnection import answers_collection


def create_app() -> Flask:

    load_dotenv()

    app = Flask(__name__)

    cors_origin = os.getenv("CORS_ORIGIN", "*")
    CORS(
        app,
        resources={r"/*": {"origins": cors_origin}},
        supports_credentials=True,
        expose_headers=["Content-Type", "Authorization"],
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        max_age=3600,
    )

    @app.before_request
    def log_request():
        app.logger.info(f"➡ {request.method} {request.path} from {request.remote_addr}")
        if request.method != "GET":
            app.logger.debug(f"Body: {request.get_data(as_text=True)}")

    @app.after_request
    def log_response(response):
        app.logger.info(f"⬅ {request.method} {request.path} -> {response.status_code}")
        return response

    @app.errorhandler(Exception)
    def handle_exception(err):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Internal Server Error"}), 500

    app.register_blueprint(auth_router, url_prefix="/auth")

    @app.route("/health", methods=["GET"])
    def health() -> tuple:
        return jsonify({"status": "ok"}), 200

    @app.route("/test/answers", methods=["POST"])
    def add_answer() -> tuple:
        data = request.json

        isTaken = answers_collection.find_one({"user_id": (data.get("userId")), "name": data.get("name")})
        if isTaken:
            answers_collection.update_one({"_id": ObjectId(isTaken.get("_id"))},{"$set": data})
            return jsonify({"status": "success"}), 201
        total = data.get("total")
        if total is None:
            return jsonify({"error": "Missing 'total' in request body"}), 400

        record = {"total": total,"user_id": data.get("userId"), "name": data.get("name")}
        result = answers_collection.insert_one(record)
        return jsonify({"status": "success"}), 201
    @app.route("/user/result/<id>" )
    def getScores(id):
        user_score = answers_collection.find({"user_id": id}, {"_id": 0})
        
        return {"user_scores": list(user_score)}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)


