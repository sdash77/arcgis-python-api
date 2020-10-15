from typing import Collection
import fastai
import fastai.data_block
from fastai.core import array

if fastai.__version__=='1.0.60':
    def process(self, ds:Collection):
        ds.items = array([self.process_one(item) for item in ds.items], dtype=object)
    fastai.data_block.PreProcessor.process = process

precondition = True
