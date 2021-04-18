from flask import Flask

from sensor import get_pmi_result

app = Flask(__name__)

@app.route('/')
def pmi_result():
    result = get_pmi_result()
    return result 

if __name__ == "__main__":
    app.run()
