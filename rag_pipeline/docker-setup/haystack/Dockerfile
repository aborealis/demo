# -------- BUILDER --------
FROM python:3.14-slim-bookworm AS builder

COPY configs/requirements.txt /root
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --root-user-action=ignore -r /root/requirements.txt 
RUN apt-get update && apt-get install -y --no-install-recommends libatomic1 postgresql-client && rm -rf /var/lib/apt/lists/*

COPY configs/alembic_init.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/alembic_init.sh
COPY ./configs/alembic_env.py /root
WORKDIR /code

# -------- PRODUCTION --------
FROM builder AS production
ENV PATH=/root/.local/bin:$PATH

ENTRYPOINT ["alembic_init.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]

# -------- DEV --------
FROM builder AS dev
ENV PATH=/root/.local/bin:$PATH

RUN apt-get update && apt-get install git zsh screen curl sed -y
COPY ./configs/install_zsh.sh /root
RUN /root/install_zsh.sh

ENTRYPOINT ["alembic_init.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]




