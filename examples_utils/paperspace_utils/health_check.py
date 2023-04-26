# Copyright (c) 2023 Graphcore Ltd. All rights reserved.
from datetime import datetime
import json
import os
import yaml
import logging
import pathlib
from metadata_utils import check_files_match_metadata
from pathlib import Path
from time import time

"""
Checks status of a list of datasets in a directory
Looks for a metadata.json file in each dataset and checks files match what is expected from the metadata file
Returns dictionary of logging information on the status of the datasets
"""


def check_datasets_exist(dataset_names: [str], dirname: str):
    dirpath = Path(dirname)
    output_dict = {}
    if not dirpath.exists():
        warn = f"Directory {dirname} does not exist"
        logging.warning(warn)
        return {"warning": warn}
    else:
        logging.info("Directory " + dirname + " exists")
    for dataset_name in dataset_names:
        full_path = dirpath / dataset_name
        if not full_path.exists():
            logging.warning(dataset_name + " not found in " + dirname)
            output_dict[dataset_name] = {
                "warning": dataset_name + " dataset not mounted, " + dataset_name + " directory not found in " + dirname
            }
        else:
            if (full_path / "gradient_dataset_metadata.json").exists():
                logging.info("Metadata found in " + str(full_path))
                output_dict[dataset_name] = check_files_match_metadata(full_path, False)
            else:
                logging.warning("Metadata file not found in " + str(full_path))
                output_dict[dataset_name] = {"warning": "Metadata file not found in " + str(full_path)}
    return output_dict


"""
Logs whether path exists and returns dict of logging information
"""


def check_paths_exists(paths: [str]):
    symlinks_exist = []
    for path in paths:
        if Path(path).exists():
            logging.info("Folder exists: " + path)
            symlinks_exist.append({path: True})
        else:
            logging.warning("Folder does not exist " + path)
            symlinks_exist.append({path: False})
    return symlinks_exist


def main():
    notebook_id = os.environ.get("PAPERSPACE_METRIC_WORKLOAD_ID", "")
    # Check that graphcore_health_checks folder exists
    health_check_dir = pathlib.Path("/storage/graphcore_health_checks")
    health_check_dir.mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logging.info("Running health check")
    logging.info("Checking datasets mounted")
    # Check that the datasets have mounted as expected
    # Gather the datasets expected from the settings.yaml
    with open("/.gradient/settings.yaml") as f:
        my_dict = yaml.safe_load(f)
        datasets = my_dict["integrations"].keys()

    # Check that dataset exists and if a metadata file is found check that all files in the metadata file exist
    datasets_mounted = check_datasets_exist(datasets, "/datasets")

    # Check that the folders specified in the key of the symlink_config.json exist
    logging.info("Checking symlink folders exist")
    with open("symlink_config.json") as f:
        symlinks = json.load(f)
        new_folders = list(map(os.path.expandvars, symlinks.keys()))
    symlinks_exist = check_paths_exists(new_folders)

    output_json_dict = {"mounted_datasets": datasets_mounted, "symlinks_exist": symlinks_exist}

    (
        health_check_dir / (datetime.fromtimestamp(time()).strftime("%Y-%m-%d-%H.%M.%S") + "_" + notebook_id + ".json")
    ).write_text(json.dumps(output_json_dict, indent=4))


if __name__ == "__main__":
    main()
