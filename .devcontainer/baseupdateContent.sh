function preConfig() {
    sudo apt -y update
    sudo apt -y upgrade
    sudo apt-get install fzf eza tmux -y
    pip install --upgrade pip
    pip install -r backend/requirements.txt --user
}


function postConfig(){

    # Zsh plugins for syntax highlighting and autosuggestions
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
    git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

    # fzf-tab for improved tab completion in Zsh
    git clone https://github.com/Aloxaf/fzf-tab ~/fzf-tab

}
