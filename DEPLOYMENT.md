# ChatBT Deployment Guide

This guide provides instructions for deploying the ChatBT application in a production environment.

## Prerequisites

*   A server with Python 3.8+ and Node.js 14+ installed.
*   A process manager like `systemd` or `supervisor` to keep the backend running.
*   A web server like Nginx or Apache to act as a reverse proxy.

## Deployment Steps

### 1. Prepare the Application

1.  **Clone the repository or upload the final package to your server.**

2.  **Install backend dependencies:**

    ```bash
    cd /path/to/chatbt/chatbt-backend
    pip install -r requirements.txt
    ```

3.  **Build the frontend:**

    ```bash
    cd /path/to/chatbt/chatbt-frontend
    npm install
    npm run build
    ```

4.  **Copy the frontend build to the backend static directory:**

    ```bash
    cp -r /path/to/chatbt/chatbt-frontend/dist/* /path/to/chatbt/chatbt-backend/src/static/
    ```

### 2. Configure the Backend

1.  **Create a `.env` file in the `chatbt-backend` directory with the following content:**

    ```env
    FLASK_ENV=production
    SECRET_KEY=your-production-secret-key
    ```

2.  **Test the backend:**

    ```bash
    cd /path/to/chatbt/chatbt-backend
    python src/main_with_specialists.py
    ```

    The backend should start on `http://0.0.0.0:5000`.

### 3. Set up a Process Manager (systemd)

1.  **Create a systemd service file:**

    ```bash
    sudo nano /etc/systemd/system/chatbt.service
    ```

2.  **Add the following content to the file:**

    ```ini
    [Unit]
    Description=ChatBT Backend Service
    After=network.target

    [Service]
    User=your-user
    Group=your-group
    WorkingDirectory=/path/to/chatbt/chatbt-backend
    ExecStart=/usr/bin/python3 /path/to/chatbt/chatbt-backend/src/main_with_specialists.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

3.  **Enable and start the service:**

    ```bash
    sudo systemctl enable chatbt
    sudo systemctl start chatbt
    ```

### 4. Set up a Reverse Proxy (Nginx)

1.  **Install Nginx:**

    ```bash
    sudo apt-get update
    sudo apt-get install nginx
    ```

2.  **Create an Nginx configuration file:**

    ```bash
    sudo nano /etc/nginx/sites-available/chatbt
    ```

3.  **Add the following content to the file:**

    ```nginx
    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://localhost:5000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
    }
    ```

4.  **Enable the site:**

    ```bash
    sudo ln -s /etc/nginx/sites-available/chatbt /etc/nginx/sites-enabled
    ```

5.  **Test and restart Nginx:**

    ```bash
    sudo nginx -t
    sudo systemctl restart nginx
    ```

## 5. Access the Application

You should now be able to access the ChatBT application at `http://your-domain.com`.


