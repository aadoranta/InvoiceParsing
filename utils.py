import os
import re
import pytesseract

from PIL import Image
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

def extract_invoice_no(image):

    image_pil = Image.open(BytesIO(image))
    text = pytesseract.image_to_string(image_pil, config='--psm 6')

    pattern1 = r'(?i)no\.\s*(\d+)'
    match1 = re.search(pattern1, text)

    pattern2 = r'(?i)no\.:\s*(\d+)'
    match2 = re.search(pattern2, text)
    
    if match1:
        match1 = match1.group(1)
    if match2:
        match2 = match2.group(1)
    
    if match1 and len(match1) == 5:
        result = match1
    elif match2 and len(match2) == 5:
        result = match2
    else:
        result = None
    
    return result

def get_label_dict(file_path):

    invoice_dict = dict()

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            key, value = line.split(':')
            invoice_dict[key.strip()] = int(value.strip())

    return invoice_dict

def rename_files(directory):
    file_counter = 1
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            file_extension = os.path.splitext(filename)[1]
            new_filename = f"Invoice{file_counter}{file_extension}"
            file_counter += 1

            original_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_filename)

            os.rename(original_path, new_path)

