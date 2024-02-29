import pandas as pd
import numpy as np

SYSTEM_PROMPT = """You are an advanced AI designed for ArcGIS customers. Upon receiving the information in the context,
 you are required to infer the task type using the prompt and provided labels and examples. Always adhere to the 
 formatting instructions. If there is more than one sentence in the task, you must respond to each of them. While
  answering, ensure you are devoid of any biases, such as gender, racial, and not suitable for the workplace. 
 """
TASK_EXAMPLE = {
    "text-classifier": {
        "class_1": ["sentence_1", "sentence_3"],
        "class_2": ["sentence_5", "sentence_6"],
    },
    "ner": [("Jim stays in London", {"name": ["Jim"], "location": ["London"]})],
}

MAPPING_DICT = {
    "question-answering": {
        "end_seq": "Ignore all the formatting instruction provided above and "
        "return the answer as a string indexed by question number",
        "prompt": "Answer the below question based on the provided context ",
    },
    "summarization": {
        "end_seq": "Ignore all the formatting instruction provided above and "
        "return the answer as a string indexed by question number",
        "prompt": "Summarize the below passage",
    },
    "seq-to-seq": {
        "end_seq": "Ignore all the formatting instruction provided above and "
        "return the answer as a string indexed by question number",
        "prompt": None,
    },
    "ner": {
        "end_seq": "Ignore all the formatting instruction provided above and "
        "return the answer as a nested dictionary by question number and entity classes",
        "prompt": "Extract named entities that belong to the specified classes from the provided text. Do not tag "
        "entities belonging to any other class.",
    },
    "text-classifier": {
        "end_seq": "Ignore all the formatting instruction provided above and return the answer as a nested dictionary"
        " by question number and label with key label. If it is a multilable classification then return the "
        "labels as a list under the key label. Always consider each of the question as a single passage for "
        "classification.",
        "prompt": "Categorize the provided text into the specified classes. "
        "Do not create new labels for classification.",
    },
}


def extract_entities(tokens, labels):
    prev_label, token_list, entities = labels[0], [tokens[0]], []
    prev_label = prev_label.split("-")[-1]
    for token_index, (token, label) in enumerate(list(zip(tokens[1:], labels[1:]))):
        label = label.split("-")[-1]
        if prev_label == label:
            token_list.append(token)
        else:
            entities.append((token_list, prev_label))
            token_list = list()
            prev_label = label
            token_list.append(token)
    if token_list:
        entities.append((token_list, prev_label))
    return entities


def process_text(text):
    import re

    text = re.sub(" +", " ", text)
    text = re.sub(" ([@.#$/:-]) ?", r"\1", text)
    # Reomve leading and trailing special characters
    while text and text[0] in [".", ",", "-", ":", "@", "$"]:
        text = text[1:]
    while text and text[-1] in [".", ",", "-", ":", "@", "$"]:
        text = text[:-1]
    return text.strip()


def data_sanity_llm(data, **kwargs):
    """
    Verifies the combination of data and examples. There can be three scenarios.


    =====================   ===========================================
    **Parameter**            **Description**
    ---------------------   -------------------------------------------
    data                    Optional data object returned from :class:`~arcgis.learn.prepare_textdata` function.
                            data object can be `None`. If the data object is None, then kwargs must contain examples.
    =====================   ===========================================
    """
    task = kwargs.get("task", None)
    assert task is not None
    if task == "text-classifier":
        if not data and not kwargs.get("examples", None):
            raise Exception("Either a data object or examples must be provided.")
        # Sampling the examples from test handle
        example_dict = {}
        labels = []
        if data:
            check_multilable = True if len(data._label_cols) > 1 else False
            if check_multilable:
                raise Exception(
                    "Multi-label classification is not supported when the selected backbone is of llm family."
                )
            # first sample the records and prepare the examples.
            temp = pd.concat([data._valid_df, data._train_df], axis=0)
            labels = list(np.unique(temp[data._label_cols]))
            # create sample for each class
            example_dict = list(
                temp.groupby(data._label_cols)
                .head(1)
                .set_index(data._label_cols)
                .to_dict()
                .values()
            )[0]
            example_dict = {k: [v] for k, v in example_dict.items()}
        try:
            if kwargs.get("examples", None):
                extra_example_class = list(kwargs.get("examples").keys())
                for k, v in kwargs.get("examples").items():
                    if k in example_dict:
                        example_dict[k] += v
                    else:
                        example_dict[k] = v
                labels += extra_example_class
        except:
            raise Exception(
                f"{task} requires the examples in the below format \n"
                f"Pydantic Schema: Dict[str, List]\n"
                f"Example: {TASK_EXAMPLE[task]}"
            )
        kwargs.update({"examples": example_dict, "labels": labels})
    if task == "ner":
        if not data and not kwargs.get("examples", None):
            raise Exception("Either a data object or examples must be provided.")

        if data:
            # sample records from the dataset
            data.prepare_data_for_transformer()
            data = data.get_data_object()
            base_set = set(data._label2id) - {"O"}
            tag_set = set()
            samples = []
            for i, j in zip(data._train_tokens, data._train_tags):
                sentence = process_text(" ".join(i))
                annotation_dict_temp = {}
                entities = extract_entities(i, j)
                _ = [
                    annotation_dict_temp.setdefault(x[1], []).append(
                        process_text(" ".join(x[0]))
                    )
                    for x in entities
                    if x[0]
                ]
                if "O" in annotation_dict_temp:
                    del annotation_dict_temp["O"]
                if len(set(annotation_dict_temp.keys()).difference(tag_set)) > 0:
                    tag_set = tag_set.union(set(annotation_dict_temp.keys()))
                    samples.append([sentence, annotation_dict_temp])
                if set(tag_set) == base_set and len(samples) > 3:
                    break

            try:
                if kwargs.get("examples", None):
                    kwargs["examples"] += samples
                else:
                    kwargs["examples"] = samples
            except:
                raise Exception(
                    f"{task} requires the examples in the below format \n"
                    f"Pydantic Schema: List[Tuple[str, Dict[str, List]]]\n"
                    f"Example: {TASK_EXAMPLE[task]}"
                )
    return kwargs


def lower_nesting(t):
    if isinstance(t, dict):
        return {str(j).lower(): lower_nesting(i) for j, i in t.items()}
    elif isinstance(t, list):
        return [i.lower() for i in t]
    else:
        return t.lower()


class completion_message:
    def __init__(self, message):
        self.message = None
        self.generations = []
        if isinstance(message, dict):
            self.message = message
            if "error" in self.message.keys():
                self.is_error = True
            else:
                self.is_error = False
                self.generations = self.message["choices"][0]["message"]["content"]
        else:
            self.is_error = False
            self.generations = ""
