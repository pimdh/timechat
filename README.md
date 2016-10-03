# TimeChat
TimeChat is a chatbot that is able to answer questions in natural language about the current time in a particular place in responses in natural language. It is built on top of ChatterBot and consists of three parts: location extraction and language determination; geocoding; response generation.

## Location extraction and language determination
Three methods are implemented: one built on basic NLP methods and two using the Google Natural Language API.

### Inverse Document Frequency
In this method, the language is first determined by choosing the language with the highest sum of the Inverse Document Frequency of each word to the power `y`. `y` is set to 1/3 to let rarer words contribute to the score appropriately.

Then the method assumes the location is in the longest sequence of 'rare' words directly after a preposition. The rareness of such a sequence is given by the sum of the inverse document frequency its words divided by `N^x`, where `N `is the length of the sequence and `x` some penalisation parameter. After some experimentation, `x` is set to 1/2 as to make the found sequences not too long, nor too short.

A corpus of part-of-speech-tagged and non-tagged text is provided for each language, to learn the document frequencies and determine which words are prepositions.

This method works for English and Dutch and can be easily extended to support more languages.

### Syntax
In this method, the Google API is used construct a full dependency tree of the syntax. The Google API operates through a neural model of syntax called SyntaxNet [(Andor et al., 2016)](http://arxiv.org/abs/1603.06042) and is trained on the [Universal Dependencies](http://universaldependencies.org/) dataset.

Because it can be assumed that a relevant question will only contain one prepositional phrase which must contain the location, this method selects the longest prepositional phrase in the sentence to include the location. If no prepositional phrase is found, the method fails.

This method works for English only.

### Named Entity Recognition
In this method, the Google API is used to detect named entities in the input sentence. Of these, the entity concerning location with the highest salience (importance) is extracted. If no location entity is found, the method fails.

Google does not publish details on the workings of their Named Entity Recognition algorithm.

This method works for English only.

### Comparison
The three methods find the location correctly in the following cases:

Question | IDF | Syntax | Entity
--- | --- | --- | ---
What is the local time in Amsterdam right now? | ✓ | ✓ | ✓
Okay, what's the time in califonia then? | ✓ | ✓ | ✗
Okay, what's the time in Califonia then? | ✓ | ✓ | ✓
Local time in 77379 | ✓ | ✓ | ✗
What is the time at 2313PN | ✓ | ✓ | ✗
What is the time on the Isle of Man? | ✗ | ✓ | ✓
In Paris is the time? | ✓ | ✓ | ✓
Hoe laat is het op Bonaire? | ✓ | ✗ | ✗

Some remarks:
- The IDF method does not work with locations that are comprised of common words.
- The Syntax method is very accurate.
- The Entity method is highly case sensitive and does not work well with postcodes.

The IDF method is cheap to compute and easily extensible to multiple languages, while the Syntax method is most accurate, but much more costly, as this involves a (paid) call to the Google NL API or a feedforward through a complicated neural net. The choice for either of the two will depend on the application. Interestingly, the Entity method, that has location extraction as an explicit feature, performs poorest. A further explanation is impossible to provide, as Google does not publish details on the algorithm.

## Geocoding
Once a location has been extracted, it is fed to the Google Maps Geocoding API to determine a full description of the location, as well as its coordinates. From the coordinates, the timezone is obtained from the Google Maps Timezone API.

## Response generation
Given the language, the location, the preposition (e.g. in or on) that is used in the question and the local time, a natural language response is simply generated from random pick from a set of templates, in which the variables are filled in.

Examples are:
```
Op Caribisch Nederland is de lokale tijd 21:46.
In Spring, TX 77379, USA it is now: 20:47.
03:48 is de lokale tijd in 2313 PN Leiden, Nederland.
```


## Installation
Requires Python 2 and Pip. Python packages:
```
pip2 install --upgrade flask chatterbot nltk google-api-python-client pytz python-Levenshtein
```
Make sure that the Google Natural Language and Maps Apis are enabled. Obtain Google Cloud Application credentials and set environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path leading to these credentials and set `GOOGLE_MAPS_API_KEY` to be a valid Google Maps Api Key.

Install NLTK corpora:
```
python2 -m nltk.downloader book alpino
```

## Usage
```
export FLASK_APP=chatbot.py
export FLASK_DEBUG=1
flask run
```
