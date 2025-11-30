from pydantic import BaseModel


class EncryptedSecret(BaseModel):
    id: str
    ciphertext: str
    ttl: int
    passphrase_hash: str | None = None
