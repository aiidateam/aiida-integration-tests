# -*- coding: utf-8 -*-
"""`CalcJob` implementation to add two numbers using bash for testing and demonstration purposes."""
from aiida import orm
from aiida.common import json
from aiida.common.datastructures import CalcInfo, CodeInfo
from aiida.common.folders import Folder
from aiida.engine import CalcJob, CalcJobProcessSpec, WorkChain
from aiida.orm.nodes.data.base import to_aiida_type
from aiida.parsers.parser import Parser


def _time_validator(value, port):
    if value < 0:
        return "time must be >= 0"
    return None


class SleepCalculation(CalcJob):
    """`CalcJob` implementation which sleeps for a set time the echo's 'success'."""

    @classmethod
    def define(cls, spec: CalcJobProcessSpec):
        """Define the process specification, including its inputs, outputs and known exit codes.

        :param spec: the calculation job process spec to define.
        """
        super().define(spec)
        spec.input(
            "time",
            serializer=to_aiida_type,
            valid_type=(orm.Int, orm.Float),
            default=lambda: orm.Int(1),
            validator=_time_validator,
            help="The time to sleep.",
        )
        spec.input(
            "payload",
            serializer=to_aiida_type,
            valid_type=orm.Dict,
            default=lambda: orm.Dict(dict={}),
            help="A dictionary that will be uploaded and retrieved.",
        )
        spec.output(
            "result",
            valid_type=orm.Bool,
            help='If the output file contains "success".',
        )
        spec.output(
            "data",
            valid_type=orm.Dict,
            help="The output data (with size metadata.options.output_size).",
        )
        # set default options (optional)
        spec.inputs["metadata"]["options"]["parser_name"].default = "sleep"
        spec.inputs["metadata"]["options"]["input_filename"].default = "aiida.in"
        spec.inputs["metadata"]["options"]["output_filename"].default = "aiida.out"
        spec.inputs["metadata"]["options"]["resources"].default = {
            "num_machines": 1,
            "num_mpiprocs_per_machine": 1,
        }
        spec.input(
            "metadata.options.payload_filename",
            valid_type=str,
            default="payload.json",
            help="Filename to which the content of the payload JSON is written.",
        )
        spec.input(
            "metadata.options.fail_calcjob",
            valid_type=bool,
            default=False,
            help="Intentionally fail the calculation (with code 410).",
        )
        spec.input(
            "metadata.options.output_size",
            valid_type=int,
            default=100,
            help="The number of attributes for the output data.",
        )

        spec.exit_code(
            310,
            "ERROR_READING_OUTPUT_FILE",
            message="The output file could not be read.",
        )
        spec.exit_code(
            311,
            "ERROR_READING_PAYLOAD_FILE",
            message="The payload file could not be read.",
        )
        spec.exit_code(
            410,
            "ERROR_FAILED_OUTPUT",
            message="The output file contains a failed output.",
        )

    def prepare_for_submission(self, folder: Folder) -> CalcInfo:
        """Prepare the calculation for submission.

        :param folder: a temporary folder on the local file system.
        :returns: the `CalcInfo` instance
        """
        echo_value = "fail" if self.node.get_option("fail_calcjob") else "success"
        with folder.open(self.options.input_filename, "w", encoding="utf8") as handle:
            handle.write(f"sleep {self.inputs.time.value}\n")
            handle.write(f'echo "{echo_value}"\n')

        with folder.open(self.options.payload_filename, "wb") as handle:
            json.dump(self.inputs.payload.get_dict(), handle)

        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdin_name = self.options.input_filename
        codeinfo.stdout_name = self.options.output_filename

        calcinfo = CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.retrieve_list = [
            self.options.output_filename,
            self.options.payload_filename,
        ]

        return calcinfo


class SleepParser(Parser):
    """Parser for an `SleepCalculation` job."""

    def parse(self, **kwargs):
        """Parse the contents of the output files stored in the `retrieved` output node."""

        try:
            with self.retrieved.open(
                self.node.get_option("output_filename"), "r"
            ) as handle:
                result = handle.read().strip()
        except OSError:
            return self.exit_codes.ERROR_READING_OUTPUT_FILE

        try:
            with self.retrieved.open(
                self.node.get_option("payload_filename"), "r"
            ) as handle:
                pass
        except OSError:
            return self.exit_codes.ERROR_READING_PAYLOAD_FILE

        self.out("result", orm.Bool(result == "success"))
        self.out(
            "data",
            orm.Dict(
                dict={
                    f"output_key_{i}": f"value_{i}"
                    for i in range(self.node.get_option("output_size"))
                }
            ),
        )

        if not result == "success":
            return self.exit_codes.ERROR_FAILED_OUTPUT


def _children_validator(value, port):
    if value < 1:
        return "children must be > 0"
    return None


class SleepWorkChain(WorkChain):
    """WorkChain to multiply two numbers and add a third, for testing and demonstration purposes."""

    @classmethod
    def define(cls, spec):
        """Specify inputs and outputs."""
        super().define(spec)
        spec.input(
            "children",
            serializer=to_aiida_type,
            valid_type=orm.Int,
            default=lambda: orm.Int(1),
            validator=_children_validator,
            help="The number of calcjobs to spawn.",
        )
        spec.expose_inputs(SleepCalculation, namespace="calcjob")
        spec.outline(
            cls.run_calcjobs,
            cls.result,
        )
        spec.output_namespace("results", valid_type=orm.Bool, dynamic=True)
        spec.exit_code(
            400, "ERROR_CALCJOB_FAILURE", message="At least one calcjob failed."
        )

    def run_calcjobs(self):
        """Run a number of calcjobs."""
        for idx in range(self.inputs.children.value):
            future = self.submit(
                SleepCalculation,
                **self.exposed_inputs(SleepCalculation, namespace="calcjob"),
            )
            self.to_context(**{f"calcjob_{idx+1}": future})

    def result(self):
        """Add the result to the outputs."""
        failed = False
        for name, calcjob in self.ctx.items():
            self.out(f"results.{name}", calcjob.outputs.result)
            if not calcjob.outputs.result.value:
                failed = True
        if failed:
            return self.exit_codes.ERROR_CALCJOB_FAILURE
