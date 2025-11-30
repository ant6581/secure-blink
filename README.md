# Secure Blink 

End-to-end encrypted, self-destructing secret sharing.
Secrets are encrypted and decrypted on the client-side using AES-256-GCM, stored (still encrypted) in Redis, and permanently deleted after being viewed once.

**Live demo**: https://secure-b.link

## Features

- **Client-Side Encryption**: The secrets never leave your device.
- **Ephemeral**: Secrets automatically expire after a set time (TTL).
- **One-Time View**: Secrets are deleted immediately after retrieval.
- **Passphrase Protection**: Optional additional security layer.

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