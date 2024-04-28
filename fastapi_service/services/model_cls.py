import io

from fastapi_service.services.models_loader import get_torch_models

from transformers import AutoTokenizer, AutoModel
import torch

import torch.nn as nn


class BertClassification(nn.Module):
    def __init__(self, model, tokenizer):
        super().__init__()

        self.tokenizer = tokenizer

        self.bert = model
        for param in self.bert.parameters():
            param.requires_grad = False
        self.inform = nn.Linear(312, 2)
        self.tonal = nn.Linear(312, 2)
        self.obj = nn.Linear(312, 3)

    def forward(self, x):
        out = self.bert(input_ids=x['input_ids'], attention_mask=x['attention_mask'])['last_hidden_state'][:, 0]
        inf = self.inform(out)
        ton = self.tonal(out)
        obj = self.obj(out)
        return inf, ton, obj

    def infer(self, data):
        quest_name = ['Название вебинара: ', ' Понравилось: ', ' Сложные моменты: ', ' Что можно улушить: ',
                      ' Чтобы хотелось узнать: ']
        s = ''
        for i, (key, value) in enumerate(data.items()):
            s += quest_name[0] + value

        texts = [s]
        s_tokens = self.tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
        out = self.bert(input_ids=s_tokens['input_ids'], attention_mask=s_tokens['attention_mask'])[
                  'last_hidden_state'][:, 0]
        inf = self.inform(out).argmax(dim=1)
        ton = self.tonal(out).argmax(dim=1)
        obj = self.obj(out).argmax(dim=1)
        data['is_positive'] = int(ton)
        data['is_relevant'] = int(inf)
        data['object'] = int(obj)
        return data


device = 'cuda' if torch.cuda.is_available() else 'cpu'

tokenizer = AutoTokenizer.from_pretrained("cointegrated/rubert-tiny2")
model = AutoModel.from_pretrained("cointegrated/rubert-tiny2")

bert = BertClassification(model, tokenizer).to(device)
bert.load_state_dict(torch.load(io.BytesIO(get_torch_models()), map_location=device))


def infer_model(data):
    with torch.no_grad():
        data = bert.infer(data)
    return data
