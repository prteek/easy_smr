FROM rocker/r-base:latest

LABEL maintainer="None"

ARG module_path
ARG target_dir_name

COPY ${module_path} /opt/program/${target_dir_name}

# Install renv and restore environment from renv path
WORKDIR /opt/program/${target_dir_name}/easy_smr_base
RUN R -e "install.packages('renv')"
RUN R -e "renv::restore()"

# For consistency with local development path
WORKDIR /opt/program/

ENTRYPOINT ["easy_sm_base/executor.sh"]
