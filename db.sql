CREATE TABLE IF NOT EXISTS revoked_tokens (
  jti        VARCHAR(64)  NOT NULL,
  sub        VARCHAR(128) NULL,
  expires_at DATETIME     NOT NULL,
  revoked_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reason     VARCHAR(255) NULL,
  PRIMARY KEY (jti),
  INDEX idx_expires_at (expires_at),
  INDEX idx_sub (sub)
);