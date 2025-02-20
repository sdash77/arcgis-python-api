# init conda shell
conda init --all

# create geosaurus_dev_env with all dependencies for ./src
conda env create --file environment.yml --yes

# set default environment on terminal load
echo "conda activate geosaurus_dev_env" >> ~/.bashrc
echo "conda activate geosaurus_dev_env" >> ~/.zshrc

# force init of conda shell in this script
# (conda init requires the shell to be restarted to take effect)
eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"

# install src package
conda activate geosaurus_dev_env && python -m pip install ./src --no-deps