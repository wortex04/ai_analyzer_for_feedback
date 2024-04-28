from transformers import GenerationConfig
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm.auto import tqdm

generation_config = GenerationConfig.from_pretrained('IlyaGusev/saiga_llama3_8b')
tokenizer = AutoTokenizer.from_pretrained("IlyaGusev/saiga_llama3_8b")
model = AutoModelForCausalLM.from_pretrained("IlyaGusev/saiga_llama3_8b")


def summarization(data):
    generation_config = GenerationConfig.from_pretrained('IlyaGusev/saiga_llama3_8b')

    data = data[data.is_relevant == 1]
    quest_name = ['Название вебинара: ', ' Понравилось: ', ' Сложные моменты: ', ' Что можно улушить: ',
                  ' Чтобы хотелось узнать: ']

    uniq_v = data.question_1.unique()
    answer = {}

    for val in uniq_v:
        data_val = data[data.question_1 == val]
        data_dict = []
        for row in tqdm(data_val.iterrows()):
            row = row[1]
            s = quest_name[0] + row.question_1 + quest_name[1] + row.question_2 + quest_name[2] + row.question_3 + \
                quest_name[3] + row.question_4 + quest_name[4] + row.question_5
            data_dict.append(s)
        all_comments = '\n'.join(data_dict)
        pattern = 'Напиши кратко все плюсы, минусы, сложные моменты, котрые описываются по пункатм и также суммаризируй: \n' + all_comments
        data_val = tokenizer(pattern, return_tensors="pt")
        data_val = {k: v.to(model.device) for k, v in data_val.items() if k in ("input_ids", "attention_mask")}
        output_ids = model.generate(**data_val, generation_config=generation_config)[0]
        output_ids = output_ids[len(pattern):]
        answer[val] = output_ids
    return answer
