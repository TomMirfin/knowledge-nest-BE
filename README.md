# Skillshare

This project is a Python application that controls a MongoDB database using the Render Python framework.
This is out back-end section of a final project for our Northcoders Bootcamp: 'SkillShare'.

Skillshare is a platform for people to connect over services provided/needed with a instant messaging service and posts to explore what type of skillset users are looking for.

The application uses FastAPI, Motor, Uvicorn, and Pydantic libraries.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)

## Requirements

- fastapi==0.104.1
- motor==3.3.1
- uvicorn==0.23.2
- pydantic[email]==2.4.2

## Installation

Clone the repository and install the requirements:

```bash
pip install -r requirements.in
```

Inside the root directory, create a .env file with the following:

MONGO_DETAILS= < INSERT-OWN-DATABASE >

