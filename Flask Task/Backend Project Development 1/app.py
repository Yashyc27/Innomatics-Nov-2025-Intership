from flask import Flask, render_template, request
import re

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    regex = ""
    test_string = ""
    matches = []
    error = None

    if request.method == "POST":
        regex = request.form.get("regex", "")
        test_string = request.form.get("test_string", "")
        try:

            matches = re.findall(regex, test_string)
        except re.error as e:
            error = str(e)

    return render_template("index.html", regex=regex, test_string=test_string, matches=matches, error=error)

if __name__ == "__main__":
    app.run(debug=True)