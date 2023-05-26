import torch
import torch.nn as nn


class _TSLSTM(nn.Module):
    def __init__(self, input_size=1, output_size=1, device=None, hidden_layer_size=100, num_layers=1, dropout=0.2):
        super(_TSLSTM, self).__init__()
        self.device = device
        self.input = input_size
        self.hidden = hidden_layer_size
        self.num_layers = num_layers
        if self.num_layers > 1:
            self.lstm = nn.LSTM(
                input_size=self.input,
                hidden_size=self.hidden,
                num_layers=self.num_layers,
                batch_first=True,
                bidirectional=True,
                dropout=dropout
            )
        else:
            self.lstm = nn.LSTM(
                input_size=self.input,
                hidden_size=self.hidden,
                num_layers=self.num_layers,
                batch_first=True,
                bidirectional=True,
            )
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(2 * self.hidden, output_size)

    def forward(self, input_seq):
        input_seq = input_seq.permute(0, 2, 1)
        batch_size = input_seq.size(0)
        x = input_seq.to(torch.float)
        h0 = torch.zeros(2 * self.num_layers, batch_size, self.hidden).to(
            self.device
        )
        c0 = torch.zeros(2 * self.num_layers, batch_size, self.hidden).to(
            self.device
        )
        out, (h0, c0) = self.lstm(x, (h0, c0))
        h_comb = torch.cat(
            [h0[: self.num_layers], h0[self.num_layers:]], dim=-1
        )[-1]
        outputs = self.linear(h_comb)
        return outputs.to(self.device)
