from flask import (
    Flask,
    flash,
    render_template,
    request,
    )

# configuration
DEBUG = True
SECRET_KEY = 'development key'  # TODO generate random key for deployed app

# create application
app = Flask(__name__)
app.config.from_object(__name__)

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
