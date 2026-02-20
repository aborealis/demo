FROM node:20.19.0-bullseye-slim
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y zsh git curl iputils-ping sed

# Обновляем npm до последней версии
RUN npm install -g npm@latest && \
    npm cache clean --force && \
    npm --version

# Устанавливаем zsh
COPY ./configs/install_zsh.sh /root
RUN /root/install_zsh.sh

RUN mkdir -p /code 
WORKDIR /code