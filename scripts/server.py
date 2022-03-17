from flask import Flask, jsonify

from tg_listener.repo.arctic_repo import arctic_db

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/symbols")
def symbols():
    return jsonify(arctic_db.db_tick.list_symbols())
