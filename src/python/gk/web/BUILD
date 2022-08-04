files(
    name="static",
    sources=["static/**/*"],
)

python_sources(
    name="src",
    dependencies=[
        ":static",
        "src/python/gk/leaderboard",
        "src/python/gk/rider",
        "src/python/gk/timer",
        "3rdparty:requirements.txt#django-bootstrap5",
        "3rdparty:requirements.txt#django-allauth",
        "3rdparty:requirements.txt#django-simple-menu",
    ],
)

pex_binary(
    name="manage",
    entry_point="manage.py",
    dependencies=[
        ":src",
        "3rdparty:requirements.txt#psycopg2-binary",
    ],
    restartable=True,
)

pex_binary(
    name="gunicorn",
    entry_point="gunicorn.py",
    dependencies=[
        ":src",
        "3rdparty:requirements.txt#psycopg2-binary",
    ],
    restartable=True,
)