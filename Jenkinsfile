stage('Deploy to WSL Backend') {
    steps {
        sshPublisher(publishers: [
            sshPublisherDesc(
                configName: 'wsl-ssh',
                transfers: [
                    sshTransfer(
                        sourceFiles: 'backend.zip',
                        remoteDirectory: '/home/pandu',
                        removePrefix: '',
                        execCommand: '''
                            cd /home/pandu

                            echo "🗑 Removing old backend code..."
                            rm -rf /var/www/backend/app/*

                            echo "📦 Unzipping backend..."
                            unzip -o /home/pandu/backend.zip -d /var/www/backend/app

                            echo "📦 Installing Python dependencies..."
                            /var/www/backend/venv/bin/pip install -r /var/www/backend/app/requirements.txt

                            echo "🔄 Restarting backend service..."
                            echo pandu_password_here | sudo -S systemctl restart backend

                            echo "🧹 Cleaning up..."
                            rm /home/pandu/backend.zip

                            echo "✔ Backend deployed successfully!"
                        '''
                    )
                ],
                verbose: true
            )
        ])
    }
}
