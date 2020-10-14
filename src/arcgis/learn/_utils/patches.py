from typing import Collection
import fastai.data_block
from fastai.core import array

## Fastai Pacthes Start ##
def process(self, ds:Collection):
    ds.items = array([self.process_one(item) for item in ds.items], dtype=object)
fastai.data_block.PreProcessor.process = process
## Fastai Pacthes END ##


precondition = True
