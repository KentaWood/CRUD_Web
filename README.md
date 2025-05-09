# CRUD_Web
[![Docker-Web](https://github.com/KentaWood/CRUD_Web/actions/workflows/docker-image.yml/badge.svg)](https://github.com/KentaWood/CRUD_Web/actions/workflows/docker-image.yml)
[![Docker-Web-Prod](https://github.com/KentaWood/CRUD_Web/actions/workflows/docker-compose.prod.yml/badge.svg)](https://github.com/KentaWood/CRUD_Web/actions/workflows/docker-compose.prod.yml)


## Currently Running on AWS EC2

The application can be accessed here: (Currently not deployed anymore as of 5/9/2025).

- Make an account and post some tweets! It's always good to get authenticated user data into the application!


## Description

This project is a web application built using Flask and SQLAlchemy, containerized with Docker. It includes features for user authentication, tweet creation, and tweet search. The application is structured to separate development and production environments using Docker Compose.

## Technologies Used

- **Python**: 3.11.3
- **Flask**: Micro web framework
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **PostgreSQL**: Relational database
- **Docker**: Containerization platform
- **Nginx**: Web server

## Testing & Web Development Practices

- Created test badges to check every time code is pushed if any configuration of the Web App is affected.
- Utilized SQL indexes to efficiently query through 10 million+ rows of data, ensuring that queries and the website are responsive in a reasonable time.


## Setup Instructions

### Prerequisites

- Docker installed on your machine
- Docker Compose installed on your machine

### Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### Environment Variables

Create a `.env.dev` file in the project root directory with the necessary environment variables:

```bash
DATABASE_URL=postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev
```

### Build and Run the Project

Build and start the services using Docker Compose:

```bash
docker-compose up --build
```

This command will:

1. Build the Docker images defined in `docker-compose.yml`.
2. Start the PostgreSQL database, Flask application, and Nginx server.

### Accessing the Application

- Open your web browser and go to `http://localhost:5000` to access the Flask application.

## Project Components

### Flask Application

The Flask application is located in the `web` directory. It includes:

- User authentication
- Tweet creation
- Tweet search

### Database

The database configuration and migration files are located in the `db` directory.

### Nginx

Nginx is used as a reverse proxy to serve the Flask application. Configuration files are located in the `nginx` directory.

## Development

### Installing Dependencies

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application Locally

To run the Flask application locally without Docker, use the following commands:

```bash
export FLASK_APP=web/app.py
export FLASK_ENV=development
flask run
```

### Running Tests

To run the tests, use the following command:

```bash
pytest
```

## Deployment

For production deployment, use the `docker-compose.prod.yml` file:

```bash
docker-compose -f docker-compose.prod.yml up --build
```

This will start the services with the production configurations.

