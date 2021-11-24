pipeline {
  agent any
  stages {
    stage('') {
      steps {
        bat(script: 'c:/conda/python.exe "%WORKSPACE%/src/setup.py" sdist --formats=gztar,zip', returnStdout: true)
      }
    }

  }
}