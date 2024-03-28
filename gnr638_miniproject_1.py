# -*- coding: utf-8 -*-
"""GNR638_MiniProject_1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BZHVi4uhbyzq-_Q0wDxymUCtVkoKlZrb
"""

from google.colab import drive
drive.mount('/content/drive')

import os
from PIL import Image
from os import listdir
from pathlib import Path
import torch
import torchvision
import torch.nn as nn
import torch.optim as optim
import numpy as np
import torch.nn.functional as F
from torchvision import models
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader, TensorDataset
import torchvision.transforms as tt
import matplotlib
import matplotlib.pyplot as plt
# %matplotlib inline
matplotlib.rcParams['figure.facecolor'] = '#ffffff'

# Load the model
X_train = torch.load('/content/drive/MyDrive/tensors/X_train_images.pt')
X_test = torch.load('/content/drive/MyDrive/tensors/X_test_images.pt')

y_train = torch.load('/content/drive/MyDrive/y_train.pt')
y_test = torch.load('/content/drive/MyDrive/y_test.pt')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print(X_train.size())
print(X_test.size())

batch_size = 32
train_ds = TensorDataset(X_train, y_train)
train_dl = DataLoader(train_ds, batch_size, shuffle=True)
test_ds = TensorDataset(X_test, y_test)
test_dl = DataLoader(test_ds, batch_size, shuffle=False)

print(y_train.size())
print(y_test.size())

class Identity(nn.Module):
    def _init_(self):
        super(Identity, self)._init_()

    def forward(self, x):
        return x

device = torch.device("cuda:0")

!pip install efficientnet_pytorch

from efficientnet_pytorch import EfficientNet
model_name = 'efficientnet-b2'

# Load the pre-trained model
model = EfficientNet.from_pretrained(model_name)

model.fc = nn.Linear(in_features=1024, out_features=32, bias=True)
model.to(device)

total_params = sum(p.numel() for p in model.parameters())
print(f"Total number of parameters: {total_params}")

# Define loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Define functions for training, validation, and testing
def train(model, train_loader, optimizer, criterion):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, torch.max(labels, 1)[1])
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == torch.max(labels, 1)[1]).sum().item()

    train_loss = running_loss / len(train_loader)
    train_accuracy = 100 * correct / total
    return train_loss, train_accuracy

def test(model, test_loader, criterion):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, torch.max(labels, 1)[1])

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == torch.max(labels, 1)[1]).sum().item()

    test_loss = running_loss / len(test_loader)
    test_accuracy = 100 * correct / total
    return test_loss, test_accuracy

# Train the model and collect data for plotting
num_epochs = 15
train_losses = []
train_accuracies = []
test_losses = []
test_accuracies = []

for epoch in range(num_epochs):
    train_loss, train_accuracy = train(model, train_dl, optimizer, criterion)
    test_loss, test_accuracy = test(model, test_dl, criterion)

    train_losses.append(train_loss)
    train_accuracies.append(train_accuracy)
    test_losses.append(test_loss)
    test_accuracies.append(test_accuracy)

    print(f"Epoch [{epoch + 1}/{num_epochs}], Train Loss: {train_loss:.4f}, Train Accuracy: {train_accuracy:.2f}%, Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.2f}%")

# Plotting
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(train_losses, label='Train Loss')
plt.plot(test_losses, label='Test Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(train_accuracies, label='Train Accuracy')
plt.plot(test_accuracies, label='Test Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy (%)')
plt.legend()

plt.show()

# saving the final model checkpoint

checkpoint_path = '/content/drive/MyDrive/model_checkpoint_efficientNet.pt'
torch.save(model.state_dict(), checkpoint_path)