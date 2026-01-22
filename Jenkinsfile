pipeline {
    agent any

    triggers {
        githubPush()
        pollSCM("H/5 * * * *")
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: "10"))
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        DOCKER_IMAGE = "crewai-automation"
        DOCKER_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage("Checkout") {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                }
            }
        }

        stage("Setup Python") {
            steps {
                sh "python3 -m venv venv"
                sh ". venv/bin/activate && pip install --upgrade pip"
                sh ". venv/bin/activate && pip install -r requirements.txt"
            }
        }

        stage("Lint") {
            steps {
                sh ". venv/bin/activate && pip install flake8"
                sh ". venv/bin/activate && flake8 main.py --max-line-length=120 || true"
            }
        }

        stage("Test") {
            steps {
                sh ". venv/bin/activate && pip install pytest pytest-cov"
                sh ". venv/bin/activate && pytest tests/ -v --junitxml=test-results.xml || true"
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: "test-results.xml"
                }
            }
        }

        stage("Build Docker Image") {
            when { branch "main" }
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} -t ${DOCKER_IMAGE}:latest ."
            }
        }

        stage("Deploy") {
            when { branch "main" }
            steps {
                echo "Ready to deploy ${DOCKER_IMAGE}:${DOCKER_TAG}"
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo "Build ${BUILD_NUMBER} succeeded!"
        }
        failure {
            echo "Build ${BUILD_NUMBER} failed!"
        }
    }
}
