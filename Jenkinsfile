pipeline {
    agent any

    environment {
        BACKEND_IMAGE = "seshaveni1/fakeguard-backend"
        FRONTEND_IMAGE = "seshaveni1/fakeguard-frontend"
    }

    stages {

        stage('Clone Repository') {
            steps {
                git branch: 'main',
                url: 'https://github.com/Seshaveni123/FakeProfileDetector.git'
            }
        }

        stage('Build Backend Image') {
            steps {
                sh "docker build -t $BACKEND_IMAGE ./backend"
            }
        }

        stage('Build Frontend Image') {
            steps {
                sh "docker build -t $FRONTEND_IMAGE ./frontend"
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }

        stage('Push Backend Image') {
            steps {
                sh "docker push $BACKEND_IMAGE"
            }
        }

        stage('Push Frontend Image') {
            steps {
                sh "docker push $FRONTEND_IMAGE"
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                 sh 'kubectl apply --validate=false -f kubernetes/'
    }
}
    }
}