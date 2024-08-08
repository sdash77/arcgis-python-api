pipeline {
    agent {
        docker {
            image "harbor-west.esri.com/python-api/arcgis-learn-pr-docs:latest"
            registryUrl 'https://harbor-west.esri.com'
            registryCredentialsId 'avworld_geosaurusaccnt'
            alwaysPull true
            label "linux && docker"
            args "-u 0 -v /media/crdata_apiref:/media/crdata_apiref -v /media/geosaurus_public:/media/geosaurus_public"
            customWorkspace "workspace/$JOB_NAME/$BUILD_NUMBER"
        }
    }

    stages {
        stage('Setup') {
            steps {
                // copy in dependent binaries to relevant path
                sh 'cp /media/geosaurus_public/build/geosaurus2/linux/py3.11/graph/* ./src/arcgis/graph'
                sh 'cp /media/geosaurus_public/build/geosaurus2/linux/py3.11/knn/* ./src/arcgis/learn/_utils'
                sh 'cp /media/geosaurus_public/build/geosaurus2/linux/py3.11/tracking-engine/* ./src/arcgis/learn/_tracking'
                sh 'python -m pip install -e ./src --no-deps'
            }
        }
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
                            sh 'zip -r ../html.zip *'
                            sh 'cp ../html.zip /media/geosaurus_public/docs/python-api/master'

                            // clean and deploy to crdata share
                            sh 'rm -rf /media/crdata_apiref/*'
                            sh 'cp -r . /media/crdata_apiref'

                            // clean and deploy to geosaurus share (master)
                            sh 'rm -rf /media/geosaurus_public/docs/python-api/master/html/*'
                            sh 'cp -r . /media/geosaurus_public/docs/python-api/master/html'

                            // deploy to geosaurus share (by commit)
                            sh "mkdir -p /media/geosaurus_public/docs/python-api/build/$GIT_COMMIT/html"
                            sh "cp ../html.zip /media/geosaurus_public/docs/python-api/build/$GIT_COMMIT"
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
                            sh 'zip -r ../json.zip *'
                            sh 'cp ../json.zip /media/geosaurus_public/docs/python-api/master'

                            // clean and deploy to geosaurus share (master)
                            sh 'rm -rf /media/geosaurus_public/docs/python-api/master/json/*'
                            sh 'cp -r . /media/geosaurus_public/docs/python-api/master/json'

                            // deploy to geosaurus share (by commit)
                            sh "mkdir -p /media/geosaurus_public/docs/python-api/build/$GIT_COMMIT/json"
                            sh "cp ../json.zip /media/geosaurus_public/docs/python-api/build/$GIT_COMMIT"
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