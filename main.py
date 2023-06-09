from utils import *

def read_invoices(directory):

    labels = get_label_dict('labels/labels.txt')

    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            print("\n\n"+filename+"\n\n")  
            image = Image.open(os.path.join(directory, filename))
            text = pytesseract.image_to_string(image, config='--psm 6')
            extracted_invoice_no = extract_invoice_no(text)
            true_label = labels[filename]

            if int(extracted_invoice_no) == int(true_label):
                print("MATCH")
            else:
                print(extracted_invoice_no, true_label)


if __name__ == "__main__":
    read_invoices('images')

