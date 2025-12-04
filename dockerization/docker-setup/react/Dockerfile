FROM node:20.19.0-bullseye-slim
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y zsh git curl iputils-ping
RUN npm install --location=global sass
RUN npm install --location=global nodemon
RUN npm install --location=global vite

RUN usermod --shell /bin/zsh root
RUN git clone https://github.com/robbyrussell/oh-my-zsh.git /root/.oh-my-zsh
RUN git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "/root/.zsh-syntax-highlighting" --depth 1
RUN git clone https://github.com/zsh-users/zsh-autosuggestions /root/.oh-my-zsh/custom/plugins/zsh-autosuggestions
COPY configs/.zshrc /root