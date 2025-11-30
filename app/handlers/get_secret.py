from fastapi import HTTPException
from models.secret import EncryptedSecret
from clients.redis import Redis
from models.requests.get_secret import (
    GetSecretRequest,
    GetSecretResponse,
    PassphraseRequiredResponse,
)


class GetSecretHandler:
    @staticmethod
    async def handle(
        request: GetSecretRequest,
    ) -> GetSecretResponse | PassphraseRequiredResponse:
        encrypted_secret = await Redis().get_encrypted_secret(request.secret_id)

        if not encrypted_secret:
            raise HTTPException(status_code=404, detail="Secret not found")

        if encrypted_secret.passphrase_hash:
            if not request.verify_hash:
                return PassphraseRequiredResponse()

            if request.verify_hash != encrypted_secret.passphrase_hash:
                raise HTTPException(status_code=401, detail="Invalid passphrase")

        await Redis().delete(request.secret_id)
        return GetSecretResponse(ciphertext=encrypted_secret.ciphertext)
