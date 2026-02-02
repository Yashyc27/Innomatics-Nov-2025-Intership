import re
import nltk
from sklearn.base import BaseEstimator, TransformerMixin
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Pre-download required NLTK data
nltk.download(['stopwords', 'wordnet', 'omw-1.4'], quiet=True)

class TextCleaner(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [self._clean(str(text)) for text in X]

    def _clean(self, text):
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        words = [self.lemmatizer.lemmatize(w) for w in text.split() if w not in self.stop_words]
        return " ".join(words)