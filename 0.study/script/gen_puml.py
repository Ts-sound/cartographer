#!/usr/bin/env python3

## python3.11

import argparse, os, glob, json, platform, logging
from pathlib import Path

# logging.basicConfig(level=logging.DEBUG ,format="[%(levelname)-s|%(asctime)s|%(filename)s] %(funcName)s:%(lineno)d %(message)s")
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s|%(filename)s] [%(funcName)s:%(lineno)d] %(message)s",
)


workpath = str(Path(__file__).resolve().parent.parent.parent)
logging.debug(f"workpath: {workpath}")


g_plantuml_jar=workpath +'/0.study/assets/plantuml-1.2025.4.jar'


def gen_puml(input_files, output_file):
    """
    Generate PlantUML file from C++ header file.
    """
    logging.debug(f"input_files: {input_files}")
    logging.debug(f"output_file: {output_file}")

    cmd = "hpp2plantuml "
    for i in input_files:
        cmd += f" -i {i} "
    cmd += f" -o {output_file} "

    logging.debug(f"cmd: {cmd}")
    ret = os.system(cmd)
    
    cmd = 'java -jar '+g_plantuml_jar+' -tsvg -o '+str(Path(output_file).resolve().parent)+'  ' +output_file
    logging.debug(f"cmd: {cmd}")
    ret |= os.system(cmd)

    if ret != 0:
        logging.error(f"Command failed with return code {ret}.")
        return False
    logging.debug(f"Command executed successfully.")

    return True


def handle_common():
    """
    Handle the common case.
    """
    common_path = os.path.join(workpath, "cartographer", "common")
    common_out_path = os.path.join(
        workpath, "0.study", "cartographer", "assets", "puml", "common"
    )
    os.makedirs(common_out_path, exist_ok=True)

    # gen blocking_queue.puml
    input_files = glob.glob(os.path.join(common_path, "internal", "*_queue.h"))
    output_file = common_out_path +"/blocking_queue.puml"
    gen_puml(input_files, output_file)
    
    # gen file_resolver.puml
    input_files = glob.glob(os.path.join(common_path, "*file_resolver.h"))
    input_files += glob.glob(os.path.join(common_path, "lua_parameter_dictionary.h"))
    output_file = common_out_path +"/file_resolver.puml"
    gen_puml(input_files, output_file)
    
    # gen thread_pool.puml
    input_files = glob.glob(os.path.join(common_path, "thread_pool.h"))
    input_files += glob.glob(os.path.join(common_path, "task.h"))
    output_file = common_out_path +"/thread_pool.puml"
    gen_puml(input_files, output_file)


def handle_metrics():
    """
    Handle the metrics case.
    """
    metrics_path = os.path.join(workpath, "cartographer", "metrics")
    metrics_out_path = os.path.join(
        workpath, "0.study", "cartographer", "assets", "puml", "metrics"
    )
    os.makedirs(metrics_out_path, exist_ok=True)
    
    # gen metrics.puml
    input_files = glob.glob(os.path.join(metrics_path, "*.h"))
    input_files += glob.glob(os.path.join(workpath, "cartographer", "cloud", "metrics","prometheus", "family_factory.*"))
    output_file = metrics_out_path +"/metrics.puml"
    gen_puml(input_files, output_file)


def handle_sensor():
    """
    Handle the sensor case.
    """
    sensor_path = os.path.join(workpath, "cartographer", "sensor")
    sensor_out_path = os.path.join(
        workpath, "0.study", "cartographer", "assets", "puml", "sensor"
    )
    os.makedirs(sensor_out_path, exist_ok=True)
    
    # gen sensor.puml
    input_files = glob.glob(os.path.join(sensor_path, "*.h"),recursive=True)
    output_file = sensor_out_path +"/sensor.puml"
    gen_puml(input_files, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="gen puml from cpp header file")
    parser.add_argument("--common", help="", type=bool, default=False)
    parser.add_argument("--metrics", help="", type=bool, default=False)
    parser.add_argument("--sensor", help="", type=bool, default=False)

    if parser.parse_args().common:
        handle_common()
    elif parser.parse_args().metrics:
        handle_metrics()
    elif parser.parse_args().sensor:
        handle_sensor()


# hpp2plantuml -i  ../../cartographer/common/internal/blocking_queue.h -o common.puml
