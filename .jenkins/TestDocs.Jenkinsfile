pipeline {
    agent {
        docker {
            image "ghcr.io/jtroe/cicd-container-images/sphinx-rtd:5.3.0"
            args "-u 0 -v /media/crdata_apiref:/media/crdata_apiref -v /media/geosaurus_public:/media/geosaurus_public"
            customWorkspace "workspace/$JOB_NAME/$BUILD_NUMBER"
        }
    }

    stages {
        stage('Setup') {
            steps {
                dir('geosaurus') {
                    checkout scm
                    sh "echo Building for $GIT_COMMIT"
                }
            }
        }
        stage('Cleanup') {
            steps {
                sh 'rm -rf geosaurus'
            }
        }
    }
}