python_sources(
    name="src",
    dependencies=[
        "src/python/gk/leaderboard",
    ],
)

pex_binary(
    name="manage",
    entry_point="manage.py",
    dependencies=[":src"],
    restartable=True,
)

pex_binary(
    name="gunicorn",
    entry_point="gunicorn.py",
    dependencies=[":src"],
    restartable=True,
)