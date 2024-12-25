FROM rocker/r-base:latest

LABEL maintainer="None"

ARG module_path
ARG target_dir_name

COPY ${module_path} /opt/program/${target_dir_name}

# Set to top level directory for consistency with local development environment
WORKDIR /opt/program/

# Copy renv related files to top level directory and restore environment (again for consistency with local development environment)
RUN mkdir -p renv
COPY ${module_path}/easy_smr_base/.Rprofile .Rprofile
COPY ${module_path}/easy_smr_base/renv.lock renv.lock
COPY ${module_path}/easy_smr_base/renv/activate.R renv/activate.R
COPY ${module_path}/easy_smr_base/renv/settings.json renv/settings.json

RUN R -e "install.packages('renv')"
RUN R -e "renv::restore()"

ENTRYPOINT ["easy_sm_base/executor.sh"]
