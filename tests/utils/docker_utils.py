import os
import time

import docker
from docker.models.containers import Container


def is_container_ready(container: Container) -> bool:
    container.reload()
    return container.status == "running"


def wait_for_stable_status(
    container: Container, stable_duration: int = 3, interval: int = 1
) -> bool:
    start_time = time.time()
    stable_count = 0
    while time.time() - start_time < stable_duration:
        if is_container_ready(container):
            stable_count += 1
        else:
            stable_count = 0

        if stable_count >= stable_duration / interval:
            return True

        time.sleep(interval)
    return False


def start_database_container() -> Container:
    client = docker.from_env()
    scripts_dir = os.path.abspath("./scripts")
    container_name = "test-db"

    try:
        existing_container = client.containers.get(container_name)
        print(f"Container {container_name} already exists. Stopping and removing.")
        existing_container.stop()
        existing_container.remove()
        print(f"Container {container_name} stopped and removed.")
    except docker.errors.NotFound:
        print(f"Container {container_name} not found.")

    # Define container configuration
    container_config = {
        "name": container_name,
        "image": "postgres",
        "detach": True,
        "ports": {"5432": "5434"},
        "environment": {
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
        },
        "volumes": [f"{scripts_dir}:/docker-entrypoint-initdb.d"],
        "network_mode": "user-items_dev-network",
    }

    container = client.containers.run(**container_config)
    while not is_container_ready(container):
        time.sleep(1)
    print(f"Container {container_name} started.")

    if not wait_for_stable_status(container):
        raise RuntimeError(
            f"Container {container_name} did not stabilize within the expected time."
        )

    return container
