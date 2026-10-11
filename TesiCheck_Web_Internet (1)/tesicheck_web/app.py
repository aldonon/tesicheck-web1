import io, re, time, csv, random
from difflib import SequenceMatcher
from urllib.parse import urlparse
import streamlit as st
import fitz
from docx import Document
from ddgs import DDGS

st.set_page_config(page_title='TesiCheck Web', page_icon='🎓', layout='wide')
st.title('🎓 TesiCheck Web')
st.caption('Ricerca automatica di somiglianze sul web • gratuito • nessuna fonte da caricare')
st.info('Questo strumento trova possibili corrispondenze nei risultati pubblici dei motori di ricerca. Non misura la percentuale reale di plagio e non rileva con affidabilità l’origine AI.')

def extract(file):
    data=file.getvalue()
    if file.name.lower().endswith('.pdf'):
        with fitz.open(stream=data, filetype='pdf') as pdf:
            return '\n'.join(page.get_text() for page in pdf)
    if file.name.lower().endswith('.docx'):
        d=Document(io.BytesIO(data))
        return '\n'.join(p.text for p in d.paragraphs)
    return data.decode('utf-8',errors='replace')

def sentences(t):
    t=re.sub(r'\s+', ' ', t)
    chunks=re.split(r'(?<=[.!?])\s+',t)
    return [s.strip() for s in chunks if 65<=len(s.strip())<=450 and len(s.split())>=11]

def sim(a,b):
    clean=lambda x: re.sub(r'[^\w\s]','',x.lower())
    return SequenceMatcher(None,clean(a),clean(b)).ratio()

file=st.file_uploader('Carica la tesi (PDF, DOCX o TXT)',type=['pdf','docx','txt'])
limit=st.slider('Numero di frasi da cercare (aumentare richiede più tempo)',5,60,20,5)
if file and st.button('🔎 Cerca somiglianze su Internet',type='primary'):
    try: content=extract(file)
    except Exception as e: st.error(f'Impossibile leggere il documento: {e}'); st.stop()
    pool=sentences(content)
    if not pool: st.error('Non ho trovato frasi estraibili. Se il PDF è una scansione, serve OCR.'); st.stop()
    # Campionamento distribuito nell’intero documento, senza duplicati
    count=min(limit,len(pool))
    indices=sorted(set(round(i*(len(pool)-1)/max(1,count-1)) for i in range(count)))
    selected=[pool[i] for i in indices]
    results=[]; errors=0
    progress=st.progress(0,text='Ricerca in corso...')
    for idx,s in enumerate(selected):
        # Interroga il motore con un estratto tra virgolette
        words=s.split()
        excerpt=' '.join(words[:min(13,len(words))])
        query='"'+excerpt+'"'
        try:
            hits=DDGS(timeout=12).text(query,max_results=5)
            for hit in hits or []:
                title=hit.get('title',''); snippet=hit.get('body',''); url=hit.get('href','')
                if not url.startswith(('https://','http://')): continue
                score=max(sim(excerpt,snippet),sim(s,snippet))
                results.append({'frase_tesi':s,'titolo':title,'url':url,'estratto_risultato':snippet,'somiglianza_estratto':round(score*100,1)})
        except Exception:
            errors+=1
        progress.progress((idx+1)/len(selected),text=f'Frasi esaminate: {idx+1}/{len(selected)}')
        time.sleep(0.7)
    st.session_state['results']=results
    st.session_state['errors']=errors
    st.session_state['searched']=len(selected)

if 'searched' in st.session_state:
    results=st.session_state['results']
    st.subheader('Risultati')
    st.write(f"Frasi cercate: **{st.session_state['searched']}** · Risultati web trovati: **{len(results)}** · Ricerche non riuscite: **{st.session_state['errors']}**")
    if st.session_state['errors']: st.warning('Alcune ricerche non sono riuscite, ad esempio per limiti del motore di ricerca. Riprova più tardi con meno frasi.')
    if not results: st.warning('Nessun risultato recuperato. Questo NON significa che la tesi sia priva di plagio.')
    for r in sorted(results,key=lambda x:x['somiglianza_estratto'],reverse=True):
        with st.expander(f"{r['somiglianza_estratto']}% somiglianza dell’estratto · {r['titolo'][:90]}"):
            st.markdown('**Frase della tesi**'); st.write(r['frase_tesi'])
            st.markdown('**Risultato web**'); st.write(r['estratto_risultato'])
            st.link_button('Apri la fonte',r['url'])
            st.caption('Il punteggio confronta solo gli estratti disponibili, non il contenuto completo della pagina.')
    output=io.StringIO(); w=csv.DictWriter(output,fieldnames=['frase_tesi','titolo','url','estratto_risultato','somiglianza_estratto']); w.writeheader(); w.writerows(results)
    st.download_button('⬇️ Scarica report CSV',output.getvalue().encode('utf-8-sig'),'report_tesicheck.csv','text/csv')

st.divider()
st.caption('Privacy: il file viene elaborato dall’app; frammenti di testo sono inviati al servizio di ricerca. Evita di caricare contenuti riservati su un hosting non fidato. Nessun documento viene intenzionalmente salvato dall’app.')
