from flask import Flask
app = Flask(__name__)
@app.route("/")
def home():
return "RAMOVIC COMMUNITY IS LIVE"
if __name__== "main__":
     app.run()
