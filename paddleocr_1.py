from paddleocr import PaddleOCR

# 1. Initialiser PaddleOCR (la première fois télécharge les modèles)
ocr = PaddleOCR(use_textline_orientation=True, lang='fr')  # 'fr' pour français

# 2. Charger et traiter l'image
result = ocr.predict(r'C:\Users\fbpmo\Documents\tmp\promenade_soudaine.png')

# 3. Extraire uniquement le texte
if result and result[0] and 'rec_texts' in result[0]:
    texte_complet = "\n".join(result[0]['rec_texts'])
else:
    texte_complet = ""

print("Texte extrait :")
print(texte_complet)
