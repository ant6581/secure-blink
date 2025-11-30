from pydantic import BaseModel


class SecretConfig(BaseModel):
    ttl: int = 604800  # 1 week
    passphrase_hash: str | None = None


class CreateSecretRequest(BaseModel):
    ciphertext: str
    config: SecretConfig
