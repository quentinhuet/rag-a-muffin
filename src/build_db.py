import requests
import bs4
import re
import json
import os

# FONCTIONS Clés 

def extraction_class(soup, class_a_extraire):
    extracts = soup.find_all(class_=class_a_extraire)

    liste_extracts_propre = []

    for extract in extracts:
        texte_extract = extract.get_text(" ", strip=True)
        clean_text = re.sub(r"\s+", " ", texte_extract)
        liste_extracts_propre.append("- " + clean_text)

    all_extracts = "\n".join(liste_extracts_propre)

    return all_extracts

def from_url_to_text(url):
    # Extraction de la page HTML et passage dans Beautiful Soup
    recette_page = requests.get(url)
    try:
        recette_page.raise_for_status()
    except Exception as exc:
        print(f'There was a problem: {exc}')

    recette_page_soup = bs4.BeautifulSoup(recette_page.text, 'html.parser')

    # Extraction des ingrédients
    ingredients_title = 'INGREDIENTS :'
    all_ingredients = extraction_class(recette_page_soup, 'card-ingredient-title')

    # Extraction des ustensils 
    ustensils_title = '\n USTENSILES :'
    all_ustensils = extraction_class(recette_page_soup, 'card-utensil-quantity')

    # Extraction des consignes
    consignes_title = '\n CONSIGNES :'
    all_consignes = extraction_class(recette_page_soup, 'recipe-step-list__container')


    text_tot = '\n'.join([ingredients_title, all_ingredients, consignes_title, all_consignes, ustensils_title, all_ustensils])

    return text_tot

# SCRIPT, tourne une fois pour générer la base de données.
if __name__ == "__main__":
    
    ## 1ère PHASE : Extraction des titres et url des recettes de muffins marmiton
    print("🕵️‍♂️ Phase 1 : Recherche de recettes de muffins")
    resultats = []
    page = 1

    while True: 

        response = requests.get(f'https://www.marmiton.org/recettes/recherche.aspx?aqt=muffin&page={page}')
        try:
            response.raise_for_status()
        except Exception as exc:
            print(f'There was a problem: {exc}') #Rq : a lieu d'office dès que l'on dépasse le nombre de pages de recherches renvoyées par la recherche de muffin.
            print("⬆️ Si la création de la base de donnée s'est déroulée sans accroc, vous pouvez ignorer le message d'erreur ci-dessus. Merci.")
            break

        page_soup = bs4.BeautifulSoup(response.text, 'html.parser')

        for lien in page_soup.find_all('a'):
            url_partielle = lien.get('href')
            
            if url_partielle and '/recettes/recette_' in url_partielle:
                
                if url_partielle.startswith('/'):
                    url_complete = "https://www.marmiton.org" + url_partielle
                else:
                    url_complete = url_partielle
                    
                titre_brut = lien.text 
                titre_propre = titre_brut.strip() 
                
                if "muffin" in titre_propre.lower(): #on vérifie qu'on a bien que des recettes de muffins sur la page.
                    resultats.append({
                        "titre": titre_propre,
                        "url": url_complete
                    })

        page += 1


    nb_de_resultats = len(resultats)

    print(f"✅ Recherche terminée. {nb_de_resultats} recettes trouvées.")

    ## 2ème PHASE : pour chaque titre et url, extraction du texte de la recette (ingrédients, ustensils, consignes)

    print("👨‍🍳 Phase 2 : Extraction des détails...")

    recettes_finales = []
        
    for i in range(nb_de_resultats):
        r = resultats[i]    
        print(f"Recette {i+1} / {nb_de_resultats}")

        url = r['url']
        titre = r['titre']
        texte = from_url_to_text(r['url'])

        dict = {
            "titre": titre,
            "texte": texte,
            "metadata": {"url": url, "source": "Marmiton"}
        }
        
        recettes_finales.append(dict)
        
    # 3ème PHASE : sauvegarde des donnes en un fichier JSON.
    print("💾 Phase 3 : Sauvegarde...")

    current_file_path = os.path.abspath(__file__)
    src_directory = os.path.dirname(current_file_path)
    project_root = os.path.dirname(src_directory)
    file_path = os.path.join(project_root, "data/raw/recettes_fr.json")

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(recettes_finales, f, ensure_ascii=False, indent=4)
        
    print(f"🎉 Terminé ! Base de données générée : {file_path}")
