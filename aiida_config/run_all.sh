#!/bin/bash
set -ex

cd "$(dirname "$0")"

# profile
verdi quicksetup -n --config quicksetup.yml
verdi status

# computers
verdi computer setup -n --config computer-local.yml
verdi computer configure core.local local -n --config computer-configure-local.yml
verdi computer test local
verdi computer setup -n --config computer-slurm.yml
verdi computer configure core.ssh slurm -n --config computer-configure-slurm.yml
verdi computer test slurm

# codes
verdi code create core.code.installed -n --config code-local-sleep.yml
verdi code create core.code.installed -n --config code-slurm-sleep.yml
verdi code create core.code.installed -n --config code-local-add.yml
