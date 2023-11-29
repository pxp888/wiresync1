import os
import logging
from flask import Flask, render_template, request, flash, jsonify

if os.path.exists("env.py"):
    import env


logging.basicConfig(filename=os.environ.get('WIRESYNC_LOG'), encoding='utf-8', level=logging.INFO, format='%(levelname)s - %(asctime)s  >  %(message)s')
logging.info('STARTING UP')


################################# FLASK STUFF #################################

funcs = {}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        logging.info('FORM:', request.form)
    return render_template("index.html")


@app.route("/test", methods=["POST"])
def test():
    if request.method == "POST":
        data = request.get_json()['data']
        try:
            return funcs[data['t']](data)
        except KeyError:
            logging.error("KeyError", data['t'])
            response_data = { "t": "dunno", "answer": "Hello, World!" }
            return jsonify(response_data)
        except Exception as e:
            logging.error("Exception", e)
            response_data = { "t": "exception", "answer": e }
            return jsonify(response_data)




if __name__ == "__main__":

    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)

