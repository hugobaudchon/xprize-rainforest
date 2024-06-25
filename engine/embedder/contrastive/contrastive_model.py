import math

import torch
from torch import nn
from torchvision import models


class XPrizeTreeEmbedder(nn.Module):
    def __init__(self,
                 resnet_model: str,
                 final_embedding_size: int,
                 dropout: float):
        super(XPrizeTreeEmbedder, self).__init__()
        # Load a ResNet50 model pre-trained on ImageNet
        if resnet_model == 'resnet50':
            self.backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        elif resnet_model == 'resnet101':
            self.backbone = models.resnet101(weights=models.ResNet101_Weights.DEFAULT)
        elif resnet_model == 'resnet152':
            self.backbone = models.resnet152(weights=models.ResNet152_Weights.DEFAULT)
        else:
            raise ValueError(f'Invalid resnet model: {resnet_model}')

        self.final_embedding_size = final_embedding_size

        # Remove the final fully connected layer
        self.backbone.fc = nn.Identity()

        # Adding a new fully connected layer to create embeddings
        self.fc = nn.Sequential(
            nn.Linear(2048 + 4, 1536),
            nn.ReLU(),
            nn.Dropout(p=dropout),
            nn.Linear(1536, self.final_embedding_size),
        )

    @staticmethod
    def _get_date_encoding(month, day):
        # Sinusoidal encoding for month
        month_sin = torch.sin(2 * math.pi * month / 12).unsqueeze(1)
        month_cos = torch.cos(2 * math.pi * month / 12).unsqueeze(1)

        # Sinusoidal encoding for day
        day_sin = torch.sin(2 * math.pi * day / 31).unsqueeze(1)
        day_cos = torch.cos(2 * math.pi * day / 31).unsqueeze(1)

        # Concatenate in a single tensor of size batch_size x 4
        date_encodings = torch.cat((month_sin, month_cos, day_sin, day_cos), dim=1)

        return date_encodings

    def forward(self, x, month, day):
        output = self.backbone(x)
        date_encoding = self._get_date_encoding(month, day)
        embeddings_concat = torch.cat((output, date_encoding), dim=1)
        embeddings_final = self.fc(embeddings_concat)
        return embeddings_final


class XPrizeTreeEmbedder2(nn.Module):
    def __init__(self,
                 resnet_model: str,
                 final_embedding_size: int,
                 dropout: float,
                 families: list[str],
                 date_embedding_dim: int = 32):
        super(XPrizeTreeEmbedder2, self).__init__()
        # Load a ResNet50 model pre-trained on ImageNet
        if resnet_model == 'resnet50':
            self.backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        elif resnet_model == 'resnet101':
            self.backbone = models.resnet101(weights=models.ResNet101_Weights.DEFAULT)
        elif resnet_model == 'resnet152':
            self.backbone = models.resnet152(weights=models.ResNet152_Weights.DEFAULT)
        else:
            raise ValueError(f'Invalid resnet model: {resnet_model}')

        self.final_embedding_size = final_embedding_size

        # Remove the final fully connected layer
        self.backbone.fc = nn.Identity()

        # Embedding layers for month and day
        self.month_embedding = nn.Embedding(12, date_embedding_dim)
        self.day_embedding = nn.Embedding(31, date_embedding_dim)

        # Adding a new fully connected layer to create embeddings
        self.fc = nn.Sequential(
            nn.Linear(2048 + 2 * date_embedding_dim, 1536),
            nn.ReLU(),
            nn.Dropout(p=dropout),
            nn.Linear(1536, 1280),
            nn.ReLU(),
            nn.Dropout(p=dropout),
            nn.Linear(1280, self.final_embedding_size),
        )

        self.families = families
        self.families_to_id_mapping = {family: i for i, family in enumerate(families)}
        self.ids_to_families_mapping = {i: family for i, family in enumerate(families)}
        self.family_classifier = nn.Linear(self.final_embedding_size, len(families))

        print('model families_to_id_mapping:', self.families_to_id_mapping)

    def _get_date_encoding(self, month, day):
        # Sinusoidal encoding for month. Expects month to be in [1, 12] and day to be in [1, 31]
        month_embedding = self.month_embedding(month - 1)
        day_embedding = self.day_embedding(day - 1)

        # Concatenate in a single tensor of size batch_size x 4
        date_encodings = torch.cat((month_embedding, day_embedding), dim=1)
        return date_encodings

    def forward(self, x, month, day):
        output = self.backbone(x)
        date_encoding = self._get_date_encoding(month, day)
        embeddings_concat = torch.cat((output, date_encoding), dim=1)
        embeddings_final = self.fc(embeddings_concat)
        classification_logits = self.family_classifier(embeddings_final)
        return embeddings_final, classification_logits

    def save(self, path):
        torch.save({
            'model_state_dict': self.state_dict(),
            'families': self.families,
            'resnet_model': 'resnet50',
            'final_embedding_size': 1024,
            'dropout': 0.5
        }, path)

    @classmethod
    def from_checkpoint(cls,
                        checkpoint_path):
        checkpoint = torch.load(checkpoint_path)

        model = cls(resnet_model=checkpoint['resnet_model'],
                    final_embedding_size=checkpoint['final_embedding_size'],
                    dropout=checkpoint['dropout'],
                    families=checkpoint['families'])
        model.load_state_dict(checkpoint['model_state_dict'])
        return model

