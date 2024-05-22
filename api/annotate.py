
import os
import re
import random
import base64
import requests
import joblib
import numpy as np

from dotenv import load_dotenv
from collections import Counter
from io import BytesIO
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import Model
from keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.applications import VGG16
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model


load_dotenv()


# generate a description for an image
def generate_desc(model, tokenizer, photo, max_length):
	# seed the generation process
	in_text = 'startseq'
	# iterate over the whole length of the sequence
	for i in range(max_length):
		# integer encode input sequence
		sequence = tokenizer.texts_to_sequences([in_text])[0]
		# pad input
		sequence = pad_sequences([sequence], maxlen=max_length)
		# predict next word
		yhat = model.predict([photo,sequence], verbose=0)
		# convert probability to integer
		yhat = np.argmax(yhat)
		# map integer to word
		word = word_for_id(yhat, tokenizer)
		# stop if we cannot map the word
		if word is None:
			break
		# append as input for generating the next word
		in_text += ' ' + word
		# stop if we predict the end of the sequence
		if word == 'endseq':
			break
	return in_text


def create_tokenizer(descriptions):
	lines = to_lines(descriptions)
	tokenizer = Tokenizer()
	tokenizer.fit_on_texts(lines)
	return tokenizer


# convert a dictionary of clean descriptions to a list of descriptions
def to_lines(descriptions):
	all_desc = list()
	for key in descriptions.keys():
		[all_desc.append(d) for d in descriptions[key]]
	return all_desc


# map an integer to a word
def word_for_id(integer, tokenizer):
	for word, index in tokenizer.word_index.items():
		if index == integer:
			return word
	return None


# load clean descriptions into memory
def load_clean_descriptions(filename, dataset):
	# load document
	doc = load_doc(filename)
	descriptions = dict()
	for line in doc.split('\n'):
		# split line by white space
		tokens = line.split()
		# split id from description
		image_id, image_desc = tokens[0], tokens[1:]
		# skip images not in the set
		if image_id in dataset:
			# create list
			if image_id not in descriptions:
				descriptions[image_id] = list()
			# wrap description in tokens
			desc = 'startseq ' + ' '.join(image_desc) + ' endseq'
			# store
			descriptions[image_id].append(desc)
	return descriptions


# load doc into memory
def load_doc(filename):
	# open the file as read only
	file = open(filename, 'r')
	# read all text
	text = file.read()
	# close the file
	file.close()
	return text


# load a pre-defined list of photo identifiers
def load_set(filename):
	doc = load_doc(filename)
	dataset = list()
	# process line by line
	for line in doc.split('\n'):
		# skip empty lines
		if len(line) < 1:
			continue
		# get the image identifier
		identifier = line.split('.')[0]
		dataset.append(identifier)
	return set(dataset)


# calculate the length of the description with the most words
def get_max_length(descriptions):
	lines = to_lines(descriptions)
	return max(len(d.split()) for d in lines)


def get_trad(caption):
	url = 'https://api-free.deepl.com/v2/translate'
	key = os.getenv('TRAD_KEY')
	headers = {
		'Authorization': f'DeepL-Auth-Key {key}',
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	data = { 
		'text': [caption],
		'source_lang': 'EN',
		'target_lang': 'FR'
	}
	response = requests.post(url, json=data, headers=headers)
	# print(response)
	if response.status_code == 200:
		result = response.json()
		print(result)
		trad = result['translations'][0]['text']
		return trad
	else:
		return 'Pas de traduction'


def get_sentiment(caption):
	emojies = { 
		'joy': { 'smiley': '😂', 'trad': 'joie' }, 
		'fear': { 'smiley': '😱', 'trad': 'peur' }, 
		'anger': { 'smiley': '😠', 'trad': 'colère' }, 
		'sadness': { 'smiley': '😢', 'trad': 'tristesse' }, 
		'disgust': { 'smiley': '🤢', 'trad': 'dégoût' }, 
		'shame': { 'smiley': '😅', 'trad': 'honte' }, 
		'guilt': { 'smiley': '😔', 'trad': 'culpabilité' }
	}
	lsvc, vectorizer = joblib.load('../models/model_sentiments.pkl')
	features = create_feature(caption, nrange=(1, 4))
	features = vectorizer.transform(features)
	prediction = lsvc.predict(features)[0]
	return { 'smiley': emojies[prediction]['smiley'], 'trad': emojies[prediction]['trad'].capitalize() }


def ngram(token, n): 
    output = []
    for i in range(n-1, len(token)): 
        ngram = ' '.join(token[i-n+1:i+1])
        output.append(ngram) 
    return output


def create_feature(text, nrange=(1, 1)):
    text_features = [] 
    text = text.lower() 
    text_alphanum = re.sub('[^a-z0-9#]', ' ', text)
    for n in range(nrange[0], nrange[1]+1): 
        text_features += ngram(text_alphanum.split(), n)
    text_punc = re.sub('[a-z0-9]', ' ', text)
    text_features += ngram(text_punc.split(), 1)
    return Counter(text_features)


def get_caption(to_annotate):
	if 'jpeg' in to_annotate:
		to_annotate = to_annotate.replace('data:image/jpeg;base64,', '')
	elif 'png' in to_annotate:
		to_annotate = to_annotate.replace('data:image/png;base64,', '')
	# load training dataset (6K)
	filename = '../data/Flickr8k_text/Flickr_8k.trainImages.txt'
	train = load_set(filename)
	train_descriptions = load_clean_descriptions('../data/descriptions.txt', train)
	tokenizer = create_tokenizer(train_descriptions)
	max_length = get_max_length(train_descriptions)
	decoded_img = base64.b64decode(to_annotate)
	img = image.load_img(BytesIO(decoded_img), target_size=(224, 224))
	# preprocess the image
	x = image.img_to_array(img)
	x = np.expand_dims(x, axis=0)
	x = preprocess_input(x)

	#load the feature extraction model
	feature_extractor = ResNet50()
	feature_extractor = Model(inputs=feature_extractor.inputs, outputs=feature_extractor.layers[-2].output)
	features = feature_extractor.predict(x)
	features = features.flatten()
	photo = features.reshape((1, -1))
	#load the model
	model_filename = '../data/model-ep004-loss3.456-val_loss3.819.keras'
	model = load_model(model_filename)
	caption = generate_desc(model, tokenizer, photo, max_length)
	caption = caption.replace('startseq', '').replace('endseq', '').strip()

	# load the feature extraction model
	# feature_extractor = VGG16()
	# feature_extractor = Model(inputs=feature_extractor.inputs, outputs=feature_extractor.layers[-2].output)
	# features = feature_extractor.predict(x)
	# features = features.flatten()
	# photo = features.reshape((1, -1))
	# # load the model
	# model_filename = '../data/alexis_final_model.keras'
	# model = load_model(model_filename)
	# caption = generate_desc(model, tokenizer, photo, max_length)
	# caption = caption.replace('startseq', '').replace('endseq', '').strip()

	return caption, get_trad(caption), get_sentiment(caption)

