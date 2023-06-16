import psycopg2

from io import BytesIO
from utils import *
from datetime import datetime
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
    return render_template('index.html', data=list())

@app.route('/home', methods=['POST'])
def home():
    try:
        delete_images(session["image_filenames"], type="download")
    except KeyError:
        pass
    return render_template('index.html')

@app.route('/date_query', methods=['GET', 'POST'])
def date_query():

    # Get user-selected date range
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Get results from query
    cursor = conn.cursor()
    query = "SELECT \"invoiceNo\", \"uploadDate\" FROM \"invoiceImages\" WHERE \"uploadDate\" BETWEEN (%s) AND (%s);"
    cursor.execute(query, (start_date, end_date))

    raw_data = cursor.fetchall()
    
    data = process_data(raw_data)

    return render_template("index.html", data=data)

@app.route('/new_upload', methods=['POST'])
def new_upload():
    return render_template('submission.html',
                           invoice_exists=False)

@app.route('/select', methods=['POST'])
def select():
    if 'image' in request.files:

        # Get the image
        image = request.files['image']
        image_filename = image.filename
        image = image.read()

        # Keep track of most recent image and all viewed images
        session['image_filename'] = image_filename
        try:
            session['image_filenames'].append(image_filename)
        except KeyError:
            session['image_filenames'] = list()

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
                            invoice_exists=False,
                            image_filename=image_filename
                            )

@app.route('/upload', methods=["POST"])
def upload():
    # Handle Primary key duplications
    # Delete images stored locally
    image_filename = session.get('image_filename')
    image_filepath = os.path.join(os.getcwd(), "static", "images_upload", image_filename)
    if image_filename:

        with open(image_filepath, 'rb') as image:
            image = image.read()

        cursor = conn.cursor()

        # Get the ID value from the request
        image_id = request.form.get('invoiceNo')

        # Get Current Date
        current_date = str(datetime.now().strftime("%Y-%m-%d"))

        # Execute the INSERT query with the provided ID
        query = "INSERT INTO \"invoiceImages\" (\"invoiceNo\", \"imageData\", \"uploadDate\") VALUES (%s, %s, %s);"
        try:
            cursor.execute(query, (int(image_id), psycopg2.Binary(image), current_date))
        except psycopg2.errors.UniqueViolation:
            delete_images(session['image_filenames'])
            return render_template('submission.html', invoice_exists=True)
        
        # Eliminate all residual images
        delete_images(session['image_filenames'])
        return render_template('index.html')
    else:
        return 'No image file provided.'
    
@app.route('/new_retrieve', methods=['POST'])
def new_retrieve():
    return render_template('retrieve.html', has_image=False)

@app.route('/retrieve', methods=["POST"])
def retrieve():

    # Delete any pre-existing downloaded files
    try:
        delete_images(session["image_filenames"], type="download")
    except KeyError:
        pass

    
    image_id = request.form.get("invoiceNo")
    cursor = conn.cursor()
    query = "SELECT \"imageData\" FROM \"invoiceImages\" WHERE \"invoiceNo\" = (%s);"
    
    # Try to retrieve the image
    try:
        cursor.execute(query, (image_id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return render_template("retrieve.html", 
                        invoice_not_exists=True
                        )

    # Ensure retrieved image exists
    image_data = cursor.fetchall()
    try:
        image_data = image_data[0][0]
    except IndexError:
        return render_template("retrieve.html", 
                               invoice_not_exists=True
                               )
    
    # Display image if exists
    if image_data:
        has_image=True
        image_filename = str(datetime.now().strftime("%Y%m%d_%H%M%S")) + ".jpg"
        session['image_filename'] = image_filename
        try:
            session['image_filenames'].append(image_filename)
        except KeyError:
            session['image_filenames'] = list()
        save_image(image_data, image_filename, type="download")
    else:
        has_image=False

    return render_template('retrieve.html', 
                           image_filename=image_filename,
                           invoice_not_exists=False,
                           has_image=has_image)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)