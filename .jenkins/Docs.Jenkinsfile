def geoserpent_scm = [$class: 'GitSCM', branches: [[name: '$GeoserpentBranch']], extensions: [[$class: 'CloneOption', noTags: true, reference: '', shallow: true, timeout: 240]], userRemoteConfigs: [[credentialsId: 'github_geosaurusaccnt', refspec: '+refs/heads/$GeoserpentBranch:refs/remotes/origin/$GeoserpentBranch', url: 'https://github.com/ArcGIS/geoserpent.git']]]

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
    parameters {
        string(name: 'GeoserpentBranch', defaultValue: 'main', description: 'Geoserpent source branch for arcgis-mapping')
    }

    stages {
        stage('Setup') {
            steps {
                dir("geoserpent") {
                    checkout geoserpent_scm
                }
                // copy in dependent binaries to relevant path
                sh 'python ./build/manage_binaries.py copy --local'
                // install arcgis
                sh 'python -m pip install ./src --no-deps'
                // install arcgis-mapping
                sh 'python -m pip install ./geoserpent/arcgis-mapping/src --no-deps'
                // copy arcgis.map namespace to arcgis
                sh 'cp -r geoserpent/arcgis-mapping/src/arcgis/map src/arcgis'
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