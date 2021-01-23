#!/bin/bash
set -ex

cd "$(dirname "$0")"

verdi quicksetup -n --config profile_quicksetup.yml
verdi daemon start 1
verdi status
verdi computer setup -n --config slurm_computer_setup.yml
verdi computer configure ssh slurm -n --config slurm_computer_config.yml
verdi computer test slurm
