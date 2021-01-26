FROM marvelnccr/docker-ubuntu2004-ansible:latest

# install system dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
  git \
  ssh \
  netcat \
  vim \
  graphviz \
  python3-dev \
  python3-distutils \
  python3-venv \
  python3-pip \
  gcc \
  g++ \
  bzip2 \
  zip \
  unzip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /root

# Add the ssh configuration identical to that in the slurm container
COPY ssh-keys .ssh
# SSH has strict requirements on the permissions of its configuration files, set them here
RUN chmod 700 .ssh && \
  chmod 600 .ssh/id_rsa .ssh/id_dsa && \
  chmod 644 .ssh/authorized_keys .ssh/id_rsa.pub .ssh/id_dsa.pub && \
  chown -R root:root .ssh
# When this image is used as ssh client then ignore the known hosts
RUN echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

# set default python as python3 venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# clone aiida-core repository and checkout particular branch/commit
ARG checkout=develop
RUN git clone https://github.com/aiidateam/aiida_core aiida-core
RUN cd aiida-core; git checkout $checkout

# pip install requirements
# note here we assume that ubuntu2004 has python 3.8
RUN pip install -U pip setuptools wheel flit; pip install pympler
RUN pip install -r aiida-core/requirements/requirements-py-3.8.txt
RUN pip install --no-deps -e aiida-core

# Add verdi autocompletion to bash initiation
RUN echo 'eval "$(/opt/venv/bin/verdi completioncommand)"' >> .bashrc

# Add the aiida-sleep plugin
COPY aiida-sleep aiida-sleep
RUN cd aiida-sleep; FLIT_ROOT_INSTALL=1 flit install --symlink; reentry scan

# Add the configuration files to setup aiida
COPY aiida_config aiida_config

# Add bash history of useful commands
COPY bash_history .bash_history
