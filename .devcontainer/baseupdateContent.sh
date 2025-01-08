function preConfig() {
    sudo apt -y update
    sudo apt -y upgrade
    sudo apt-get install graphviz fzf exa tmux -y
    pip install --upgrade pip
    pip install -r backend/requirements.txt --user
}


function postConfig(){

    # Pre-commit hooks
    pre-commit install

    # Java (needed for pyspark unittests)
    # sudo apt install default-jre -y

    # Zsh plugins for syntax highlighting and autosuggestions
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
    git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

    # GitHub CLI extensions
    gh extension install https://github.com/nektos/gh-act
    gh extension install github/gh-copilot

    # Gitleaks for detecting secrets in source code
    curl -Lo ./gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.18.4/gitleaks_8.18.4_linux_x64.tar.gz
    tar -xzf ./gitleaks.tar.gz
    chmod +x ./gitleaks
    sudo mv gitleaks /usr/bin/gitleaks
    export PATH=$PATH:/usr/bin/gitleaks

    # Neovim text editor
    curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim-linux64.tar.gz
    sudo rm -rf /opt/nvim
    sudo tar -C /opt -xzf nvim-linux64.tar.gz
    rm nvim-linux64.tar.gz
    export PATH=$PATH:/opt/nvim-linux64/bin

    # fzf-tab for improved tab completion in Zsh
    git clone https://github.com/Aloxaf/fzf-tab ~/fzf-tab

     # LazyGit for terminal-based Git UI
    LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
    curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
    tar xf lazygit.tar.gz lazygit
    sudo install lazygit /usr/local/bin
    rm lazygit.tar.gz lazygit

    # Git Large File Storage: extension for managing large files in Git repositories
    sudo apt-get update
    sudo apt-get install -y git-lfs
    git lfs install

    # Add a post-merge hook installing packages in requirements.txt
    if [ ! -f .git/hooks/post-merge ]; then
        echo "post-merge hook does not exist. Creating one..."
        mkdir -p .git/hooks/
        echo '#!/bin/bash' > .git/hooks/post-merge
        chmod +x .git/hooks/post-merge
    fi
    echo "# installs packages after a merge" >> .git/hooks/post-merge
    echo 'pip install -q -r requirements.txt --user' >> .git/hooks/post-merge

}
