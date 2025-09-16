# from flask import Flask, request,jsonify
# from dotenv import load_dotenv
# from pymongo import MongoClient
# import os
# import Auth_router

# app = Flask("__name__")

# client = MongoClient(os.getenv("Mongourl"))
# db = client["cagedb"]
# user_collection = db["user"]
# answers = db["useranswers"]


# @app.route("/phq/answers", methods=["POST"])
# def add():
#     data = request.json
#     record = {
#         "total": data.get("total")
#     }
#     answers.insert_one(record)
#     return jsonify({"status": "success", "saved": record})
# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

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

    @app.route("/phq/answers", methods=["POST"])
    def add_answer() -> tuple:
        data = request.get_json(silent=True) or {}
        total = data.get("total")
        if total is None:
            return jsonify({"error": "Missing 'total' in request body"}), 400

        record = {"total": total}
        result = answers_collection.insert_one(record)
        saved = {"_id": str(result.inserted_id), **record}
        return jsonify({"status": "success", "saved": saved}), 201

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)


