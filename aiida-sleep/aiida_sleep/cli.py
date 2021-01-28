# -*- coding: utf-8 -*-
from aiida.cmdline.utils.decorators import with_dbenv
import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main():
    """The command line interface for aiida-sleep."""


@main.command("calc")
@click.option(
    "-n", "--number", type=int, default=1, help="The number of calculations to launch."
)
@click.option("-c", "--code", default="sleep@slurm", help="The code to run.")
@click.option("-t", "--time", type=int, default=1, help="The time to sleep (seconds).")
@click.option(
    "-p",
    "--payload",
    type=int,
    default=100,
    help="The number of attributes for the input payload.",
)
@click.option(
    "-o",
    "--output-dict",
    type=int,
    default=100,
    help="The number of attributes for the output Dict.",
)
@click.option(
    "-a",
    "--output-array",
    type=int,
    default=100,
    help="The size of the numpy array for the output ArrayData.",
)
@click.option(
    "-f",
    "--fail",
    is_flag=True,
    help="Parse the calculation with a non-zero exit code.",
)
@click.option("-s", "--submit", is_flag=True, help="Submit the calculation (or run).")
@with_dbenv()
def run_calcs_cli(number, code, time, payload, fail, output_dict, output_array, submit):
    """Run the `SleepCalculation`"""
    for i in range(number):
        print(
            f"setting up and {'submitting' if submit else 'running'} calculation {i+1}"
        )
        node = run_calc(
            code=code,
            time=time,
            payload=payload,
            output_dict=output_dict,
            output_array=output_array,
            fail=fail,
            submit=submit,
        )
        click.echo(str(node))


def run_calc(
    code="sleep@slurm",
    time=1,
    payload=100,
    output_dict=100,
    output_array=100,
    fail=False,
    submit=False,
):
    """Run the `SleepCalculation`

    :param code: code label
    :param time: time the `SleepCalculation` runs sleep for (seconds)
    :param payload: Size of input dict
    :param output_dict: Size of output dict
    :param output_array: Size of output array
    :param fail: Intentionally  fail the `SleepCalculation`
    :param submit: whether to submit to daemon, otherwise run
    :return: workchain node
    """
    from aiida.engine import run_get_node
    from aiida.engine import submit as submit_func
    from aiida.orm import load_code

    builder = load_code(code).get_builder()
    builder.time = time
    builder.payload = {f"input_key_{i}": f"value_{i}" for i in range(payload)}
    builder.metadata.options.fail_calcjob = fail
    builder.metadata.options.output_dict_size = output_dict
    builder.metadata.options.output_array_size = output_array

    if submit:
        node = submit_func(builder)
    else:
        node = run_get_node(builder).node

    return node


@main.command("workchain")
@click.option(
    "-nw",
    "--number-work",
    type=int,
    default=1,
    help="The number of workchains to launch.",
)
@click.option(
    "-nc",
    "--number-calc",
    type=int,
    default=1,
    help="The number of calculations per workchain.",
)
@click.option("-c", "--code", default="sleep@slurm", help="The code to run.")
@click.option("-t", "--time", type=int, default=1, help="The time to sleep (seconds).")
@click.option(
    "-p",
    "--payload",
    type=int,
    default=100,
    help="The number of attributes for the input payload.",
)
@click.option(
    "-o",
    "--output-dict",
    type=int,
    default=100,
    help="The number of attributes for the output Dict.",
)
@click.option(
    "-a",
    "--output-array",
    type=int,
    default=100,
    help="The number of rows for the output ArrayData.",
)
@click.option(
    "-f", "--fail", is_flag=True, help="Parse calculations with a non-zero exit code."
)
@click.option("-s", "--submit", is_flag=True, help="Submit the workchain (or run).")
@with_dbenv()
def run_workchains_cli(
    number_work,
    number_calc,
    code,
    time,
    payload,
    output_dict,
    output_array,
    fail,
    submit,
):
    """Run the `SleepWorkChain`"""
    for i in range(number_work):
        print(f"setting up and {'submitting' if submit else 'running'} workchain {i+1}")
        node = run_workchain(
            number=number_calc,
            code=code,
            time=time,
            payload=payload,
            output_dict=output_dict,
            output_array=output_array,
            fail=fail,
            submit=submit,
        )
        click.echo(str(node))


def run_workchain(
    number=1,
    code="sleep@slurm",
    time=1,
    payload=100,
    output_dict=100,
    output_array=100,
    fail=False,
    submit=False,
):
    """Run the `SleepWorkChain`

    :param number: Number of children `SleepCalculation`
    :param code: code label
    :param time: time each `SleepCalculation` runs sleep for (seconds)
    :param payload: Size of input dict
    :param output_dict: Size of output dict
    :param output_array: Size of output array
    :param fail: Intentionally  fail all `SleepCalculation`
    :param submit: whether to submit to daemon, otherwise run
    :return: workchain node
    """
    from aiida.engine import run_get_node
    from aiida.engine import submit as submit_func
    from aiida.orm import load_code
    from aiida.plugins import WorkflowFactory

    builder = WorkflowFactory("sleep").get_builder()
    builder.children = number
    builder.calcjob.code = load_code(code)
    builder.calcjob.time = time
    builder.calcjob.payload = {f"input_key_{i}": f"value_{i}" for i in range(payload)}
    builder.calcjob.metadata.options.fail_calcjob = fail
    builder.calcjob.metadata.options.output_dict_size = output_dict
    builder.calcjob.metadata.options.output_array_size = output_array

    if submit:
        node = submit_func(builder)
    else:
        node = run_get_node(builder).node

    return node
