FROM jenkins/jenkins:lts-jdk17

USER root

# Install prerequisites, Docker CLI, kubectl, Python3, and Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update && apt-get install -y --no-install-recommends docker-ce-cli docker-buildx-plugin \
    && curl -fsSL -o /usr/local/bin/kubectl "https://dl.k8s.io/release/v1.31.0/bin/linux/amd64/kubectl" \
    && chmod +x /usr/local/bin/kubectl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add jenkins user to docker group if it exists
RUN groupadd -f -g 999 docker && usermod -aG docker jenkins

# Pre-install Python test dependencies for fast pipeline execution
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir pytest pytest-asyncio httpx fastapi pydantic scikit-learn pandas numpy && \
    chmod -R 777 /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY entrypoint-wrapper.sh /usr/local/bin/entrypoint-wrapper.sh

RUN chmod +x /usr/local/bin/entrypoint-wrapper.sh

ENTRYPOINT ["/usr/local/bin/entrypoint-wrapper.sh"]

