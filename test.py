import pandas as pd
from datetime import datetime, timedelta
from googletrans import Translator
import arabic_reshaper
from bidi.algorithm import get_display

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer()
translator = Translator()

booknumber = int(input("Please enter the book number: "))
lessonnumber = int(input("Please enter the lesson number: "))
levellist= [0,1,2,3,5,10,15,30]

df = pd.read_excel("test.xlsx")

book_list = []
lesson_list = []
final_list = []

def convert(text):
    reshaped_text = arabic_reshaper.reshape(text)
    converted = get_display(reshaped_text)
    return converted

for i in range (0,len(df["book"])) :
    if df["time"].isnull().iloc[i]:
        df.loc[i, "level"] = 0
        df.loc[i, "time"] = datetime.now().date()

df.to_excel("test.xlsx", index=False)
df = pd.read_excel("test.xlsx")

for i in range (0,len(df["book"])) :
    if df["book"].iloc[i] == booknumber :
        book_list.append(i)

for i in book_list :
    if df["lesson"].iloc[i] == lessonnumber :
        lesson_list.append(i)

for i in lesson_list :
    if df.loc[i, "time"].to_pydatetime().date() <= datetime.now().date() :
        final_list.append(i)

for i in final_list :
    print("")
    print("***************************************************")
    print("***************************************************")
    translated_text = translator.translate(df["en"].iloc[i], src='en', dest='fa')
    print(convert(translated_text.text))
    print("Translate the above sentence into English:")

    sentence = input()
    
    vectors = vectorizer.fit_transform([df["en"].iloc[i], sentence])
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]

    print("Correct answer: ", df["en"].iloc[i])

    if round(similarity, 2) == 1 :
        if (df["level"].loc[i] <= 6):
            df.loc[i, "level"] = df["level"].loc[i] + 1
        else:
            df.loc[i, "level"] = df["level"].loc[i]
        df.loc[i, "time"] = df.loc[i, "time"].to_pydatetime().date()+ timedelta(days=levellist[int(df["level"].loc[i])])
        df.to_excel("test.xlsx", index=False)
        print("That's true!")
    else:
        df.loc[i, "level"]  = 0
        df.loc[i, "time"]= datetime.now().date()
        df.to_excel("test.xlsx", index=False)
        print("That's wrong!")

    print("The amount of difference: ", round(similarity, 2))

    if df["sta"].notnull().iloc[i] :
        print("Structure: ", df["sta"].iloc[i])