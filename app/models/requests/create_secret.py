from pydantic import BaseModel, Field


class SecretConfig(BaseModel):
    ttl: int = Field(
        default=604800,
        description="Time-to-live in seconds",
        examples=[3600, 86400, 604800],
    )
    passphrase_hash: str | None = Field(
        default=None,
        description="Optional SHA-256 hash of passphrase for verification",
        examples=["a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"],
    )


class CreateSecretRequest(BaseModel):
    ciphertext: str = Field(
        description="Client-side encrypted secret data",
        examples=["U2FsdGVkX1+ZK8jG..."],
    )
    config: SecretConfig = Field(description="Secret configuration options")


class CreateSecretResponse(BaseModel):
    id: str = Field(
        description="Unique identifier for the created secret",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
