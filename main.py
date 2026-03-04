from flask import Flask, render_template
from app.routes.revoke import revoke_bp
from app.db import Base, engine
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG

app = Flask(__name__)
app.register_blueprint(revoke_bp)

# Create table if it doesn't exist yet (safe no-op if already created by db.sql)
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}, 200


@app.get("/")
def revoke_tester():
    return render_template("test_revoke.html")


if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
