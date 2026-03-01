import flask
import os
from contact_utils import (
    build_contacts_response,
    process_identification,
    get_all_contacts,
    clear_contacts,
)
from contact import sqldb

app = flask.Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

sqldb.init_app(app)
with app.app_context():
    sqldb.drop_all()
    sqldb.create_all()


@app.route("/favicon.ico")
def favicon():
    return flask.send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/apple-touch-icon.png")
def apple_touch_icon():
    return flask.send_from_directory(
        os.path.join(app.root_path, "static"),
        "apple-touch-icon.png",
        mimetype="image/png",
    )


@app.route("/apple-touch-icon-precomposed.png")
def apple_touch_icon_precomposed():
    return flask.send_from_directory(
        os.path.join(app.root_path, "static"),
        "apple-touch-icon-precomposed.png",
        mimetype="image/png",
    )


@app.route("/")
def hello():
    return flask.render_template("index.html")


@app.route("/identify", methods=["POST"])
def identify():
    data = flask.request.get_json(silent=True)

    if not data:
        return flask.jsonify({"error": "Request body must be JSON"}), 400

    email = data.get("email")
    phone_number = data.get("phoneNumber")

    # Validate input
    if not email and not phone_number:
        return (
            flask.jsonify({"error": "Email or PhoneNumber must be provided"}),
            400,
        )

    contacts = process_identification(
        email=email,
        phone_number=phone_number,
    )

    result = build_contacts_response(contacts)

    return flask.jsonify({"contacts": result}), 200


@app.route("/contacts", methods=["GET"])
def get_contacts():
    contacts = get_all_contacts()
    result = build_contacts_response(contacts)
    return flask.jsonify({"contacts": result}), 200


@app.route("/health", methods=["GET"])
def health():
    return flask.jsonify({"status": "ok"}), 200


@app.route("/reset", methods=["POST"])
def reset():
    clear_contacts()
    return flask.jsonify({"status": "database reset successful"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
