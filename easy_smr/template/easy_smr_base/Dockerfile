FROM rocker/r-base:latest

LABEL maintainer="None"

ARG module_path
ARG target_dir_name

WORKDIR /opt/program/${target_dir_name}/${module_path}

# Install renv and restore environment
RUN R -e "install.packages('renv')"
RUN R -e "renv::restore()"

COPY ${module_path} /opt/program/${target_dir_name}

ENTRYPOINT ["easy_sm_base/executor.sh"]
