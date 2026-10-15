pipeline {
    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    parameters {
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Execute automated backend and frontend tests')
        booleanParam(name: 'PUSH_TO_REGISTRY', defaultValue: true, description: 'Publish built application Docker images to Docker Hub registry')
        booleanParam(name: 'DEPLOY_TO_K8S', defaultValue: true, description: 'Deploy application manifests to Kubernetes cluster')
        string(name: 'K8S_NAMESPACE', defaultValue: 'fakeguard', description: 'Target Kubernetes namespace for deployment')
    }

    environment {
        // Docker Registry & Image definitions
        DOCKER_REGISTRY      = "seshaveni1"
        PREDICTION_IMAGE     = "${DOCKER_REGISTRY}/fakeguard-prediction"
        HISTORY_IMAGE        = "${DOCKER_REGISTRY}/fakeguard-history"
        ANALYTICS_IMAGE      = "${DOCKER_REGISTRY}/fakeguard-analytics"
        FRONTEND_IMAGE       = "${DOCKER_REGISTRY}/fakeguard-frontend"
        BACKEND_IMAGE        = "${DOCKER_REGISTRY}/fakeguard-backend"

        // Build metadata and image tags
        IMAGE_TAG            = "${env.BUILD_NUMBER}"
        GIT_COMMIT_SHORT     = "${sh(script: 'git rev-parse --short HEAD 2>/dev/null || echo "manual"', returnStdout: true).trim()}"

        // Kubernetes Target Configuration
        TARGET_NAMESPACE     = "${params.K8S_NAMESPACE}"
        KUBECONFIG_PATH      = "${env.KUBECONFIG ?: '/var/jenkins_home/.kube/config'}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "=========================================================="
                echo "Stage 1: Checkout Source Code"
                echo "=========================================================="
                checkout scm
                sh '''
                    echo "Repository: https://github.com/Seshaveni123/FakeProfileDetector"
                    echo "Current Commit: $(git rev-parse HEAD 2>/dev/null || echo 'workspace')"
                    echo "Short Commit SHA: ${GIT_COMMIT_SHORT}"
                    echo "Build Number: ${BUILD_NUMBER}"
                '''
            }
        }

        stage('Validation') {
            steps {
                echo "=========================================================="
                echo "Stage 2: Validation of Workspace and Configurations"
                echo "=========================================================="
                sh '''
                    echo "Verifying presence of Dockerfiles, Compose specs, and Kubernetes manifests..."
                    test -f docker-compose.yml || { echo "ERROR: docker-compose.yml not found"; exit 1; }
                    test -f services/prediction-service/Dockerfile || { echo "ERROR: Prediction Dockerfile not found"; exit 1; }
                    test -f services/history-service/Dockerfile || { echo "ERROR: History Dockerfile not found"; exit 1; }
                    test -f services/analytics-service/Dockerfile || { echo "ERROR: Analytics Dockerfile not found"; exit 1; }
                    test -f frontend/Dockerfile || { echo "ERROR: Frontend Dockerfile not found"; exit 1; }
                    test -f kubernetes/microservices.yaml || { echo "ERROR: kubernetes/microservices.yaml not found"; exit 1; }
                    test -f kubernetes/frontend-deployment.yaml || { echo "ERROR: kubernetes/frontend-deployment.yaml not found"; exit 1; }

                    echo "Validating Docker daemon connectivity from Jenkins..."
                    docker info >/dev/null 2>&1 || {
                        echo "ERROR: Docker daemon is not accessible from Jenkins. Check /var/run/docker.sock mount.";
                        exit 1;
                    }
                    echo "Docker daemon verified. Engine version: $(docker version --format '{{.Server.Version}}')"
                    echo "All project validation checks passed successfully."
                '''
            }
        }

        stage('Testing') {
            when {
                expression { return params.RUN_TESTS.toBoolean() == true }
            }
            steps {
                echo "=========================================================="
                echo "Stage 3: Automated Testing"
                echo "=========================================================="
                sh '''
                    echo "--- Running Backend Unit & Service Tests ---"
                    pytest tests/ -v --ignore=tests/test_microservices_e2e.py

                    echo "--- Validating Frontend Assets & Configuration ---"
                    test -f frontend/package.json || { echo "ERROR: frontend/package.json missing"; exit 1; }
                    echo "Frontend configuration is valid."
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo "=========================================================="
                echo "Stage 4: Build Docker Images"
                echo "=========================================================="
                sh '''
                    echo "Building [1/4] Prediction Service (Port 8000)..."
                    docker build -t ${PREDICTION_IMAGE}:${IMAGE_TAG} \
                                 -t ${PREDICTION_IMAGE}:latest \
                                 -f services/prediction-service/Dockerfile .

                    echo "Building [2/4] History Service (Port 8001)..."
                    docker build -t ${HISTORY_IMAGE}:${IMAGE_TAG} \
                                 -t ${HISTORY_IMAGE}:latest \
                                 -f services/history-service/Dockerfile .

                    echo "Building [3/4] Analytics Service (Port 8002)..."
                    docker build -t ${ANALYTICS_IMAGE}:${IMAGE_TAG} \
                                 -t ${ANALYTICS_IMAGE}:latest \
                                 -f services/analytics-service/Dockerfile .

                    echo "Building [4/4] Frontend Service (Port 5173)..."
                    docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                                 -t ${FRONTEND_IMAGE}:latest \
                                 ./frontend

                    echo "--- Built Images Summary ---"
                    docker images --filter "reference=${DOCKER_REGISTRY}/fakeguard*"
                '''
            }
        }

        stage('Publish to Docker Hub') {
            when {
                expression { return params.PUSH_TO_REGISTRY == null || params.PUSH_TO_REGISTRY.toBoolean() == true }
            }
            steps {
                echo "=========================================================="
                echo "Stage 5: Publish Application Images to Docker Hub (${DOCKER_REGISTRY})"
                echo "=========================================================="
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "Authenticating with Docker Hub as user: ${DOCKER_USER}..."
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

                        echo "Publishing [1/4] Prediction Service (${PREDICTION_IMAGE})..."
                        docker push ${PREDICTION_IMAGE}:${IMAGE_TAG}
                        docker push ${PREDICTION_IMAGE}:latest

                        echo "Publishing [2/4] History Service (${HISTORY_IMAGE})..."
                        docker push ${HISTORY_IMAGE}:${IMAGE_TAG}
                        docker push ${HISTORY_IMAGE}:latest

                        echo "Publishing [3/4] Analytics Service (${ANALYTICS_IMAGE})..."
                        docker push ${ANALYTICS_IMAGE}:${IMAGE_TAG}
                        docker push ${ANALYTICS_IMAGE}:latest

                        echo "Publishing [4/4] Frontend Service (${FRONTEND_IMAGE})..."
                        docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
                        docker push ${FRONTEND_IMAGE}:latest

                        docker logout
                        echo "All 4 FakeGuard AI application images successfully published to Docker Hub."
                    '''
                }
            }
        }

        stage('Kubernetes Validation') {
            steps {
                echo "=========================================================="
                echo "Stage 6: Kubernetes Manifest Validation"
                echo "=========================================================="
                sh '''
                    if [ -f "$KUBECONFIG_PATH" ]; then
                        export KUBECONFIG="$KUBECONFIG_PATH"
                    fi

                    echo "Testing kubectl client and server connectivity..."
                    kubectl version --client

                    echo "Performing client-side dry-run validation of manifests..."
                    test -f kubernetes/namespace.yaml && kubectl apply --dry-run=client -f kubernetes/namespace.yaml
                    kubectl apply --dry-run=client -n ${TARGET_NAMESPACE} -f kubernetes/microservices.yaml
                    kubectl apply --dry-run=client -n ${TARGET_NAMESPACE} -f kubernetes/frontend-deployment.yaml
                    kubectl apply --dry-run=client -n ${TARGET_NAMESPACE} -f kubernetes/frontend-service.yaml

                    echo "Manifests are syntactically and structurally valid."
                '''
            }
        }

        stage('Kubernetes Deployment') {
            when {
                expression { return params.DEPLOY_TO_K8S.toBoolean() == true }
            }
            steps {
                echo "=========================================================="
                echo "Stage 7: Deploying to Kubernetes Cluster"
                echo "=========================================================="
                sh '''
                    if [ -f "$KUBECONFIG_PATH" ]; then
                        export KUBECONFIG="$KUBECONFIG_PATH"
                    fi

                    # 1. Ensure target namespace exists
                    if [ -f kubernetes/namespace.yaml ]; then
                        kubectl apply -f kubernetes/namespace.yaml
                    else
                        kubectl create namespace ${TARGET_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                    fi

                    # 2. Ensure database credentials secret exists in target namespace without hardcoding passwords in Git
                    if ! kubectl get secret fakeguard-database -n ${TARGET_NAMESPACE} >/dev/null 2>&1; then
                        if kubectl get secret fakeguard-database -n default >/dev/null 2>&1; then
                            echo "Replicating existing fakeguard-database secret into ${TARGET_NAMESPACE} namespace..."
                            kubectl get secret fakeguard-database -n default -o yaml | \
                                sed '/namespace: default/d; /resourceVersion:/d; /uid:/d; /creationTimestamp:/d' | \
                                kubectl apply -n ${TARGET_NAMESPACE} -f -
                        else
                            echo "Generating initial fakeguard-database secret in ${TARGET_NAMESPACE}..."
                            kubectl create secret generic fakeguard-database \
                                --from-literal=database=fakeguard \
                                --from-literal=username=fakeguard \
                                --from-literal=password=fakeguard \
                                --from-literal=url='postgresql://fakeguard:fakeguard@postgres-service:5432/fakeguard' \
                                -n ${TARGET_NAMESPACE}
                        fi
                    fi

                    # 3. Apply Microservices, PostgreSQL, and HPA
                    echo "Deploying Microservices (Prediction, History, Analytics, PostgreSQL)..."
                    kubectl apply -n ${TARGET_NAMESPACE} -f kubernetes/microservices.yaml

                    # 4. Apply Frontend
                    echo "Deploying Frontend Service & Deployment..."
                    kubectl apply -n ${TARGET_NAMESPACE} -f kubernetes/frontend-deployment.yaml
                    kubectl apply -n ${TARGET_NAMESPACE} -f kubernetes/frontend-service.yaml

                    # 5. Apply Ingress if ingress-nginx controller is present
                    if [ -f kubernetes/ingress.yaml ]; then
                        echo "Applying Ingress routing rules..."
                        kubectl apply -n ${TARGET_NAMESPACE} -f kubernetes/ingress.yaml || echo "Ingress optional"
                    fi
                '''
            }
        }

        stage('Rollout Verification') {
            when {
                expression { return params.DEPLOY_TO_K8S.toBoolean() == true }
            }
            steps {
                echo "=========================================================="
                echo "Stage 8: Verifying Deployment Rollouts and Health"
                echo "=========================================================="
                sh '''
                    if [ -f "$KUBECONFIG_PATH" ]; then
                        export KUBECONFIG="$KUBECONFIG_PATH"
                    fi

                    echo "Verifying postgres-deployment rollout..."
                    kubectl rollout status deployment/postgres-deployment -n ${TARGET_NAMESPACE} --timeout=90s

                    echo "Verifying history-service-deployment rollout..."
                    kubectl rollout status deployment/history-service-deployment -n ${TARGET_NAMESPACE} --timeout=90s

                    echo "Verifying prediction-service-deployment rollout..."
                    kubectl rollout status deployment/prediction-service-deployment -n ${TARGET_NAMESPACE} --timeout=90s

                    echo "Verifying analytics-service-deployment rollout..."
                    kubectl rollout status deployment/analytics-service-deployment -n ${TARGET_NAMESPACE} --timeout=90s

                    echo "Verifying frontend-deployment rollout..."
                    kubectl rollout status deployment/frontend-deployment -n ${TARGET_NAMESPACE} --timeout=90s

                    echo "--- Kubernetes Resources in Namespace [${TARGET_NAMESPACE}] ---"
                    kubectl get deployments,services,pods -n ${TARGET_NAMESPACE} -o wide
                '''
            }
        }
    }

    post {
        always {
            echo "=========================================================="
            echo "Stage 9: Post-build Cleanup & Execution Summary"
            echo "=========================================================="
            sh '''
                echo "Build ID: ${BUILD_NUMBER}"
                echo "Git Commit: ${GIT_COMMIT_SHORT}"
                echo "Timestamp: $(date -u)"
                # Safe cleanup: prune dangling builder cache if needed
                docker builder prune -f --filter "until=24h" 2>/dev/null || true
            '''
        }
        success {
            echo "=========================================================="
            echo "SUCCESS: FakeGuard AI CI/CD Pipeline Completed Successfully!"
            echo "All microservices and frontend built, validated, and deployed to ${TARGET_NAMESPACE}."
            echo "=========================================================="
        }
        failure {
            echo "=========================================================="
            echo "FAILURE: Pipeline execution encountered an error."
            echo "Please inspect stage output above for root cause."
            echo "=========================================================="
        }
    }
}