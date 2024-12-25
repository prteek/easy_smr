FROM rocker/r-base:latest

LABEL maintainer="None"

ARG module_path
ARG target_dir_name

COPY ${module_path} /opt/program/${target_dir_name}

# Install renv and here packages and restore the environment.
# It is assumed that all the scripts should load this Renv internally: renv::load('path_to_renv')
RUN R -e "install.packages(c('renv', 'here'))"
RUN R -e "renv::load('/opt/program/${target_dir_name}/easy_smr_base') ; \
            renv::restore()"

# Set to top level directory for consistency with local development environment path references within scripts
WORKDIR /opt/program/

ENTRYPOINT ["easy_smr_base/executor.sh"]
