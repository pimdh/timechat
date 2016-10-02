# Problems
- Create ChatBot + train with corpus
- Identifying relevant question
- Extracting location
- Fetching result

Ideas for question detection:
- Naive bayes classifier (/other ML approaches)
- POS tagging

Ideas for location extraction:
-

Sentence sim
Synets/Wordnet 
https://www.quora.com/What-is-the-best-way-to-find-the-most-similar-sentence

# ChatBot
ChatterBot + NPS corpus

Packages:
ChatBot, NLTK, NPS corpus, python-Levenshtein

Todo:
- Train with Reddit dataset
- Pick and implement logic matcher
- Build time matcher
- Build fetcher
- Put online




# Location extraction

- Subseq with lowest average idf score after proposition
- Named Entity Recognition
- Syntax parsing


# Env vars:
GOOGLE_APPLICATION_CREDENTIALS : path to google cloud key
GOOGLE_MAPS_API_KEY
