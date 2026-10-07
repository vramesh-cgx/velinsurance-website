# velinsurance.com

Website for Velinsurance and Financial Services LLC, served by GitHub Pages from `docs/`.

- Page content: `src/pages/<page>.html`. Styles: `src/style.css`.
- Shared header, footer, menu, contact details and the upload-assistant link: `build.py`.
- After any edit run `python3 build.py`, then commit `src/` and `docs/` together.

The document upload chat is a separate Google Apps Script web app (`website/upload-assistant/` in the
velinsurance repo); set its `/exec` link as `UPLOAD_URL` in `build.py`.
