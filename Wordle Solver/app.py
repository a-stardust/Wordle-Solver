from flask import Flask, request, jsonify ,render_template
from flask_cors import CORS
import sys
import os
import pandas as pd
import difflib
import psutil
import subprocess
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')


#-------------------------------------------------------------------

list1=[]
exit=[]
nonexit=[]
posdict={}

with open('words.txt',"r") as alpha:
    for i in alpha:
        list1.append(i)
alphabets="abcdefghijklmnopqrstuvwxyz"

#-------------------------------------------------------------------

def probability(list1):
    alphalist=[[0,0,0,0,0] for _ in range(26) ]
    for i in list1:
        for j in range(0,5):
            for x,alphabet in zip(alphalist,alphabets):
                if i[j]==alphabet:
                    x[j]=x[j]+1
    dataf1=pd.DataFrame(alphalist, index = list('abcdefghijklmnopqrstuvwxyz'), columns = list('12345'))
    #print(dataf1)
    mostprobable = dataf1.idxmax()
    mostprob=''
    for i in range (0,5):
        mostprob=mostprob+str(mostprobable[i]) 
    #print(mostprob)
    words=difflib.get_close_matches(mostprob, list1,n=3, cutoff = 0.1 )
    print(list1)
    print(words)
    if len(words)==0:
        if len(list1)!=0:
            return list1[0]
        else:
            return list2[0]
    else:
        return words[0]


def constraint(list1,exit,nonexit):
    list2=[]
    listinter1=[]
    listinter2=[]
    for i in list1:
        count1=0
        count2=0
        for j in exit:
            if j in i:
                count1=count1+1
        if count1==len(exit):
            listinter1.append(i)
        
        for k in nonexit:
            if k not in i:
                count2=count2+1
        if  count2==len(nonexit):
            listinter2.append(i)
    return list(set(listinter1) & set(listinter2) )
                                

def position(list2,posdict,chosen):
    list3=[]
    list4=[]
    for i in list2:
        count=0
        for index in range(1,6):
            if posdict[index]!='':
                if posdict[index]==i[index-1]:
                    count=count+1  
                    continue
            if posdict[index]=='':
                count=count+1

        if count==5:
            list3.append(i)
    #print(list3)
            
    for i in list2:
        count1=0
        for ex in exit:
            if ex not in posdict.values():
                if ex!=i[chosen.index(ex)]:    
                    count1=count1+1
            if ex in posdict.values():
                if ex==i[chosen.index(ex)]:    
                    count1=count1+1
        if count1==len(exit):
            list4.append(i)    
    #print(list4)
    return list(set(list3) & set(list4))
###################################################################





###################################################################

@app.route('/restart', methods=['POST'])
def restart_app():
    try:
        list2=[]
        list1=[]
        list3=[]
        # del exit
        # del nonexit
        # del posdict
        subprocess.Popen(['python', 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('app restarted')
        return jsonify({'message': 'Flask app restarted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/predict', methods=['POST'])
def predict():
    global list1
    global list2
    global exit
    global nonexit
    word_data = request.get_json()
    # print(word_data)
    chosen=word_data['wordData']['word']
    # print(chosen)
    yellow_letters = word_data['wordData'].get('yellowLetters', [])
    green_letters = word_data['wordData'].get('greenLetters', [])
    uncolored_set = word_data['wordData'].get('uncoloredLetters', [])
 
    yellow_letters = [letter['letter'] for letter in yellow_letters]
    green_letters = [letter['letter'] for letter in green_letters]
    uncolored_set = [letter['letter'] for letter in uncolored_set]

    yellow_letters=set(yellow_letters)
    green_letters=set(green_letters)
    uncolored_set=set(uncolored_set)

    exit=list(green_letters.union(yellow_letters))

    uncolored_set = set(uncolored_set)
    distinct_letters = set(exit)

    nonexit = list(uncolored_set - distinct_letters)

    greenletters = {}
    greenLetters = word_data['wordData'].get('greenLetters', [])
    for item in greenLetters:
        index = item.get('index') + 1
        letter = item.get('letter')
        greenletters[index] = letter
    for i in range(1, 6):
        if i not in greenletters:
            greenletters[i] = ''

    posdict=greenletters
######################################################################
    list2=constraint(list1,exit,nonexit)
    list3=position(list2,posdict,chosen)
    list1=list3
    print(exit,'\n',nonexit,'\n',posdict,'\n',list2,'\n',list3)
    predicted_word =probability(list3)
    predicted_word=predicted_word[0:5]
    print("Predicted word:", predicted_word)  # Print the predicted word
    return jsonify({"predictedWord": predicted_word})





if __name__ == '__main__':
    app.run(debug=True)
