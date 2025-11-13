pipeline {
    agent any

    stages {

        stage('Checkout Backend Code') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: "*/feature/code-merge"]],
                    userRemoteConfigs: [[
                        url: 'https://github.com/apexneural-likhithmasura/dbaas-backup.git',
                        credentialsId: 'github-token'
                    ]]
                ])
            }
        }

        stage('Zip Backend') {
            steps {
                bat """
                    "C:\\Program Files\\7-Zip\\7z.exe" a backend.zip .\\*
                """
            }
        }

        stage('Deploy to WSL Backend') {
            steps {
                sshPublisher(publishers: [
                    sshPublisherDesc(
                        configName: 'wsl-ssh',
                        transfers: [
                            sshTransfer(
                                sourceFiles: 'backend.zip',
                                remoteDirectory: '/home/pandu',
                                execCommand: '''
                                    cd /home/pandu

                                    echo "🗑 Removing old backend code..."
                                    rm -rf /var/www/backend/app/*

                                    echo "📦 Unzipping backend..."
                                    unzip -o backend.zip -d /var/www/backend/app

                                    echo "📦 Installing Python dependencies..."
                                    /var/www/backend/venv/bin/pip install --upgrade pip
                                    /var/www/backend/venv/bin/pip install -r /var/www/backend/app/requirements.txt

                                    echo "🔄 Restarting backend service..."
                                    sudo systemctl restart backend

                                    echo "🧹 Cleaning up..."
                                    rm backend.zip

                                    echo "✔ Backend deployed successfully!"
                                '''
                            )
                        ],
                        verbose: true
                    )
                ])
            }
        }
    }

    post {
        success {
            echo '🚀 Backend deployment completed successfully!'
        }
        failure {
            echo '❌ Backend deployment failed!'
        }
        always {
            cleanWs()
        }
    }
}
