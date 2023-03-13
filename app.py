from flask import Flask, render_template
# import monitor as m
app = Flask(__name__)


@app.route('/')
def front():

    # recent, current = m.main()
    return render_template('index.html')
