node {
    stage('Checkout Backend Code') {
        checkout([
            $class: 'GitSCM',
            branches: [[name: "*/feature/code-merge"]],
            userRemoteConfigs: [[
                url: 'https://github.com/apexneural-likhithmasura/dbaas-backup.git',
                credentialsId: 'github-token'
            ]]
        ])
    }

    stage('Zip Backend') {
        bat "\"C:\\Program Files\\7-Zip\\7z.exe\" a backend.zip .\\*"
    }

    stage('Deploy to WSL Backend') {
        sshPublisher(publishers: [
            sshPublisherDesc(
                configName: 'wsl-ssh',
                transfers: [
                    sshTransfer(
                        sourceFiles: 'backend.zip',
                        remoteDirectory: '',
                        execCommand: '''
                            cd /home/pandu

                            echo "🗑 Removing old backend code..."
                            rm -rf /var/www/backend/app/*

                            echo "📦 Unzipping backend..."
                            unzip -o /home/pandu/backend.zip -d /var/www/backend/app

                            echo "📦 Installing dependencies..."
                            /var/www/backend/venv/bin/pip install -r /var/www/backend/app/requirements.txt

                            echo "🔄 Restarting backend..."
                            sudo systemctl restart backend

                            echo "🧹 Cleaning..."
                            rm /home/pandu/backend.zip

                            echo "✔ Backend deployed successfully!"
                        '''
                    )
                ],
                verbose: true
            )
        ])
    }

    stage('Cleanup') {
        cleanWs()
    }
}
