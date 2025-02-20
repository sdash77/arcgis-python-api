# init conda shell
conda init --all

# create geosaurus_dev_env with all dependencies for ./src
conda env create --file environment.yml --yes

# set default environment on terminal load
echo "conda activate geosaurus_dev_env" >> .bashrc
echo "conda activate geosaurus_dev_env" >> .zshrc

# reload terminal config
. ~/.bashrc

# install src package
python -m pip install ./src --no-deps