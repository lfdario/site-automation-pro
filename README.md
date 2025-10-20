
# Rete di siti automatici (IT) — Hugo + GitHub Pages + Agent AI + Dashboard guadagni

Sistema **end-to-end**: contenuti generati da AI, pubblicazione automatica quotidiana, e **dashboard** (traffico + guadagni AdSense) su GitHub Pages.

## Cosa fa
- 2 articoli/giorno in italiano (SEO, FAQ, immagini placeholder).
- Pubblicazione automatica con GitHub Actions.
- **Dashboard** in `/dashboard` con **Chart.js** (traffico GA4 + ricavi AdSense).
- Architettura ad **agenti** (ideazione → scrittura → revisione SEO → pubblicazione).

## Come attivare
1. Crea un repository su GitHub e carica questi file nel branch `main`.
2. In **Settings → Pages**: abilita deploy da **GitHub Actions**.
3. In **Settings → Secrets and variables → Actions** crea le seguenti **secrets**:
   - `OPENAI_API_KEY`
   - `GA4_SERVICE_ACCOUNT_JSON`  (incolla l'intero JSON della service account)
   - `GA4_PROPERTY_ID`           (es. 123456789)
   - `ADSENSE_CLIENT_ID`
   - `ADSENSE_CLIENT_SECRET`
   - `ADSENSE_REFRESH_TOKEN`
   - `ADSENSE_ACCOUNT_ID`        (formato: accounts/pub-XXXXXXXXXXXXXXX)
4. (Opzionale) Inserisci i tuoi ID AdSense in `data/ads.yaml` per mostrare gli annunci.
5. Premi **Run workflow** su `Publish Site` per lanciare subito; altrimenti parte ogni giorno alle 07:00 CET.

### Dove vedo la dashboard
Dopo il primo deploy, apri: `https://<user>.github.io/<repo>/dashboard/`

## Cartella principale
- `scripts/agents/`  → gli agent modulari (ideation, writer, editor, publisher)
- `scripts/generate_posts.py` → orchestratore
- `scripts/update_metrics.py` → aggiorna `public/data/metrics.json`
- `.github/workflows/publish.yml` → build + deploy + generazione contenuti
- `.github/workflows/metrics.yml` → aggiorna dashboard (ogni 3 ore)
