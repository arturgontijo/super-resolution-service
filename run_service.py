import pathlib
import subprocess
import time
import os
import sys
import logging
import threading

from service import registry

logging.basicConfig(
    level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s"
)
log = logging.getLogger("run_super_resolution_service")


def main():

    root_path = pathlib.Path(__file__).absolute().parent

    # All services modules go here
    service_modules = ["service.super_resolution_service"]

    # Removing all previous snetd .db file
    os.system("rm *.db")

    # Call for all the services listed in service_modules
    start_all_services(root_path, service_modules)

    # Infinite loop to serve the services
    while True:
        try:
            time.sleep(1)
        except Exception as e:
            log.error(e)
            exit(0)


def start_all_services(cwd, service_modules):
    """
    Loop through all service_modules and start them.
    For each one, an instance of Daemon 'snetd' is created.
    snetd will start with configs from 'snet_SERVICENAME_config.json'
    and will create a 'db_SERVICENAME.db' database file for each service.
    """
    try:
        for i, service_module in enumerate(service_modules):
            server_name = service_module.split(".")[-1]
            log.info("Launching {} on ports {}".format(str(registry[server_name]), service_module))

            process_thread = threading.Thread(target=start_service, args=(cwd, service_module))

            # Bind the thread with the main() to abort it when main() exits.
            process_thread.daemon = True
            process_thread.start()

    except Exception as e:
        log.error(e)
        return False

    return True


def start_service(cwd, service_module):
    """
    Starts SNET Daemon ("snetd") and the python module of the service at the passed gRPC port.
    """
    start_snetd(str(cwd))

    service_name = service_module.split(".")[-1]
    grpc_port = registry[service_name]["grpc"]
    subprocess.Popen(
        [sys.executable, "-m", service_module, "--grpc-port", str(grpc_port)],
        cwd=str(cwd))


def start_snetd(cwd):
    """
    Starts the Daemon 'snetd'
    """
    try:
        cmd = ["snetd", "serve"]
        subprocess.Popen(cmd, cwd=str(cwd))
    except Exception as e:
        log.error(e)
        print(e)
        exit(1)
    return True


if __name__ == "__main__":
    main()
