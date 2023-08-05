# Insecure Bank (python)

![Insecure-Bank](https://hdivsecurity.com/img/bank.png)

## Running the application locally

1.  Clone the repository:

        $ git clone https://github.com/hdiv/insecure-bank-py.git

2.  Prepare python environment:

        $ python install
        $ . .venv/bin/activate
        $ python src/manage.py migrate 
        $ python src/manage.py runserver 

3.  You can then access the bank application here: http://localhost:8000

## Running with Docker

Run the insecure-bank application with Docker.

        $ docker build -t insecure-bank .
        $ docker run -p 8000:8000 -d --name insecure-bank-app insecure-bank
        $ docker logs insecure-bank-app

Open the application in > http://localhost:8000

## Login credentials

-   Username: john
-   Password: test
