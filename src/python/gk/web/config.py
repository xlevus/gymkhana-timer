import os

PROJECT = os.getenv("PROJECT", "coneheads-wgtn")
DB_NAMESPACE = os.getenv("DB_NAMESPACE", None)
TEST_DATASTORE_HOST = os.getenv("TEST_DATASTORE_HOST", "localhost:8081")
