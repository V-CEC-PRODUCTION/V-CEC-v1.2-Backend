# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import WordNetLemmatizer

# # nltk.download('punkt')
# # nltk.download('stopwords')
# # nltk.download('wordnet')

# def extract_unique_meaningful_words(text):
   
#     words = word_tokenize(text)
#     words = [word.lower() for word in words if word.isalnum()]
#     stop_words = set(stopwords.words('english'))
#     words = [word for word in words if word not in stop_words and not word.isdigit()]
#     lemmatizer = WordNetLemmatizer()
#     words = [lemmatizer.lemmatize(word) for word in words]

#     words = [word for word in words if len(word) > 2]

#     unique_words = set(words)

#     return unique_words


# text = '''As part of National Engineer's Day, APJAKTU NSS CELL Units 184, 338 & 559 of College of Engineering Chengannur is here with an Essay Writing Competition.

#  Topic: The role of engineers in sustainable development

#  Guidelines

# 📍Must be done on A4 size paper.
# 📍It shouldn't exceed over 500 words.
# 📍Submissions must be in pdf format.
# 📍Handwriting should be readable.
# 📍Plagiarism is prohibited.'''

# unique_words = extract_unique_meaningful_words(text)


# unique_words_list = list(unique_words)
# unique_words_str = ", ".join(unique_words_list)
# print(unique_words_str)

from django.utils import timezone
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vcec_bk.settings')

current_time = timezone.now()
print("Current Time (UTC):", current_time)

