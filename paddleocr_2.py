from paddleocr import PaddleOCR
# import cv2
# import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import argparse

def draw_ocr(image, boxes, txts, scores, font_path='arial.ttf'):
    """
    Fonction personnalisée pour dessiner les résultats OCR
    """
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(font_path, 20)
    except IOError:
        print(f"⚠️ Impossible de charger la police {font_path}, utilisation de la police par défaut.")
        font = ImageFont.load_default()

    for box, txt, score in zip(boxes, txts, scores):
        # Convertir le numpy array en liste de tuples si nécessaire
        if isinstance(box, np.ndarray):
            box = [tuple(pt) for pt in box]
        
        # Dessiner le polygone (la boîte)
        draw.polygon(box, outline='red')
        
        # Position du texte (coin haut gauche de la boîte)
        # On essaie de placer le texte un peu au-dessus
        left_top = min(box, key=lambda x: x[0] + x[1])
        
        txt_str = f"{txt} ({score:.2f})"
        
        # Dessiner le texte (rouge)
        draw.text((left_top[0], left_top[1] - 25), txt_str, fill='red', font=font)
        
    return np.array(image)

# Initialisation
# use_angle_cls est obsolète, on utilise use_textline_orientation
ocr = PaddleOCR(use_textline_orientation=True, lang='fr')

# Gestion des arguments
parser = argparse.ArgumentParser(description="Script OCR avec PaddleOCR")
parser.add_argument("input_image", help="Chemin vers l'image à traiter")
args = parser.parse_args()

# Chemin vers votre image PNG
img_path = args.input_image

# Vérifier si l'image existe
if not os.path.exists(img_path):
    print(f"❌ Erreur : L'image '{img_path}' n'existe pas.")
    exit(1)

# Définir les chemins de sortie basés sur le nom du fichier d'entrée
base_name = os.path.splitext(os.path.basename(img_path))[0]
output_dir = os.path.dirname(img_path)
if not output_dir:
    output_dir = "."

png_output_path = os.path.join(output_dir, f"{base_name}_resultat.png")
txt_output_path = os.path.join(output_dir, f"{base_name}_resultat.txt")

# Exécution OCR
# ocr.ocr() est obsolète pour la nouvelle version, on utilise predict()
print(f"Traitement de l'image : {img_path}")
result = ocr.predict(img_path)

# Vérification et extraction
if result and result[0]:
    # La structure de retour de predict() est différente de ocr.ocr()
    # C'est une liste de dictionnaires (un par image)
    data = result[0]
    
    # Vérifier si les clés existent
    if 'rec_texts' in data and 'rec_scores' in data and 'dt_polys' in data:
        texts = data['rec_texts']
        scores = data['rec_scores']
        boxes = data['dt_polys']
        
        print("Texte détecté :")
        for text, score in zip(texts, scores):
            print(f"- {text} (confiance: {score:.2%})")
        
        # Création de l'image annotée
        image = Image.open(img_path).convert('RGB')
        
        # Dessiner les résultats
        # Assurons-nous d'utiliser une police valide
        font_path = r'C:\Windows\Fonts\arial.ttf'
        if not os.path.exists(font_path):
             # Fallback si arial n'est pas là
             font_path = r'C:\Windows\Fonts\calibri.ttf'
        
        # draw_ocr attend des boîtes, textes et scores
        im_show = draw_ocr(image, boxes, texts, scores, font_path=font_path)
        im_show = Image.fromarray(im_show)
        
        # Sauvegarder l'image annotée
        # output_path = r'C:\Users\fbpmo\Documents\resultat_ocr.png'
        im_show.save(png_output_path)
        print(f"\nImage annotée sauvegardée : {png_output_path}")

        # Sauvegarder le texte dans un fichier .txt
        # txt_output_path = r'C:\Users\fbpmo\Documents\resultat_ocr.txt'
        with open(txt_output_path, 'w', encoding='utf-8') as f:
            for text, score in zip(texts, scores):
                f.write(f"{text}\n")
        print(f"Fichier texte sauvegardé : {txt_output_path}")
    else:
        print("Structure de résultat inattendue (clés manquantes)")
        print(f"Clés disponibles: {data.keys()}")
else:
    print("Aucun texte détecté dans l'image")
