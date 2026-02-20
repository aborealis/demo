#!/bin/bash

# Проверяем, установлен ли zsh
if command -v zsh >/dev/null 2>&1; then
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
    cp /root/.oh-my-zsh/templates/zshrc.zsh-template /root/.zshrc
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "/root/.zsh-syntax-highlighting" --depth 1
    echo "source /root/.zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" >> "/root/.zshrc"
    git clone https://github.com/zsh-users/zsh-autosuggestions /root/.oh-my-zsh/custom/plugins/zsh-autosuggestions
    sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions)/' ~/.zshrc
    chsh -s /usr/bin/zsh root
fi