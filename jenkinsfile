pipeline {
    agent any

    stages {

        stage('Clone Repository') {
            steps {
                git branch: 'main',
                url: 'https://github.com/Seshaveni123/FakeProfileDetector.git'
            }
        }

        stage('Build Backend Image') {
            steps {
                sh 'docker build -t seshaveni1/fakeguard-backend ./backend'
            }
        }

        stage('Build Frontend Image') {
            steps {
                sh 'docker build -t seshaveni1/fakeguard-frontend ./frontend'
            }
        }

        stage('Push Backend Image') {
            steps {
                sh 'docker push seshaveni1/fakeguard-backend'
            }
        }

        stage('Push Frontend Image') {
            steps {
                sh 'docker push seshaveni1/fakeguard-frontend'
            }
        }
    }
}