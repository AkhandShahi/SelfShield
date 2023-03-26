from flask import Flask, render_template, request

app = Flask(__name__)
app.debug = True

app.static_folder = 'static'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    pass

@app.route('/register')
def register():
    return render_template('sign.html')


@app.route('/logout')
def logout():
    pass

if __name__ == "__main__":
    app.run()
