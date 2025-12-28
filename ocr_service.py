import os
import sys

# Configuration spécifique pour Vercel / Environnement Serverless
# Si on est sur Vercel, le seul dossier inscriptible est /tmp
if os.environ.get('VERCEL') or not os.access(os.path.expanduser('~'), os.W_OK):
    os.environ['HOME'] = '/tmp'
    os.environ['XDG_CACHE_HOME'] = '/tmp/.cache'

from paddleocr import PaddleOCR
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pypdfium2 as pdfium

# Initialisation du modèle (une seule fois)
# use_angle_cls est obsolète, on utilise use_textline_orientation
ocr_engine = PaddleOCR(use_textline_orientation=True, lang='fr')

def draw_ocr_results(image, boxes, txts, scores, font_path='arial.ttf'):
    """
    Fonction personnalisée pour dessiner les résultats OCR sur une image PIL
    """
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(font_path, 20)
    except IOError:
        # Fallback fonts
        possible_fonts = [
            # Windows
            r'C:\Windows\Fonts\arial.ttf',
            r'C:\Windows\Fonts\calibri.ttf',
            # Linux / Vercel
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
        ]
        font = ImageFont.load_default()
        for f in possible_fonts:
            if os.path.exists(f):
                try:
                    font = ImageFont.truetype(f, 20)
                    break
                except:
                    continue

    for box, txt, score in zip(boxes, txts, scores):
        if isinstance(box, np.ndarray):
            box = [tuple(pt) for pt in box]
        
        draw.polygon(box, outline='red')
        
        left_top = min(box, key=lambda x: x[0] + x[1])
        txt_str = f"{txt} ({score:.2f})"
        
        draw.text((left_top[0], left_top[1] - 25), txt_str, fill='red', font=font)
        
    return image

def process_file(file_path, output_dir):
    """
    Traite un fichier (image ou PDF) et retourne les résultats.
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    results = []
    
    if file_ext == '.pdf':
        # Traitement PDF
        pdf = pdfium.PdfDocument(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        for i, page in enumerate(pdf):
            # Rendu de la page en image
            bitmap = page.render(scale=2.0) # Augmenter l'échelle pour une meilleure OCR
            pil_image = bitmap.to_pil()
            
            # Sauvegarder l'image temporaire (optionnel, mais utile pour le debug/affichage)
            page_img_filename = f"{base_name}_page_{i+1}.png"
            page_img_path = os.path.join(output_dir, page_img_filename)
            pil_image.save(page_img_path)
            
            # Traiter l'image
            page_result = process_image(page_img_path, output_dir, original_filename=page_img_filename)
            results.append(page_result)
            
    else:
        # Traitement Image standard
        result = process_image(file_path, output_dir)
        results.append(result)
        
    return results

def process_image(img_path, output_dir, original_filename=None):
    """
    Traite une image unique avec PaddleOCR.
    """
    if original_filename is None:
        original_filename = os.path.basename(img_path)
        
    base_name = os.path.splitext(original_filename)[0]
    
    # Exécution OCR
    ocr_result = ocr_engine.predict(img_path)
    
    extracted_text = ""
    annotated_image_path = ""
    
    if ocr_result and ocr_result[0]:
        data = ocr_result[0]
        
        if 'rec_texts' in data and 'rec_scores' in data and 'dt_polys' in data:
            texts = data['rec_texts']
            scores = data['rec_scores']
            boxes = data['dt_polys']
            
            # Concaténer le texte
            extracted_text = "\n".join(texts)
            
            # Créer l'image annotée
            image = Image.open(img_path).convert('RGB')
            annotated_image = draw_ocr_results(image, boxes, texts, scores)
            
            annotated_image_filename = f"{base_name}_annotated.png"
            annotated_image_path = os.path.join(output_dir, annotated_image_filename)
            annotated_image.save(annotated_image_path)
            
            return {
                "success": True,
                "filename": original_filename,
                "text": extracted_text,
                "annotated_image": annotated_image_filename,
                "full_annotated_path": annotated_image_path
            }
            
    return {
        "success": False,
        "filename": original_filename,
        "error": "Aucun texte détecté ou structure inattendue."
    }

