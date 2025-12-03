import uuid
from models.requests.create_secret import CreateSecretRequest, CreateSecretResponse
from models.secret import EncryptedSecret
from clients.redis import Redis


class CreateSecretHandler:
    @staticmethod
    async def handle(request: CreateSecretRequest) -> CreateSecretResponse:

        secret = EncryptedSecret(
            id=str(uuid.uuid4()),
            ciphertext=request.ciphertext,
            ttl=request.config.ttl,
            passphrase_hash=request.config.passphrase_hash,
        )

        await Redis().save_encrypted_secret(secret=secret, ttl=request.config.ttl)

        return CreateSecretResponse(id=secret.id)
