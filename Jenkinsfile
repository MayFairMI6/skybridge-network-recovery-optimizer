pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  triggers {
    // Poll every two minutes. Jenkins detects changes; it does not build on every poll.
    pollSCM('H/2 * * * *')
  }

  environment {
    IMAGE_NAME = 'local-pipeline-app'
    CONTAINER_NAME = 'local-pipeline-app'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build Docker image') {
      steps {
        sh '''#!/bin/sh
          set -eu
          docker build --build-arg APP_BUILD="$BUILD_NUMBER" -t "$IMAGE_NAME:$BUILD_NUMBER" .
        '''
      }
    }

    stage('Deploy with Terraform') {
      steps {
        dir('terraform') {
          sh '''#!/bin/sh
            set -eu
            terraform init -input=false
            # The app name is intentionally stable. Remove an orphaned prior
            # container if the Jenkins workspace/state was recreated.
            docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
            terraform apply -auto-approve -input=false \\
              -var="image_name=$IMAGE_NAME:$BUILD_NUMBER" \\
              -var="container_name=$CONTAINER_NAME"
          '''
        }
      }
    }
  }

  post {
    success {
      sh 'docker ps --filter "name=^/${CONTAINER_NAME}$"'
    }
  }
}
