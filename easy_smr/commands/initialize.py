import os
import sys

import boto3
import click
from click import BadParameter
import os
from pathlib import Path
from easy_sm.config.config import ConfigManager
from distutils.dir_util import copy_tree

_FILE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def _template_creation(app_name, aws_profile, aws_region, output_dir, renv_dir):
    easy_sm_module_name = 'easy_sm_base'

    easy_sm_exists = os.path.exists(os.path.join(output_dir, easy_sm_module_name))
    if easy_sm_exists:
        raise ValueError(
            "There is a easy_sm directory/module already. "
            "Please, rename it in order to use easy_sm."
        )

    Path(output_dir).mkdir(exist_ok=True)
    Path(os.path.join(output_dir, '__init__.py')).touch()

    # Set 'easy_sm module' directory up
    copy_tree(os.path.join(_FILE_DIR_PATH, '../template'), output_dir)

    # Set configuration file up
    config_manager = ConfigManager(os.path.join(f"{app_name}.json"))
    config = config_manager.get_config()

    config.image_name = app_name
    config.aws_region = aws_region
    config.aws_profile = aws_profile
    config.easy_sm_module_dir = output_dir
    config.renv_dir = renv_dir
    config_manager.set_config(config)


def _get_local_aws_profiles():
    return boto3.Session().available_profiles


def ask_for_app_name():
    return click.prompt(
        text="Type in a name for your SageMaker app (Only alphanumeric characters and - are allowed))",
        type=str
    )


def ask_if_existing_project_exists():
    return click.confirm(text="Are you starting a new project?")


def ask_for_root_dir():
    return click.prompt(text="Type in the directory where your code lives. Example: src", type=str).strip('/')


def ask_for_aws_details():
    available_profiles = _get_local_aws_profiles()

    if len(available_profiles) == 0:
        print("aws cli is not configured!")
        return

    valid_positions = list(range(1, len(available_profiles) + 1))
    print("Select AWS profile:")
    print('{}'.format(
            '\n'.join(
                [
                    '{} - {}'.format(pos, profile)
                    for pos, profile in zip(valid_positions, available_profiles)
                ]
            )
        )
    )

    def _validate_profile_position(input_pos):
        if int(input_pos) not in valid_positions:
            raise BadParameter(
                message="invalid choice: {}. (choose from {})".format(
                    input_pos,
                    ', '.join([str(pos) for pos in valid_positions])
                )
            )
        return int(input_pos)

    chosen_profile_index = click.prompt(
        text="Choose from {}".format(', '.join([str(pos) for pos in valid_positions])),
        default=1,
        value_proc=lambda x: _validate_profile_position(x)
    )
    chosen_profile_index -= 1

    chosen_profile = available_profiles[chosen_profile_index]

    chosen_region = click.prompt(
        text="Type in your preferred AWS region name",
        default='eu-west-1',
        type=str
    )

    return chosen_profile, chosen_region


def ask_for_renv_dir():
    return click.prompt(text="Type in the path to renv directory", type=str).strip('/')


@click.command()
def init():
    """
    Command to initialize SageMaker template
    """

    easy_sm_app_name = ask_for_app_name()

    is_new_project = ask_if_existing_project_exists()

    root_dir = None
    if not is_new_project:
        root_dir = ask_for_root_dir()

    aws_profile, aws_region = ask_for_aws_details()

    renv_dir = ask_for_renv_dir()
    _template_creation(
        app_name=easy_sm_app_name,
        aws_profile=aws_profile,
        aws_region=aws_region,
        output_dir=root_dir if root_dir else easy_sm_app_name,
        requirements_dir=renv_dir
    )

    print("\neasy_sm module is created! ヽ(´▽`)/")
