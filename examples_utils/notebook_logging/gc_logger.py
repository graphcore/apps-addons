# Copyright (c) 2023 Graphcore Ltd. All rights reserved.

import base64
import boto3
import hashlib
import ipynbname
import json
import os
import pkg_resources
import time
import multiprocessing as mp
import nbformat

from datetime import datetime
from pathlib import Path


class GCLogger(object):
    """Tracks the times at which cells are executed"""

    _instance = None
    _CREATION_TIME = datetime.now()

    LOG_STATE = None
    _TIER_TYPE = os.getenv("TIER_TYPE", "UNKNOWN")

    _POLLING_SECONDS = 10

    _MP_MANAGER = mp.Manager()
    _PAYLOAD = _MP_MANAGER.dict()
    _CODE_CELLS = _MP_MANAGER.list()

    _PROC_LIST = []

    _FIREHOSE_STREAM_NAME = os.getenv("FIREHOSE_STREAM_NAME", "paperspacenotebook_production")
    _REGION = "eu-west-1"

    _FRAMEWORKS = [
        "poptorch",
        "torch",
        "transformers",
        "tensorflow",
        "poptorch-geometric",
    ]

    _COLUMN_TYPES = {
        # Timing data
        "event_time": "",
        "execution_start_time": "",
        "execution_end_time": "",
        "time_to_first_error_seconds": 0,
        "compile_time_seconds": 0,
        # Event metadata
        "event_type": "",
        "user_onetime_id": "",
        "manual_logging_termination_event": 0,
        "manual_cell_termination_event": 0,
        # Largely constant values
        "notebook_path": "",
        "notebook_name": "",
        "notebook_repo_id": "",
        "notebook_id": "",
        "cluster_id": "",
        "repo_framework": "",
        # Cell input/output information
        "error_trace": "",
        "cell_output": "",
        "code_executed": "",
        "cell_code_modified": 0,
        # Major framework versions from env
        "poptorch_version_major": 0,
        "poptorch_version_minor": 0,
        "poptorch_version_patch": "",
        "torch_version_major": 0,
        "torch_version_minor": 0,
        "torch_version_patch": "",
        "transformers_version_major": 0,
        "transformers_version_minor": 0,
        "transformers_version_patch": "",
        "tensorflow_version_major": 0,
        "tensorflow_version_minor": 0,
        "tensorflow_version_patch": "",
        "popgeometric_version_major": 0,
        "popgeometric_version_minor": 0,
        "popgeometric_version_patch": "",
    }

    _HF_KEY_LENGTH = 37

    def __new__(cls, ip):
        if cls._instance is None:
            cls._SHELL = ip
            cls._instance = super(GCLogger, cls).__new__(cls)

            if cls.LOG_STATE is None and cls._TIER_TYPE == "FREE":
                cls.LOG_STATE = "ENABLED"

                try:
                    # Get AWS keys for firehose
                    config_file = Path(os.getenv("GCLOGGER_CONFIG"), ".config").resolve()
                    with open(config_file, "r") as file:
                        aws_access_key = base64.b64decode(file.readline().encode("ascii")).decode("ascii").strip()
                        aws_secret_key = base64.b64decode(file.readline().encode("ascii")).decode("ascii").strip()

                    cls._FIREHOSE_CLIENT = boto3.client(
                        "firehose",
                        aws_access_key_id=aws_access_key[:2] + aws_access_key[3:],
                        aws_secret_access_key=aws_secret_key[:2] + aws_secret_key[3:],
                        region_name=cls._REGION,
                    )

                    # Inform user
                    print(
                        "\n============================================================================================================================================\n"
                        "Graphcore would like to collect information about the applications and code being run in this notebook, as well as the system it's being run \n"
                        "on to improve usability and support for future users. The information will be anonymised and sent to Graphcore \n\n"
                        "You can disable this at any time by running `%unload_ext gc_logger` from any cell.\n\n"
                        "Unless logging is disabled, the following information will be collected:\n"
                        "\t- User progression through the notebook\n"
                        "\t- Notebook details: number of cells, code being run and the output of the cells\n"
                        "\t- ML application details: Model information, performance, hyperparameters, and compilation time\n"
                        "\t- Environment details\n"
                        "\t- System performance: IO, memory and host compute performance\n\n"
                        "=============================================================================================================================================\n"
                    )

                except:
                    cls.LOG_STATE = "DISABLED"
                    return cls._instance

                # Prepare shared dict and populate with Nulls in schema format
                cls._PAYLOAD.update(cls._COLUMN_TYPES)

                # Create a short unique user ID
                cls._UNIQUE_HASH = base64.urlsafe_b64encode(
                    hashlib.md5(cls._CREATION_TIME.strftime("%Y-%m-%d %H:%M:%S.%f").encode("utf-8")).digest()
                ).decode("ascii")[:12]
                cls._PAYLOAD["user_onetime_id"] = cls._UNIQUE_HASH

                # Convert data collection into repeated polling with update checking
                background_functions = [
                    cls.__get_notebook_metadata,
                    cls.__get_frameworks_versions,
                    cls.__manual_termination_polling,
                    cls.__store_initial_cell_states,
                ]

                # Start multiprocess procs for all functions
                cls._PROC_LIST = [mp.Process(target=func) for func in background_functions]
                for proc in cls._PROC_LIST:
                    proc.daemon = True
                    proc.start()

            else:
                cls.LOG_STATE = "DISABLED"

        return cls._instance

    def __init__(self, ip):
        return

    @classmethod
    def __update_payload(cls, output: str or int, name: str) -> str:
        """Update the payload with empty types as backups."""

        if cls.LOG_STATE == "DISABLED":
            return

        if output:
            cls._PAYLOAD[name] = output
        else:
            empty_output_type = type(output)
            cls._PAYLOAD[name] = empty_output_type()

    @classmethod
    def __store_initial_cell_states(cls):
        """store the initial state of all cells in notebook."""

        if cls.LOG_STATE == "DISABLED":
            return

        try:
            with open(ipynbname.path()) as notebook:
                initial_state = nbformat.read(notebook, nbformat.NO_CONVERT)

            # Get list of all code cells
            for cell in initial_state["cells"]:
                if cell["cell_type"] == "code":
                    cls._CODE_CELLS.append(cell["source"])

        except:
            pass

    @classmethod
    def __manual_termination_polling(cls):
        """Report if exeuction termination event was some kill signal."""

        try:
            while True:
                time.sleep(cls._POLLING_SECONDS)
        except:
            cls.__update_payload(1, "manual_cell_termination_event")

    @classmethod
    def __get_notebook_metadata(cls):
        """Get notebook metadata."""

        if cls.LOG_STATE == "DISABLED":
            return

        try:
            try:
                notebook_path = ipynbname.path()
            except:
                notebook_path = "failed-to-get-nb-path"

            # Encode and hash
            notebook_id = os.getenv("PAPERSPACE_NOTEBOOK_ID")
            salted_id = notebook_id + datetime.now().strftime("%Y-%m-%d")
            anonymised_notebook_id = base64.urlsafe_b64encode(hashlib.md5(salted_id.encode("utf-8")).digest()).decode(
                "ascii"
            )[:16]

            notebook_metadata = {
                "notebook_path": str(notebook_path),
                "notebook_name": str(notebook_path.stem),
                "notebook_repo_id": os.getenv("PAPERSPACE_NOTEBOOK_REPO_ID"),
                "notebook_id": anonymised_notebook_id,
                "cluster_id": os.getenv("PAPERSPACE_CLUSTER_ID"),
                "repo_framework": os.getenv("REPO_FRAMEWORK"),
            }

            for key, val in notebook_metadata.items():
                cls.__update_payload(val, key)

        except:
            pass

    @classmethod
    def __get_frameworks_versions(cls) -> str:
        """Get framework versions."""

        if cls.LOG_STATE == "DISABLED":
            return

        try:
            try:
                installed_packages = pkg_resources.working_set
            except:
                installed_packages = {}

            # Query pip packages and versions for frameworks
            all_pkgs = {i.key: i.version for i in installed_packages}
            for fw in cls._FRAMEWORKS:
                version = all_pkgs.get(fw, "..").split(".")

                if fw == "poptorch-geometric":
                    fw = "popgeometric"

                cls.__update_payload(int(version[0]) if version[0] else 0, f"{fw}_version_major")
                cls.__update_payload(int(version[1]) if version[0] else 0, f"{fw}_version_minor")
                cls.__update_payload(version[2], f"{fw}_version_patch")

        except:
            pass

    @classmethod
    def __convert_time_from_string(cls, raw_string_time: str) -> int:
        """Convert times from MM:SS string format to integer seconds"""

        minutes = int(raw_string_time[:2])
        seconds = int(raw_string_time[3:])

        return (minutes * 60) + seconds

    @classmethod
    def __get_compile_time(cls, cell_input: str, cell_output: str) -> int:
        """Capture compile time from a cells inputs/outputs."""

        if cls.LOG_STATE == "DISABLED":
            return

        # Whether any compil/e/ation happened or not
        if not "compil" in cell_input + cell_output:
            # Covers most HF, PyG and Pytorch cases
            if "Graph compilation: 100%" in cell_output:
                start_index = cell_output.find("Graph compilation: 100%")
                end_index = cell_output.find("00:00]")
                compile_time_raw = cell_output[start_index:end_index][-6:-1]
                compile_time = cls.__convert_time_from_string(compile_time_raw)
            else:
                compile_time = 0

        return compile_time

    @classmethod
    def __detect_logging_termination(cls, cell_input: str) -> int:
        """Detect if GCL logging was terminated by user"""

        if cls.LOG_STATE == "DISABLED":
            return

        if "unload_ext gc_logger" in cell_input:
            return 1
        else:
            return 0

    @classmethod
    def __detect_cell_modification(cls, executed_code):
        """Detect if the cell code has been modified before execution."""

        if cls.LOG_STATE == "DISABLED":
            return

        if cls._CODE_CELLS == []:
            return 0

        try:
            if executed_code in cls._CODE_CELLS:
                return 0
            else:
                return 1
        except:
            pass

        return 0

    def __remove_hf_keys(cls, raw_string: str) -> str:
        """Detect and remove possible HF API keys from strings."""

        if cls.LOG_STATE == "DISABLED":
            return

        while "hf_" in raw_string:
            key_start = raw_string.find("hf_")
            key_end = key_start + cls._HF_KEY_LENGTH
            raw_string = raw_string[:key_start] + "<HF_API_KEY>" + raw_string[key_end:]

        return raw_string

    @classmethod
    def __sanitize_payload(cls, payload):

        if cls.LOG_STATE == "DISABLED":
            return

        # Clean out any private keys, fix quotes
        for key, val in payload.items():
            if type(val) == str:
                if key in ["error_trace", "cell_output", "code_executed"]:
                    val = cls.__remove_hf_keys(val)

                payload[key] = val.replace('"', "'")

        payload = json.dumps(payload, separators=(",", ":"))
        payload = payload.encode("utf-8")

        return payload

    @classmethod
    def __firehose_put(cls, payload):
        """Submit a PUT record request to the firehose stream."""

        if cls.LOG_STATE == "DISABLED":
            return

        payload["event_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        clean_payload = cls.__sanitize_payload(payload)

        cls._FIREHOSE_CLIENT.put_record(
            DeliveryStreamName=cls._FIREHOSE_STREAM_NAME,
            Record={"Data": clean_payload},
        )

    @classmethod
    def pre_run_cell(cls, info):
        """Runs just before any cell is run."""

        if cls.LOG_STATE == "DISABLED":
            return

        cls._PAYLOAD["execution_start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    @classmethod
    def post_run_cell(cls, result):
        """Runs just after any cell is run."""

        if cls.LOG_STATE == "DISABLED":
            return

        event_dict = cls._PAYLOAD._getvalue()

        # Common values to all events
        event_dict["execution_end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        event_dict["code_executed"] = str(result.info.raw_cell)
        event_dict["cell_output"] = str(result.result)

        # Get compile time if available
        event_dict["compile_time_seconds"] = cls.__get_compile_time(
            event_dict["code_executed"],
            event_dict["cell_output"],
        )

        # Detect if this cell is new or has been modified from its initial state
        # TODO: Once we upgrade to newer IPython, we can distinguish these two
        event_dict["cell_code_modified"] = cls.__detect_cell_modification(result.info.raw_cell)

        if result.error_before_exec or result.error_in_exec:
            # Only get this value once
            if cls._PAYLOAD["time_to_first_error_seconds"] == 0:
                cls._PAYLOAD["time_to_first_error_seconds"] = int((datetime.now() - cls._CREATION_TIME).total_seconds())

            event_dict["event_type"] = "error"
            event_dict["error_trace"] = (
                str(result.error_before_exec) if result.error_before_exec else str(result.error_in_exec)
            )
        else:
            event_dict["event_type"] = "success"
            event_dict["error_trace"] = ""

        event_dict["manual_logging_termination_event"] = cls.__detect_logging_termination(result.info.raw_cell)

        cls.__firehose_put(event_dict)


def load_ipython_extension(ip):
    global _gc_logger
    _gc_logger = GCLogger(ip)
    ip.events.register("pre_run_cell", _gc_logger.pre_run_cell)
    ip.events.register("post_run_cell", _gc_logger.post_run_cell)


def unload_ipython_extension(ip):
    global _gc_logger
    _gc_logger.LOG_STATE = "DISABLED"
    del _gc_logger
