from flask import Flask, render_template
from monitor import track_webcam

app = Flask(__name__)


@app.route('/')
def front():

    # recent, current = m.main()
    return render_template('index.html')
