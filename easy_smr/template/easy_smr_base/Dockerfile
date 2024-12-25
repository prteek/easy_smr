FROM rocker/r-base:latest

LABEL maintainer="None"

ARG module_path
ARG target_dir_name

COPY ${module_path} /opt/program/${target_dir_name}

# Install renv and here packages and restore the environment.
# It is assumed that all the scripts should load this Renv internally: renv::load('path_to_renv')
RUN R -e "install.packages(c('renv', 'here', 'plumber'))"
RUN R -e "renv::load('/opt/program/${target_dir_name}/easy_smr_base') ; \
            renv::restore()"

# Set to top level directory for consistency with local development environment path references within scripts
WORKDIR /opt/program/

# target_dir_name is saved as an ENV var to allow expansion subsequently. This variable is then also used in executer.sh, train (training), serve (serving)
ENV TARGET_DIR=${target_dir_name}

# The weird bit at the end allows passing arguments to executer.sh at runtime
ENTRYPOINT ["/bin/sh", "-c", "$TARGET_DIR/easy_smr_base/executor.sh \"$@\"", "--"]