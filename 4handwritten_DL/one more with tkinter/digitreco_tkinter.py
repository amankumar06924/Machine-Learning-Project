import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST(root='./data', train=True, transform=transform, download=True)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)

class DigitNN(nn.Module):
    def __init__(self):
        super(DigitNN, self).__init__()
        self.fc1 = nn.Linear(28 * 28, 128)
        self.fc2 = nn.Linear(128, 32)
        self.fc3 = nn.Linear(32, 10)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = DigitNN().to(device)
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()
model.train()
for epoch in range(10):
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1}/10 completed")

model.eval()
print("Model trained successfully! Opening GUI...")
class DigitRecognizerApp:
    def __init__(self, root, model):
        self.root = root
        self.model = model
        self.root.title("Draw Digit & Predict")
        self.root.resizable(False, False)
        self.canvas_size = 280
        self.heading = tk.Label(root, text="Draw a digit (0 - 9) in the black box:", font=("Arial", 14, "bold"))
        self.heading.pack(pady=10)
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg="black", cursor="cross")
        self.canvas.pack(pady=5)
        self.image = Image.new("L", (self.canvas_size, self.canvas_size), color=0)
        self.draw = ImageDraw.Draw(self.image)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.result_label = tk.Label(root, text="Prediction: None", font=("Arial", 16, "bold"), fg="blue")
        self.result_label.pack(pady=10)
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.btn_predict = tk.Button(btn_frame, text="Predict", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=10, command=self.predict_digit)
        self.btn_predict.grid(row=0, column=0, padx=10)

        self.btn_clear = tk.Button(btn_frame, text="Clear", font=("Arial", 12, "bold"), bg="#f44336", fg="white", width=10, command=self.clear_canvas)
        self.btn_clear.grid(row=0, column=1, padx=10)

    def paint(self, event):
        brush_radius = 10
        x1, y1 = (event.x - brush_radius), (event.y - brush_radius)
        x2, y2 = (event.x + brush_radius), (event.y + brush_radius)
        self.canvas.create_oval(x1, y1, x2, y2, fill="white", outline="white")
        self.draw.ellipse([x1, y1, x2, y2], fill=255, outline=255)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("L", (self.canvas_size, self.canvas_size), color=0)
        self.draw = ImageDraw.Draw(self.image)
        self.result_label.config(text="Prediction: None", fg="blue")

    def predict_digit(self):
        img_resized = self.image.resize((28, 28), Image.Resampling.LANCZOS)
        img_array = np.array(img_resized) / 255.0
        img_tensor = torch.from_numpy(img_array).float().unsqueeze(0).unsqueeze(0)
        with torch.no_grad():
            output = self.model(img_tensor)
            probabilities = torch.nn.functional.softmax(output, dim=1)[0]
            predicted_class = torch.argmax(probabilities).item()
            confidence = probabilities[predicted_class].item() * 100
        self.result_label.config(
            text=f"Prediction: {predicted_class}  ({confidence:.1f}%)", 
            fg="green"
        )
if __name__ == "__main__":
    root = tk.Tk()
    app = DigitRecognizerApp(root, model)
    root.mainloop()