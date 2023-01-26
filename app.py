from flask import Flask, request, render_template, redirect, flash, url_for, Response
from werkzeug.utils import secure_filename
import os.path
import os
import utils_2.centroid_tracker as centroid
import utils_2.get_frame as get_frame
import cv2 as cv

app = Flask(__name__)
ENV = 'dev'

if ENV == 'dev':
    app.debug = True

else:
    app.debug = False

# Feed Link
feed = 'http://176.57.73.231/mjpg/video.mjpg'
timeToWait = 3000

# File with the prediction boxes
outputFile = 'static/boxes.jpg'

# Initialize the Centroid Tracker
ct = centroid.CentroidTracker()

# Detector Params
confThreshold = 0.5  # Confidence Threshold
nmsThreshold = 0.4   # Non max suppression threshold
inpWidth = 416       # Image Width to feed the network
inpHeight = 416      # Image Height to feed the network

# Load Classes
classesFile = "dnn_config_files/coco.names"
classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

# Load model and configuration file
modelConfiguration = "dnn_config_files/yolov3.cfg"
# modelWeights = "https://nyc3.digitaloceanspaces.com/portfolio92/people-counter/model/yolov3.weights"
# net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
# net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
# net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

# Configurations for image uploading
DEV_PATH = '/app/static/images/uploads'
app.config["IMAGE_UPLOADS"] = 'static/images/uploads'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPG", "JPEG"]
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SEND_FILE_MAX_FILESIZE'] = 2.5 * 1024 * 1024


@app.route('/')
def index():
    return render_template('index.html')


def allowed_size(filesize):
    """Verify if the file size is valid.

    Arguments:
        filesize {int} -- Size of the file

    Returns:
        {boolean} -- True if the file size is valid. False otherwise. 
    """
    if int(filesize) <= app.config['SEND_FILE_MAX_FILESIZE']:
        return True
    else:
        return False


def allowed_image(filename):
    """Verify if the file type is allowed

    Arguments:
        filename {string} -- File Name

    Returns:
        {boolean} -- True if file extesions is allowed. False otherwise. 
    """
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


@app.route('/upload', methods=["GET", "POST"])
def upload_image():
    try:
        if request.method == 'POST':
            if request.files:
                if not allowed_size(request.cookies.get("filesize")):
                    flash("File exceeded maximum size.")
                    return redirect(request.url)

                image = request.files["image"]

                if image.filename == "":
                    flash("Image must have a name!")
                    return redirect(request.url)

                if not allowed_image(image.filename):
                    flash("Only JPG, JPEG allowed!")
                    return redirect(request.url)

                else:
                    filename = secure_filename(image.filename)
                    print("image", image.filename)

                    ext = filename.rsplit(".", 1)[1]
                    fileName = 'input'
                    if os.path.exists(fileName):
                        os.remove(fileName)
                    image.save(os.path.join(
                        app.config["IMAGE_UPLOADS"], fileName))
                    # suc, numObj, conf, errorMsg = do_predictions(live=False)
                    return render_template('upload.html')
                    # return render_template('upload.html', uploaded=True, numObj=numObj, conf=round(conf*100, 1), suc=suc, errorMsg=errorMsg)
        return render_template('upload.html')
    except Exception as e:
        return render_template('upload.html')
