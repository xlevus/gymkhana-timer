import flask

from gk.web import models


app = flask.Flask(__name__)


COURSES = [
    ("gp8", "GP8"),
    ("2022mgymkhana-wc1", "2022 MGymkhana WC1"),
    ("2022mgymkhana-wc2", "2022 MGymkhana WC2"),
    ("2022mgymkhana-wc3", "2022 MGymkhana WC3"),
]


@app.route("/_add_course")
def add_course():
    for (id, name) in COURSES:
        models.Course.create(id=id, name=name)
    return "ADDED"


@app.route("/")
def index():
    courses = models.Course.query()

    return flask.render_template(
        "index.j2.html",
        courses=courses,
    )


if __name__ == "__main__":
    from ndbmodels.connection import connect
    connect("coneheads-wgtn", "dev")

    app.run("0.0.0.0", port=8080)
    pass
