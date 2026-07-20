FROM jenkins/jenkins:lts-jdk17

USER root

# Docker CLI talks to the Docker Desktop daemon through the mounted socket.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg lsb-release unzip \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli \
    && curl -fsSL https://releases.hashicorp.com/terraform/1.10.5/terraform_1.10.5_linux_amd64.zip -o /tmp/terraform.zip \
    && unzip /tmp/terraform.zip -d /usr/local/bin \
    && rm -rf /var/lib/apt/lists/* /tmp/terraform.zip

# The workspace can be created by the Jenkins image's original jenkins user
# and later used by the local root-runner; allow Git to reuse that workspace.
RUN git config --system --add safe.directory '*'

USER jenkins
