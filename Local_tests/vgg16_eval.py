
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models

# Set device to GPU if available, otherwise use CPU
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Define transformations for the dataset
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # VGG16 expects input size of 224x224
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# Load CIFAR-10 test dataset
testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                       download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=32,
                                         shuffle=False, num_workers=2)

# Load pre-trained VGG16 model
vgg16 = models.vgg16(pretrained=True)

# Freeze convolutional layers
for param in vgg16.features.parameters():
    param.requires_grad = False

# Modify the last fully connected layer for 10 classes
vgg16.classifier[6] = nn.Linear(4096, 10)

# Send model to GPU
vgg16 = vgg16.to(device)

# Test the model
correct = 0
total = 0
with torch.no_grad():
    for data in testloader:
        images, labels = data[0].to(device), data[1].to(device)
        outputs = vgg16(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print('Accuracy of the pre-trained VGG16 model on the 10000 test images: %d %%' % (
    100 * correct / total))
