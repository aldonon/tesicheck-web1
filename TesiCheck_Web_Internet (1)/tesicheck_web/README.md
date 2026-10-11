# TesiCheck Web

Carica PDF/DOCX/TXT e cerca automaticamente estratti sul web con DDGS. Nessuna chiave API richiesta, ma il motore di ricerca può limitare le richieste.

## Avvio locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Pubblicazione gratuita

1. Crea un repository GitHub e carica `app.py` e `requirements.txt` (NON la tua tesi).
2. Vai su https://share.streamlit.io/ e seleziona **Create app**.
3. Seleziona il repository, branch `main`, file `app.py` e premi **Deploy**.
4. Riceverai un link pubblico `*.streamlit.app`.

## Limiti

Non è un software antiplagio certificato, non controlla archivi chiusi, non determina una percentuale di plagio sull'intero documento e non identifica in modo affidabile testo AI. I punteggi sono somiglianze fra estratti di testo, non probabilità di plagio.
