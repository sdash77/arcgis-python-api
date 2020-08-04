import re
import traceback
import collections

HAS_TRANSFORMER = True

try:
    from transformers import PreTrainedTokenizer
    from fastai.text import List, BaseTokenizer, Vocab, Collection
except Exception as e:
    transformer_exception = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))
    HAS_TRANSFORMER = False

    class BaseTokenizer:
        pass

    class Vocab:
        pass


class TransformersBaseTokenizer(BaseTokenizer):
    """
    Wrapper around PreTrainedTokenizer to be compatible with fast.ai
    """
    def __init__(self, pretrained_tokenizer: PreTrainedTokenizer, lang="en", seq_len=512, **kwargs):
        super().__init__(lang)
        self._pretrained_tokenizer = pretrained_tokenizer
        self._seq_len = seq_len
        self.max_seq_len = min(pretrained_tokenizer.model_max_length, self._seq_len)

    def __call__(self, *args, **kwargs):
        return self

    # new improved tokenizer wich can support any transformer model
    def tokenizer(self, t:str) -> List[str]:
        ids = self._pretrained_tokenizer.encode(t, max_length=self.max_seq_len)
        tokens = self._pretrained_tokenizer.convert_ids_to_tokens(ids)
        return tokens


class TransformersVocab(Vocab):
    """
    Contain the correspondence between numbers and tokens and numericalize.
    """
    def __init__(self, tokenizer: PreTrainedTokenizer):
        super().__init__(itos=[])
        self.tokenizer = tokenizer
        self.special_token_map = self.tokenizer.special_tokens_map
        self.has_cls_token = True if self.special_token_map.get('cls_token') else False
        self.has_sep_token = True if self.special_token_map.get('sep_token') else False
        self.has_unk_token = True if self.special_token_map.get('unk_token') else False
        self.has_pad_token = True if self.special_token_map.get('pad_token') else False

    def numericalize(self, t: Collection[str]) -> List[int]:
        """
        Convert a list of tokens `t` to their ids.
        """
        return self.tokenizer.convert_tokens_to_ids(t)

    def textify(self, nums: Collection[int], sep=' ') -> str:
        """
        Convert a list of `nums` to their tokens.
        """
        # text = self.tokenizer.decode(nums, skip_special_tokens=True)
        text = self.tokenizer.decode(nums)
        if self.has_cls_token: text = text.replace(self.tokenizer.cls_token, '')
        if self.has_sep_token: text = text.replace(self.tokenizer.sep_token, '')
        if self.has_unk_token: text = text.replace(self.tokenizer.unk_token, '')
        if self.has_pad_token: text = text.replace(self.tokenizer.pad_token, '')
        text = re.sub(' +', ' ', text)
        return text.strip()

    def __getstate__(self):
        return {'itos': self.itos, 'tokenizer': self.tokenizer}

    def __setstate__(self, state: dict):
        self.itos = state['itos']
        self.tokenizer = state['tokenizer']
        self.stoi = collections.defaultdict(int, {v: k for k, v in enumerate(self.itos)})
