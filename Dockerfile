# Use Debian Bookworm as the base image
FROM bitnami/minideb:bookworm

WORKDIR /app/

# Debian 12 thing
ENV PIP_BREAK_SYSTEM_PACKAGES 1

# Install Python3 and required packages using Apt
RUN apt-get -qqq update && \
    apt-get -qqq install -y python3 python3-pip && \
	apt-get clean && \
    pip3 install --upgrade pip setuptools wheel --quiet --root-user-action=ignore

# Copy necessary files to /app directory
COPY *.TXT /app/
COPY *.gz /app/
COPY docker_install_srvc.sh /app/


# Execute installation script
RUN /app/docker_install_srvc.sh
COPY setup.config.template /etc/rollama/setup.config 

# Expose port 5001
EXPOSE 5001

# ROllama Env vars
ARG host
ENV host $host
ARG port
ENV port $port
ARG database
ENV database $database
ARG user
ENV user $user
ARG password
ENV password $password
ARG client_id
ENV client_id $client_id
ARG client_secret
ENV client_secret $client_secret
ARG username
ENV username $username
ARG rpassword
ENV rpassword $rpassword
ARG user_agent
ENV user_agent $user_agent
ARG JWT_SECRET_KEY
ENV JWT_SECRET_KEY $JWT_SECRET_KEY
ARG SRVC_SHARED_SECRET
ENV SRVC_SHARED_SECRET $SRVC_SHARED_SECRET
ARG IDENTITY
ENV IDENTITY $IDENTITY
ARG APP_SECRET_KEY
ENV APP_SECRET_KEY $APP_SECRET_KEY
ARG CSRF_PROTECTION_KEY
ENV CSRF_PROTECTION_KEY $CSRF_PROTECTION_KEY
ARG ENDPOINT_URL
ENV ENDPOINT_URL $ENDPOINT_URL 
ARG OLLAMA_API_URL
ENV OLLAMA_API_URL $OLLAMA_API_URL
ARG PROC_WORKERS
ENV PROC_WORKERS $PROC_WORKERS
ARG LLMS
ENV LLMS $LLMS
ARG ENCRYPTION_KEY
ENV ENCRYPTION_KEY $ENCRYPTION_KEY

# Run ROllama Run!
CMD ["/usr/local/rollama/docker_run_srvc.sh"]
