import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("Parser d'annonces LinkedIn vers Excel")

# Boîte de texte pour coller les annonces
raw_text = st.text_area("Collez ici votre texte copié depuis LinkedIn", height=400)

if st.button("Parser et Télécharger XLSX") and raw_text:
    # Séparer les annonces par occurrence "Logo de "
    annonces = raw_text.split("Logo de ")[1:]  # ignore tout ce qui est avant la première annonce
    
    data = []
    
    for annonce in annonces:
        lines = [line.strip() for line in annonce.split("\n") if line.strip()]
        
        # Nom de l'entreprise
        entreprise = lines[0] if len(lines) > 0 else ""
        
        # Titre du poste : on prend la première ligne qui contient "H/F" ou "Project"
        titre = next((l for l in lines[1:5] if re.search(r'H/F|Project|Chef', l)), "")
        
        # Localisation : ligne qui contient un pays ou une ville
        localisation = next((l for l in lines if re.search(r'France|Suisse|Bilbao|Genève|Toulouse|Orléans', l)), "")
        
        # Date de publication : "il y a X semaine(s) / jour(s)"
        date_pub = next((re.search(r"il y a .*", l).group(0) for l in lines if "il y a" in l), "")
        
        # Nb de personnes qui ont cliqué sur Postuler
        nb_clicks = next((re.search(r"Plus de ([\d\s]+) personnes", l).group(1).replace(" ", "") 
                          for l in lines if "Postuler" in l), "")
        
        data.append({
            "Entreprise": entreprise,
            "Titre": titre,
            "Localisation": localisation,
            "Date de publication": date_pub,
            "Nb de clics": nb_clicks
        })
    
    df = pd.DataFrame(data)
    
    # Générer le fichier Excel en mémoire
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    
    st.success("Parsing terminé !")
    st.download_button(
        label="Télécharger le fichier XLSX",
        data=output,
        file_name="annonces_linkedin.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
