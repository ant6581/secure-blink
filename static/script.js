document.addEventListener('DOMContentLoaded', () => {
    const createView = document.getElementById('create-view');
    const readView = document.getElementById('read-view');
    const secretInput = document.getElementById('secret-input');
    const generateBtn = document.getElementById('generate-btn');
    const resultArea = document.getElementById('result-area');
    const secretLinkInput = document.getElementById('secret-link');
    const copyBtn = document.getElementById('copy-btn');
    const deleteBtn = document.getElementById('delete-btn');
    const revealBtn = document.getElementById('reveal-btn');
    const secretDisplay = document.getElementById('secret-display');
    const secretContent = document.getElementById('secret-content');
    const errorMsg = document.getElementById('error-msg');

    let currentSecretId = null; // Track created secret ID

    // Check if we are in "read" mode (hash present)
    if (window.location.hash.length > 1) {
        createView.classList.add('hidden');
        readView.classList.remove('hidden');
    }

    const passphraseInput = document.getElementById('passphrase-input');
    const passphraseSection = document.getElementById('passphrase-section');
    const decryptPassphraseInput = document.getElementById('decrypt-passphrase');
    const submitPassphraseBtn = document.getElementById('submit-passphrase-btn');

    // Helper to hash passphrase
    async function hashPassphrase(passphrase) {
        const encoder = new TextEncoder();
        const data = encoder.encode(passphrase);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }

    generateBtn.addEventListener('click', async () => {
        const text = secretInput.value;
        if (!text) return;

        try {
            // 1. Generate Key
            const key = await window.crypto.subtle.generateKey(
                { name: "AES-GCM", length: 256 },
                true,
                ["encrypt", "decrypt"]
            );

            // 2. Encrypt
            const iv = window.crypto.getRandomValues(new Uint8Array(12));
            const encodedText = new TextEncoder().encode(text);
            const encryptedData = await window.crypto.subtle.encrypt(
                { name: "AES-GCM", iv: iv },
                key,
                encodedText
            );

            // 3. Export key to string (JWK)
            const exportedKey = await window.crypto.subtle.exportKey("jwk", key);

            // 4. Prepare payload (IV + Ciphertext)
            const ivArray = Array.from(iv);
            const encryptedArray = Array.from(new Uint8Array(encryptedData));

            const payload = btoa(String.fromCharCode.apply(null, ivArray)) + "." +
                btoa(String.fromCharCode.apply(null, encryptedArray));

            const ttlSelect = document.getElementById('ttl-select');
            const ttl = parseInt(ttlSelect.value);

            // Handle Passphrase
            let passphraseHash = null;
            if (passphraseInput.value) {
                passphraseHash = await hashPassphrase(passphraseInput.value);
            }

            // 5. Send to server
            const response = await fetch('/api/secret', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ciphertext: payload,
                    config: {
                        ttl: ttl,
                        passphrase_hash: passphraseHash
                    }
                })
            });

            if (!response.ok) throw new Error('Failed to store secret');
            const data = await response.json();
            const id = data.id;

            // 6. Construct Link
            const keyString = JSON.stringify(exportedKey);
            const keyBase64 = btoa(keyString).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

            const link = `${window.location.origin}/#${id}_${keyBase64}`;

            currentSecretId = id; // Store for delete
            secretLinkInput.value = link;
            resultArea.classList.remove('hidden');
            document.getElementById('input-section').classList.add('hidden');
        } catch (err) {
            console.error(err);
            alert('Error creating secret');
        }
    });

    const copySecretBtn = document.getElementById('copy-secret-btn');

    function showCopyFeedback(btn) {
        const originalHtml = btn.innerHTML;
        btn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
        `;

        setTimeout(() => {
            btn.innerHTML = originalHtml;
        }, 2000);
    }

    copyBtn.addEventListener('click', () => {
        const text = secretLinkInput.value;
        navigator.clipboard.writeText(text).then(() => {
            showCopyFeedback(copyBtn);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    });

    if (copySecretBtn) {
        copySecretBtn.addEventListener('click', () => {
            const text = secretContent.textContent;
            navigator.clipboard.writeText(text).then(() => {
                showCopyFeedback(copySecretBtn);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        });
    }

    deleteBtn.addEventListener('click', async (e) => {
        e.preventDefault();

        if (!currentSecretId) return;

        if (!confirm('Are you sure you want to delete this secret? It will no longer be accessible.')) {
            return;
        }

        try {
            const response = await fetch(`/api/secret/${currentSecretId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                // Reset to create mode
                resultArea.classList.add('hidden');
                document.getElementById('input-section').classList.remove('hidden');
                secretInput.value = '';
                passphraseInput.value = ''; // Clear passphrase
                currentSecretId = null;
            } else {
                alert('Failed to delete secret. It may have already been accessed or deleted.');
            }
        } catch (err) {
            console.error(err);
            alert('Error deleting secret');
        }
    });

    async function fetchAndReveal(id, keyBase64, passphraseHash = null) {
        let url = `/api/secret/${id}`;
        if (passphraseHash) {
            url += `?verify_hash=${passphraseHash}`;
        }

        const response = await fetch(url);

        if (response.status === 404) {
            throw new Error('Secret not found or already viewed.');
        }

        if (response.status === 401) {
            // 401 now only means WRONG passphrase (actual auth error)
            throw new Error('Invalid passphrase. Please try again.');
        }

        if (!response.ok) throw new Error('Network error');

        const data = await response.json();

        // Check if passphrase is required (business logic, not error)
        if (data.passphrase_required) {
            revealBtn.classList.add('hidden');
            passphraseSection.classList.remove('hidden');
            errorMsg.classList.add('hidden');
            return; // Stop here, wait for user input
        }

        const payload = data.ciphertext;

        // 2. Parse payload
        const [ivB64, cipherB64] = payload.split('.');
        const iv = new Uint8Array(atob(ivB64).split('').map(c => c.charCodeAt(0)));
        const ciphertext = new Uint8Array(atob(cipherB64).split('').map(c => c.charCodeAt(0)));

        // 3. Import Key
        const keyString = atob(keyBase64.replace(/-/g, '+').replace(/_/g, '/'));
        const keyJwk = JSON.parse(keyString);
        const key = await window.crypto.subtle.importKey(
            "jwk",
            keyJwk,
            { name: "AES-GCM" },
            true,
            ["decrypt"]
        );

        // 4. Decrypt
        const decryptedData = await window.crypto.subtle.decrypt(
            { name: "AES-GCM", iv: iv },
            key,
            ciphertext
        );

        const decodedText = new TextDecoder().decode(decryptedData);

        secretContent.textContent = decodedText;
        secretDisplay.classList.remove('hidden');
        revealBtn.classList.add('hidden');
        passphraseSection.classList.add('hidden');
        errorMsg.classList.add('hidden');
    }

    revealBtn.addEventListener('click', async () => {
        try {
            const hash = window.location.hash.substring(1); // Remove #
            const [id, keyBase64] = hash.split('_');

            if (!id || !keyBase64) {
                throw new Error('Invalid link format');
            }

            await fetchAndReveal(id, keyBase64);

        } catch (err) {
            console.error(err);
            errorMsg.textContent = err.message;
            errorMsg.classList.remove('hidden');
            revealBtn.classList.add('hidden');
        }
    });

    submitPassphraseBtn.addEventListener('click', async () => {
        const passphrase = decryptPassphraseInput.value;
        if (!passphrase) return;
        
        errorMsg.classList.add('hidden');
        try {
            const hash = window.location.hash.substring(1);
            const [id, keyBase64] = hash.split('_');

            const pHash = await hashPassphrase(passphrase);
            await fetchAndReveal(id, keyBase64, pHash);

        } catch (err) {
            console.error(err);
            errorMsg.textContent = err.message;
            errorMsg.classList.remove('hidden');
        }
    });
});
