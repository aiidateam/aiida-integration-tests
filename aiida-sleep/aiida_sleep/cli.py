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
    default=1,
    help="The number of attributes for the payload.",
)
@click.option(
    "-f",
    "--fail",
    is_flag=True,
    help="Parse the calculation with a non-zero exit code.",
)
@click.option("-s", "--submit", is_flag=True, help="Submit the calculation (or run).")
@with_dbenv()
def run_calcs_cli(number, code, time, payload, fail, submit):
    """Run the `SleepCalculation`"""
    for _ in range(number):
        node = run_calc(code, time, payload, fail, submit)
        click.echo(str(node))


def run_calc(code="sleep@slurm", time=1, payload=1, fail=False, submit=False):
    """Run the `SleepCalculation`"""
    from aiida.engine import run_get_node, submit as submit_func
    from aiida.orm import load_code

    builder = load_code(code).get_builder()
    builder.time = time
    builder.fail = fail
    builder.payload = {f"key_{i}": f"value_{i}" for i in range(payload)}

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
    default=1,
    help="The number of attributes for the payload.",
)
@click.option(
    "-f", "--fail", is_flag=True, help="Parse calculations with a non-zero exit code."
)
@click.option("-s", "--submit", is_flag=True, help="Submit the workchain (or run).")
@with_dbenv()
def run_workchains_cli(number_work, number_calc, code, time, payload, fail, submit):
    """Run the `SleepWorkChain`"""
    for _ in range(number_work):
        node = run_workchain(number_calc, code, time, payload, fail, submit)
        click.echo(str(node))


def run_workchain(
    number=1, code="sleep@slurm", time=1, payload=1, fail=False, submit=False
):
    """Run the `SleepWorkChain`"""
    from aiida.engine import run_get_node, submit as submit_func
    from aiida.orm import load_code
    from aiida.plugins import WorkflowFactory

    builder = WorkflowFactory("sleep").get_builder()
    builder.children = number
    builder.calcjob.code = load_code(code)
    builder.calcjob.time = time
    builder.calcjob.payload = {f"key_{i}": f"value_{i}" for i in range(payload)}
    builder.calcjob.fail = fail

    if submit:
        node = submit_func(builder)
    else:
        node = run_get_node(builder).node

    return node
