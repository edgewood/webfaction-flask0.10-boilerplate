import os

from flask import (
    Flask,
    flash,
    render_template,
    request,
    )
from myapp import config

# create and configure application
app = Flask(__name__)
config.configure_app(app)

@app.route('/', methods=['GET', 'POST'])
def hello():
    name = None
    if request.method == 'POST':
        if request.form['name']:
            name = request.form['name']
    if not name:
        flash("Using default name")
        name = 'world'
    return render_template('hello.html', name=name)

if __name__ == '__main__':
    app.run()
