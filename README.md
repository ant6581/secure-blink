# Secure Blink 

End-to-end encrypted, self-destructing secret sharing.
Secrets are encrypted and decrypted on the client-side using AES-256-GCM, stored (still encrypted) in Redis, and permanently deleted after being viewed once.

**Live demo**: https://secure-b.link

## Features

- **Client-Side Encryption**: The secrets never leave your device.
- **Ephemeral**: Secrets automatically expire after a set time (TTL).
- **One-Time View**: Secrets are deleted immediately after retrieval.
- **Passphrase Protection**: Optional additional security layer.

## How it Works

Secure Blink uses a **Zero-Knowledge** architecture. This means the server never knows the secret, the passphrase, or the encryption key.

### 1. Encryption (Client-Side)
When you click "Create Secret Link", the following happens in your browser:
1. A random **AES-256-GCM** key is generated.
2. A random initialization vector (IV) is generated.
3. The secret text is encrypted using the key and IV.
4. The key is exported as a JWK (JSON Web Key).

### 2. Storage (Server-Side)
The browser sends *only* the encrypted data (ciphertext + IV) to the server. The key remains in your browser.

**Example Payload sent to Server:**
```json
{
  "ciphertext": "YmFzZTY0X2l2...YmFzZTY0X2NpcGhlcnRleHQ=",
  "config": {
    "ttl": 604800,
    "passphrase_hash": "optional_sha256_hash"
  }
}
```

### 3. Link Generation
The server returns a unique ID for the secret. The browser then constructs the shareable link:

`https://secure-b.link/#<secret_id>_<encryption_key>`

- **`secret_id`**: Used to fetch the encrypted data from the server.
- **`encryption_key`**: The part after the `#` (URL fragment) is **never sent to the server**. Browsers do not include the fragment in HTTP requests.

### 4. Decryption
When the recipient opens the link:
1. The browser extracts the `secret_id` and `encryption_key` from the URL.
2. It fetches the encrypted data from the server using the `secret_id`.
3. It decrypts the data locally using the `encryption_key`.

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/ant6581/secure-blink.git
   cd secure-blink
   ```

2. **Configure Environment**
   Create a `.env` file in the root directory:
   ```env
   REDIS_URL=redis://redis:6379/0 # default Redis URL
   ```

3. **Build and run with Docker**
   ```bash
   docker compose up --build
   ```

The application will be available at `http://0.0.0.0:8000`.

# Contributing
PRs and issues are very welcome!
Just keep it secure and keep it simple.

[![Stars](https://img.shields.io/github/stars/ant6581/secure-blink?style=flat-square)](https://github.com/ant6581/secure-blink/stargazers) [![License](https://img.shields.io/github/license/ant6581/secure-blink?style=flat-square)](LICENSE)