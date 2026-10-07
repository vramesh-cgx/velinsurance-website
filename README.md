# velinsurance.com

Website for Velinsurance and Financial Services LLC, served by GitHub Pages from `docs/`.

- Page content: `src/pages/<page>.html`. Styles: `src/style.css`.
- Shared header, footer, menu, contact details and the upload-assistant link: `build.py`.
- Edit on github.com or on the Mac. Every push to `main` rebuilds the site with `build.py` and publishes it
  (GitHub Actions, `.github/workflows/pages.yml`), about a minute later. `docs/` is the build output; never edit it.
- Working on the Mac: `python3 build.py` shows the result locally in `docs/`.

The document upload chat is a separate Google Apps Script web app (`website/upload-assistant/` in the
velinsurance repo); set its `/exec` link as `UPLOAD_URL` in `build.py`.
