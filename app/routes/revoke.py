from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db import SessionLocal
from app.models import RevokedToken
from config import JWT_SECRET, JWT_ALG

revoke_bp = Blueprint("revoke", __name__)


def _get_db() -> Session:
    return SessionLocal()



# POST /revoke
# Accepts a raw JWT, decodes it, and writes the jti to revoked_tokens.
@revoke_bp.route("/revoke", methods=["POST"])
def revoke_token():
    body = request.get_json(silent=True) or {}
    raw_token = body.get("token")
    reason    = body.get("reason")

    if not raw_token:
        return jsonify({"error": "Missing 'token' field"}), 400

    # Decode without verifying expiry so recently-expired tokens can still
    # be explicitly revoked (prevents replay during the grace window).
    try:
        payload = jwt.decode(
            raw_token,
            JWT_SECRET,
            algorithms=[JWT_ALG],
            options={"verify_exp": False},
        )
    except JWTError as e:
        return jsonify({"error": f"Invalid token: {str(e)}"}), 422

    jti = payload.get("jti")
    sub = payload.get("sub")
    exp = payload.get("exp")

    if not jti:
        return jsonify({"error": "Token has no 'jti' claim — cannot revoke"}), 422

    if not exp:
        return jsonify({"error": "Token has no 'exp' claim — cannot revoke"}), 422

    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc).replace(tzinfo=None)

    db = _get_db()
    try:
        # Idempotent: if already revoked, just return success
        existing = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
        if existing:
            return jsonify({
                "jti":        jti,
                "revoked_at": existing.revoked_at.isoformat(),
                "message":    "Token was already revoked",
            }), 200

        entry = RevokedToken(
            jti        = jti,
            sub        = sub,
            expires_at = expires_at,
            reason     = reason,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)

        return jsonify({
            "jti":        entry.jti,
            "revoked_at": entry.revoked_at.isoformat(),
            "message":    "Token revoked successfully",
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 503
    finally:
        db.close()



# GET /validate/<jti>
# Used by other microservices to check whether a token has been revoked.

@revoke_bp.route("/validate/<string:jti>", methods=["GET"])
def validate_token(jti: str):
    db = _get_db()
    try:
        entry = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
        if entry:
            return jsonify({
                "jti":        jti,
                "is_revoked": True,
                "reason":     entry.reason,
                "revoked_at": entry.revoked_at.isoformat(),
            }), 200

        return jsonify({
            "jti":        jti,
            "is_revoked": False,
        }), 200

    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 503
    finally:
        db.close()



# DELETE /cleanup
# Removes rows whose expires_at is in the past — safe to run on a cron job.

@revoke_bp.route("/cleanup", methods=["DELETE"])
def cleanup_expired():
    db = _get_db()
    try:
        now = datetime.utcnow()
        deleted = (
            db.query(RevokedToken)
            .filter(RevokedToken.expires_at < now)
            .delete(synchronize_session=False)
        )
        db.commit()
        return jsonify({
            "deleted_count": deleted,
            "message":       f"Removed {deleted} expired token(s)",
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 503
    finally:
        db.close()