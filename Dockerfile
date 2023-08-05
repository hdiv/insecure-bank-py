FROM python:3.10-alpine

EXPOSE 8000

ADD . .

ENV PATH=".venv/bin:$PATH"

RUN apk add --no-cache tini
RUN python install
RUN python src/manage.py migrate

ENTRYPOINT [ "tini", "--" ]
CMD ["python", "src/manage.py",  "runserver", "0.0.0.0:8000"]
