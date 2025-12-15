# Server Deployment Guide

## Prerequisites
Before starting, it is required that the latest version of Node.js is installed on the machine.
Also, a valid API Key must be obtained from the dashboard.

## Configuration
The configuration file `config.json` is located in the root folder.
Changes can be made to this file to adjust the server port.

To apply the changes, the service must be restarted.

### Installation Steps

1. **Clone the repository:** The repository can be cloned using Git.
2. **Install dependencies:** The command `npm install` is run to download packages.
3. **Database Setup:** The migration script is executed to prepare the database tables.

> **Note:** Care should be taken when modifying the production database.

## Troubleshooting
If an error is encountered, the logs can be checked at `/var/log/app.log`.
The error message "Connection Refused" is usually caused by a firewall rule.

[Click here for more help](#support)