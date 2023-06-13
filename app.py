from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
# Must verify that the invoice number is unique
# What to title the file after it has been saved
def upload():
    if 'image' in request.files:
        image = request.files['image']
        image.save('uploaded_image.jpg')
        return 'Image uploaded successfully!'
    else:
        return 'No image file provided.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)