import os
import sys
import click
import subprocess

from easy_smr.config.config import ConfigManager

def _config(app_name):
    config_file_path = os.path.join(f'{app_name}.json')
    if not os.path.isfile(config_file_path):
        raise ValueError("This is not a easy_smr directory: {}".format(os.getcwd()))
    else:
        return ConfigManager(config_file_path).get_config()


@click.group()
def local():
    """
    Commands for local operations: train and deploy
    """
    pass


@click.command()
@click.option(
    u"-a",
    u"--app-name",
    required=True,
    help="The app name whose json file will be referenced for setting up command"
)
@click.pass_obj
def train(obj, app_name):
    """
    Command to train ML model(s) locally
    """
    print("Started local training...\n")
    config = _config(app_name)
    dir = config.easy_smr_module_dir
    docker_tag = obj['docker_tag']
    image_name = config.image_name
    easy_smr_module_path = os.path.join(dir, 'easy_smr_base')
    local_train_script_path = os.path.join(easy_smr_module_path, 'local_test', 'train_local.sh')
    test_path = os.path.join(easy_smr_module_path, 'local_test', 'test_dir')

    if not os.path.isdir(test_path):
        raise ValueError("This is not a easy_smr directory: {}".format(dir))

    try:
        output = subprocess.check_output(
                [
                    "{}".format(local_train_script_path),
                    "{}".format(os.path.abspath(test_path)),
                    docker_tag,
                    image_name
                ],
        stderr=subprocess.STDOUT,  # Merge stderr into stdout
        text=True  # Return output as a string instead of bytes
        )

        print("Local training completed successfully!")

    except subprocess.CalledProcessError as e:
        # Surface the error
        print("Error occurred while running the command:")
        print(f"Return code: {e.returncode}")
        print(f"Command: {e.cmd}")
        print("Error output:")
        print(e.output)  # This contains both stdout and stderr


@click.command()
@click.option(
    u"-f",
    u"--file",
    required=True,
    help="The name (not path) of R file to run as processing job"
)
@click.option(
    u"-a",
    u"--app-name",
    required=True,
    help="The app name whose json file will be referenced for setting up command"
)
@click.pass_obj
def process(obj, file, app_name):
    """
    Command to run R files locally as processing job
    """
    print("Started local processing job...\n")
    config = _config(app_name)
    dir = config.easy_smr_module_dir
    docker_tag = obj['docker_tag']
    image_name = config.image_name
    aws_profile = config.aws_profile
    aws_region = config.aws_region
    easy_smr_module_path = os.path.join(dir, 'easy_smr_base')
    local_process_script_path = os.path.join(easy_smr_module_path, 'local_test', 'process_local.sh')
    test_path = os.path.join(easy_smr_module_path, 'local_test', 'test_dir')
    job_file_path = os.path.join(easy_smr_module_path, 'processing', file)

    if not os.path.isdir(test_path):
        raise ValueError("This is not a easy_smr directory: {}".format(dir))

    if not os.path.isfile(job_file_path):
        raise ValueError("Processing file does not exist: {}".format(job_file_path))

    try:
        output = subprocess.check_output(
        [
            "{}".format(local_process_script_path),
            "{}".format(os.path.abspath(test_path)),
            docker_tag,
            image_name,
            file,
            aws_profile,
            aws_region
        ],
        stderr=subprocess.STDOUT,  # Merge stderr into stdout
        text=True  # Return output as a string instead of bytes
        )
        print("Local processing completed successfully!")
    except subprocess.CalledProcessError as e:
        # Surface the error
        print("Error occurred while running the command:")
        print(f"Return code: {e.returncode}")
        print(f"Command: {e.cmd}")
        print("Error output:")
        print(e.output)  # This contains both stdout and stderr

@click.command()
@click.option(
    u"-a",
    u"--app-name",
    required=True,
    help="The app name whose json file will be referenced for setting up command"
)
@click.pass_obj
def deploy(obj, app_name):
    """
    Command to deploy ML model(s) locally
    """

    config = _config(app_name)
    dir = config.easy_smr_module_dir
    docker_tag = obj['docker_tag']
    image_name = config.image_name

    easy_smr_module_path = os.path.join(dir, 'easy_smr_base')
    local_deploy_script_path = os.path.join(easy_smr_module_path, 'local_test', 'deploy_local.sh')
    test_path = os.path.join(easy_smr_module_path, 'local_test', 'test_dir')

    if not os.path.isdir(test_path):
        raise ValueError("This is not a easy_smr directory: {}".format(dir))

    try:
        print("Started local deployment at localhost:8080 ...\n")
        output = subprocess.check_output(
            [
                "{}".format(local_deploy_script_path),
                "{}".format(os.path.abspath(test_path)),
                docker_tag,
                image_name
            ],
        stderr=subprocess.STDOUT,  # Merge stderr into stdout
        text=True  # Return output as a string instead of bytes
        )

    except subprocess.CalledProcessError as e:
        # Surface the error
        print("Error occurred while running the command:")
        print(f"Return code: {e.returncode}")
        print(f"Command: {e.cmd}")
        print("Error output:")
        print(e.output)  # This contains both stdout and stderr


@click.command()
@click.option(
    u"-t",
    u"--target",
    required=True,
    help="The name of target that needs to be built"
)
@click.option(
    u"-a",
    u"--app-name",
    required=True,
    help="The app name whose json file will be referenced for setting up command"
)
@click.pass_obj
def make(obj, target, app_name):
    """
    Command to build make targets defined in a Makefile in easy_smr_base/processing
    """
    config = _config(app_name)
    dir = config.easy_smr_module_dir
    docker_tag = obj['docker_tag']
    image_name = config.image_name
    aws_profile = config.aws_profile
    aws_region = config.aws_region
    easy_smr_module_path = os.path.join(dir, 'easy_smr_base')
    local_make_script_path = os.path.join(easy_smr_module_path, 'local_test', 'make_local.sh')
    test_path = os.path.join(easy_smr_module_path, 'local_test', 'test_dir')
    makefile_path = os.path.join(easy_smr_module_path, 'processing', 'Makefile')

    if not os.path.isdir(test_path):
        raise ValueError("This is not a easy_smr directory: {}".format(dir))

    if not os.path.isfile(makefile_path):
        raise ValueError("Makefile does not exist: {}".format(makefile_path))

    try:
        output = subprocess.check_output(
            [
                "{}".format(local_make_script_path),
                "{}".format(os.path.abspath(test_path)),
                docker_tag,
                image_name,
                target,
                aws_profile,
                aws_region
            ],
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True  # Return output as a string instead of bytes
        )
        print(f"{target} built successfully!")

    except subprocess.CalledProcessError as e:
        # Surface the error
        print("Error occurred while running the command:")
        print(f"Return code: {e.returncode}")
        print(f"Command: {e.cmd}")
        print("Error output:")
        print(e.output)  # This contains both stdout and stderr


local.add_command(train)
local.add_command(deploy)
local.add_command(process)
local.add_command(make)
