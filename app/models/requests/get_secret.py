from pydantic import BaseModel


class GetSecretRequest(BaseModel):
    secret_id: str
    verify_hash: str | None = None

class GetSecretResponse(BaseModel):
    ciphertext: str