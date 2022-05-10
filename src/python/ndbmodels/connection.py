from typing import Optional

from google.cloud import datastore as ds

CLIENT: Optional[ds.Client] = None


def connect(project: str, namespace: str) -> ds.Client:
    global CLIENT

    CLIENT = ds.Client(
        project=project,
        namespace=namespace,
    )

    return CLIENT


def get_client() -> ds.Client:
    if CLIENT is None:
        raise ValueError("No Client")
    return CLIENT
