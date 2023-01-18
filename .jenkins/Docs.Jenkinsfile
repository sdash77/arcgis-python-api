pipeline {
    agent {
        docker {
            image "ghcr.io/jtroe/cicd-container-images/sphinx-rtd:5.3.0"
            args "-u 0 -v /media/crdata_apiref:/media/crdata_apiref -v /media/geosaurus_public:/media/geosaurus_public"
            customWorkspace "workspace/$JOB_NAME/$BUILD_NUMBER"
        }
    }

    stages {
        stage('Sphinx HTML') {
            stages {
                stage('Build') {
                    steps {
                        dir('docs/api_ref') {
                            sh 'make html'
                        }
                    }
                }
                stage('Deploy') {
                    steps {
                        dir('docs/api_ref/build/html') {
                            // clean and deploy to crdata share
                            sh 'rm -rf /media/crdata_apiref/*'
                            sh 'cp -r . /media/crdata_apiref'

                            // clean and deploy to geosaurus share (master)
                            sh 'rm -rf /media/geosaurus_public/docs/python-api/master/html/*'
                            sh 'cp -r . /media/geosaurus_public/docs/python-api/master/html'

                            // deploy to geosaurus share (by commit)
                            sh "mkdir -p /media/geosaurus_public/docs/python-api/build/$GIT_COMMIT/html"
                            sh "cp -r . /media/geosaurus_public/docs/python-api/build/$GIT_COMMIT/html"
                        }
                    }
                }
            }
        }
        stage('Sphinx JSON') {
            stages {
                stage('Build') {
                    steps {
                        dir('docs/api_ref') {
                            sh 'make json'
                        }
                    }
                }
                stage('Deploy') {
                    steps {
                        dir('docs/api_ref/build/json') {
                            // clean and deploy to geosaurus share (master)
                            sh 'rm -rf /media/geosaurus_public/docs/python-api/master/json/*'
                            sh 'cp -r . /media/geosaurus_public/docs/python-api/master/json'

                            // deploy to geosaurus share (by commit)
                            sh "mkdir -p /media/geosaurus_public/docs/python-api/build/$GIT_COMMIT/json"
                            sh "cp -r . /media/geosaurus_public/docs/python-api/build/$GIT_COMMIT/json"
                        }
                    }
                }
            }
        }
        stage('Cleanup') {
            steps {
                cleanWs()
            }
        }
    }
}