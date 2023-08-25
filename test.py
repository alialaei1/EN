import pandas as pd
from datetime import datetime, timedelta
from googletrans import Translator
import arabic_reshaper
from bidi.algorithm import get_display

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import pyttsx3
import speech_recognition as sr


# Initialize the text-to-speech engine
engine = pyttsx3.init()
voice = engine.getProperty('voices')
engine.setProperty('voice', voice[1].id)
engine.setProperty('rate', 150)



vectorizer = TfidfVectorizer()
translator = Translator()
r = sr.Recognizer()



activatevoice = int(input("Activate voice: "))
booknumber = int(input("Please enter the book number: "))
lessonnumber = int(input("Please enter the lesson number: "))

levellist= [0,1,2,3,5,10,15,30]

df = pd.read_excel("EN1.xlsx")

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

df.to_excel("EN1.xlsx", index=False)
df = pd.read_excel("EN1.xlsx")

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
    if activatevoice == 1:
        
        engine.say("ready!")
        engine.runAndWait()

        try:
            with sr.Microphone() as source2:
                r.dynamic_energy_threshold = False
                r.adjust_for_ambient_noise(source2, duration=0.2)
                try:
                    audio2 = r.listen(source2,timeout=10,phrase_time_limit=15)
                    MyText = r.recognize_google(audio2)
                    MyText = MyText.lower()
                except:
                    MyText = ""
                sentence = MyText
                print("sey: ",sentence)
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            sentence = ""
         
        except sr.UnknownValueError:
            print("unknown error occurred")
            sentence = ""
    else:

        sentence = input()
    
    vectors = vectorizer.fit_transform([df["en"].iloc[i], sentence])
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]

    print("Correct answer: ", df["en"].iloc[i])
        # Convert the Farsi text to speech


    if round(similarity, 2) == 1 :
        if (df["level"].loc[i] <= 6):
            df.loc[i, "level"] = df["level"].loc[i] + 1
        else:
            df.loc[i, "level"] = df["level"].loc[i]
        df.loc[i, "time"] = df.loc[i, "time"].to_pydatetime().date()+ timedelta(days=levellist[int(df["level"].loc[i])])
        df.to_excel("EN1.xlsx", index=False)
        print("That's true!")
        engine.say("That's true!")
        engine.runAndWait()
    else:
        df.loc[i, "level"]  = 0
        df.loc[i, "time"]= datetime.now().date()
        df.to_excel("EN1.xlsx", index=False)
        print("That's wrong!")
        engine.say("That's wrong!")
        engine.runAndWait()

    engine.say(df["en"].iloc[i])

    # Wait for the speech to finish
    engine.runAndWait()
    print("The amount of difference: ", round(similarity, 2))

    if df["sta"].notnull().iloc[i] :
        print("Structure: ", df["sta"].iloc[i])
