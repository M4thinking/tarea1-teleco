import json 
import torch
import numpy
import torch.nn as nn

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

TRESH = 0.90

#definimos si trabajar o no en la CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#importamos el modelo ya entrenado guardado en data.pth
FILE = "data.pth" 
data = torch.load(FILE)

# Cargamos los datos necesarios para inicializar el modelo
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

#cargamos el modelo ya entrenado
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval() #Dejamos el modelo en modo evaluación

#creamos una funcion que a partir de una frase, evalúa la respuesta del modelo
def interp(frase):
	tokenizado = tokenize(frase) # Tokenizamos la frase
	X = bag_of_words(tokenizado, all_words) # Vemos que palabras del vocabulario tiene la frase
	X = X.reshape(1, X.shape[0]) # Ajustamos el tamaño de x
	X = torch.from_numpy(X).to(device) # Creamos un tensor con la frase ya procesada 
	soft = nn.Softmax(dim = 1) # Inicializamos un sof
	output = model(X) # Evaluamos el modelo en X
	prob = soft(output) # Pasamos el output del modelo por una softmax
	a, predicted = torch.max(prob, dim=1) # Obtenemos el dato predicho junto con su probabilidad 
	probabilidad = a.detach().numpy()[0] # Guardamos la probabilidad 
	tag = tags[predicted.item()]

	#Evaluamos si la probabilidad de la categoría predicha supera el humbral
	if probabilidad >= TRESH:
		return tag
	else:
		return "0"