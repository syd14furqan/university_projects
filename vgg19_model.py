#install this lib
"""pip install torch torchvision pillow"""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, models
from PIL import Image
import matplotlib.pyplot as plt

# Load and preprocess images
def load_image(image_path, max_size=400, shape=None):
    image = Image.open(image_path).convert('RGB')

    # Resize the image
    size = max_size if max(image.size) > max_size else max(image.size)
    if shape:
        size = shape

    in_transform = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])

    image = in_transform(image)[:3, :, :].unsqueeze(0)

    return image

# Display tensor as image
def im_convert(tensor):
    image = tensor.to("cpu").clone().detach()
    image = image.numpy().squeeze()
    image = image.transpose(1, 2, 0)
    image = image * (0.229, 0.224, 0.225) + (0.485, 0.456, 0.406)
    image = image.clip(0, 1)

    return image

# Load VGG19 model
vgg = models.vgg19(pretrained=True).features

# Freeze parameters
for param in vgg.parameters():
    param.requires_grad_(False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
vgg.to(device)

# Define the content and style layers
def get_features(image, model, layers=None):
    if layers is None:
        layers = {'0': 'conv1_1', '5': 'conv2_1', '10': 'conv3_1', '19': 'conv4_1', '21': 'conv4_2', '28': 'conv5_1'}

    features = {}
    x = image
    for name, layer in model._modules.items():
        x = layer(x)
        if name in layers:
            features[layers[name]] = x

    return features

# Gram matrix to measure style
def gram_matrix(tensor):
    _, d, h, w = tensor.size()
    tensor = tensor.view(d, h * w)
    gram = torch.mm(tensor, tensor.t())

    return gram

# Load content and style images
content = load_image('/content/content.jpg.png').to(device)
style = load_image('/content/style.jpg.png', shape=content.shape[-2:]).to(device)

# Get features of content and style images
content_features = get_features(content, vgg)
style_features = get_features(style, vgg)

# Calculate style Gram matrices
style_grams = {layer: gram_matrix(style_features[layer]) for layer in style_features}

# Create a target image and prepare it for optimization
target = content.clone().requires_grad_(True).to(device)

# Define style and content weights
style_weights = {'conv1_1': 1.0, 'conv2_1': 0.75, 'conv3_1': 0.2, 'conv4_1': 0.2, 'conv5_1': 0.2}
content_weight = 1e4
style_weight = 1e2

# Define optimizer
optimizer = optim.Adam([target], lr=0.003)

# Style Transfer Training Loop
steps = 2000

for step in range(1, steps+1):
    target_features = get_features(target, vgg)
    content_loss = torch.mean((target_features['conv4_2'] - content_features['conv4_2'])**2)

    style_loss = 0
    for layer in style_weights:
        target_feature = target_features[layer]
        target_gram = gram_matrix(target_feature)
        style_gram = style_grams[layer]
        layer_style_loss = style_weights[layer] * torch.mean((target_gram - style_gram)**2)
        _, d, h, w = target_feature.shape
        style_loss += layer_style_loss / (d * h * w)

    total_loss = content_weight * content_loss + style_weight * style_loss

    optimizer.zero_grad()
    total_loss.backward()
    optimizer.step()

    if step % 100 == 0:
        print(f'Step {step}, Total loss: {total_loss.item()}')

# Display the final image
final_img = im_convert(target)
plt.imshow(final_img)
plt.axis('off')
plt.show()




