FROM python:3.9.19-slim-bullseye
RUN apt-get update && apt-get upgrade -y 
RUN apt-get install -y mariadb-server gcc libmariadb-dev
RUN apt-get install -y pkg-config libpcre3 libpcre3-dev zsh git wget
RUN apt-get install -y gzip make gettext

RUN mkdir /code 
RUN git clone https://github.com/robbyrussell/oh-my-zsh.git /root/.oh-my-zsh
RUN git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "/root/.zsh-syntax-highlighting" --depth 1
RUN git clone https://github.com/zsh-users/zsh-autosuggestions /root/.oh-my-zsh/custom/plugins/zsh-autosuggestions
COPY configs/.zshrc /root/.zshrc
RUN chsh -s /usr/bin/zsh root

ENV PATH $PATH:/root/.local/bin
COPY configs/requirements.txt /root
RUN pip install --no-cache-dir --root-user-action=ignore --upgrade pip
RUN pip install --no-cache-dir --root-user-action=ignore -r /root/requirements.txt 
WORKDIR /code

COPY configs/uwsgi.ini /root
RUN touch /root/reload.ini


