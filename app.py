import psycopg2

from io import BytesIO
from utils import *
from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = 'walkerville-brewery'

# Initialize the connection and cursor as None
conn = None
cursor = None

@app.before_request
def before_request():
    global conn, cursor
    if conn is None:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="Invoice",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()

@app.after_request
def after_request(response):
    # Commit the changes and close the cursor
    conn.commit()
    cursor.close()
    return response

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

        # Get the image
        image = request.files['image']
        image_filename = image.filename
        image = image.read()
        session['image_filename'] = image_filename

        # Get the invoice number
        invoice_no = extract_invoice_no(image)

        # Save the image
        save_image(image, image_filename)

        # Set a flag indicating that an image is available
        has_image = True

    else:

        has_image = False
        image_filename = ''

    return render_template("submission.html", 
                            invoice_no=invoice_no, 
                            has_image=has_image,
                            image_filename=image_filename
                            )

@app.route('/upload', methods=["POST"])
def upload():
    # Handle Primary key duplications
    # Delete images stored locally
    image_filename = session.get('image_filename')
    image_filepath = os.path.join(os.getcwd(), "static", "images", image_filename)
    if image_filename:

        with open(image_filepath, 'rb') as image:
            image = image.read()

        cursor = conn.cursor()

        # Get the ID value from the request
        image_id = request.form.get('invoiceNo')

        # Execute the INSERT query with the provided ID
        query = "INSERT INTO \"invoiceImages\" (\"invoiceNo\", \"imageData\") VALUES (%s, %s);"
        cursor.execute(query, (int(image_id), psycopg2.Binary(image)))

        return render_template('index.html')
    else:
        return 'No image file provided.'
    
@app.route('/new_retrieve', methods=['POST'])
def new_retrieve():
    return render_template('retrieve.html', has_image=False)

@app.route('/retrieve', methods=["POST"])
def retrieve():
    print("HELLO")
    # Think about sessions here. Probably can't name every file "temp.jpg"
    image_id = request.form.get("invoiceNo")

    cursor = conn.cursor()

    query = "SELECT \"imageData\" FROM \"invoiceImages\" WHERE \"invoiceNo\" = (%s);"
    cursor.execute(query, (int(image_id),))

    image_data = cursor.fetchall()
    image_data = image_data[0][0]

    if image_data:

        has_image=True
        save_image(image_data, "temp.jpg", type="download")
    else:

        has_image=False

    return render_template('retrieve.html', 
                           image_filename="temp.jpg",
                           has_image=has_image)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)