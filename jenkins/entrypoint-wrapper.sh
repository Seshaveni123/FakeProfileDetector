#!/bin/bash
set -e

# If the Docker daemon socket is mounted, grant read/write access so the jenkins user can interact with Docker
if [ -S /var/run/docker.sock ]; then
    chmod 666 /var/run/docker.sock 2>/dev/null || true
fi

# If kubeconfig is mounted at /var/jenkins_home/.kube/config, ensure permissions
if [ -f /var/jenkins_home/.kube/config ]; then
    chown -R jenkins:jenkins /var/jenkins_home/.kube 2>/dev/null || true
fi

# Execute the default Jenkins entrypoint
exec /usr/bin/tini -- /usr/local/bin/jenkins.sh "$@"
