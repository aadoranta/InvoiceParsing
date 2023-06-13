import psycopg2
from utils import *
from flask import Flask, render_template, request

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="Invoice",
    user="postgres",
    password="postgres"
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_upload', methods=['POST'])
def new_upload():
    return render_template('submission.html')

@app.route('/select', methods=['POST'])
# Must verify that the invoice number is unique
# What to title the file after it has been saved
def select():
    if 'image' in request.files:
        image = request.files['image']
        image_data = image.read()
        invoice_no = extract_invoice_no(image_data)
        print(invoice_no)
        return render_template("submission.html", invoice_no=invoice_no)



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

    #     if 'image' in request.files:
    #     image = request.files['image']
    #     image_data = image.read()
    #     cursor = conn.cursor()

    #     # Get the ID value from the request
    #     image_id = request.form.get('image_id')

    #     # Execute the INSERT query with the provided ID
    #     query = "INSERT INTO invoiceImages (id, image_data) VALUES (%s, %s);"
    #     cursor.execute(query, (image_id, psycopg2.Binary(image_data)))

    #     conn.commit()
    #     cursor.close()
    #     conn.close()

    #     return f'Image uploaded with ID: {image_id}'
    # else:
    #     return 'No image file provided.'