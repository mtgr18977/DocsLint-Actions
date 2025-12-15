# Deployment Guidelines

This document outlines how the application is deployed to production.

## Prerequisites

Before the installation is started, the following requirements must be met:

Node.js: It is required that Node.js v18 is installed.

Database: A PostgreSQL instance must be provisioned by the infrastructure team.

Permissions: Root access is needed for the initial setup.

## Installation Steps

The repository can be cloned using the standard Git command.
Once the files are downloaded, the dependencies are installed by running npm install.

. Note: The environment variables must be configured before the application is started.

## Configuration

The configuration file config.yaml is found in the root directory.
Changes can be made to this file to adjust the port settings.
If an error is encountered, the logs should be checked immediately.

[Click here for more details]()