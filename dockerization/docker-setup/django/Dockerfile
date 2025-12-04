FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get upgrade -y 
RUN apt-get install -y mariadb-server gcc libmariadb-dev
RUN apt-get install -y pkg-config libpcre3 libpcre3-dev zsh git wget
RUN rm -rf /var/lib/apt/lists/*

# Prepare Django start script
COPY configs/start.sh /root/start.sh
RUN chmod +x /root/start.sh

# Install z-shell for the root user
RUN git clone https://github.com/robbyrussell/oh-my-zsh.git /root/.oh-my-zsh
RUN git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "/root/.zsh-syntax-highlighting" --depth 1
RUN git clone https://github.com/zsh-users/zsh-autosuggestions /root/.oh-my-zsh/custom/plugins/zsh-autosuggestions
COPY configs/.zshrc /root/.zshrc
RUN chsh -s /usr/bin/zsh root

# Install requirements
COPY configs/requirements.txt /root
RUN pip install --no-cache-dir --root-user-action=ignore --upgrade pip
RUN pip install --no-cache-dir --root-user-action=ignore -r /root/requirements.txt 

ENV PATH=$PATH:/root/.local/bin
RUN mkdir /code
WORKDIR /code
