from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return {"message": "Hello SamaySudarshan V2!"}

if __name__ == '__main__':
    app.run(debug=True)

