from cmath import isnan
import csv
import pandas as pd
import numpy as np
import re
import argparse
from seqeval.metrics import classification_report
from seqeval.scheme import IOB2

def label(name):
    original_df = pd.read_csv("./suffle_test.csv") 
    original_df.drop(columns=['timestamp'], inplace=True)
    original_df.drop(columns=['algo 名稱'], inplace=True)
    original_df.drop(columns=['msno (用戶編號)'], inplace=True)
    original_df.drop(columns=['input text'], inplace=True)
    original_df.drop(columns=['confidence threshold'], inplace=True)
    original_df.drop(columns=['encoded device id'], inplace=True)
    original_df.drop(columns=['log date\r\n'], inplace=True)

    predict_df = pd.read_csv(f"./{name}/task2.csv") 
    predict_df.drop(columns=['處理的字串'], inplace=True)
    predict_df.drop(columns=['label'], inplace=True)
    
    for i in range(len(predict_df['predict'])):
        if pd.isna(predict_df['predict'][i]):
            predict_df['predict'][i] = ""

    original_df = original_df.to_numpy()
    predict_df = predict_df.to_numpy()
    original_column = [x for x in original_df.tolist()]
    predict_df = [x for x in predict_df.tolist()]

    for i in range(len(original_df)):
        temp = []
        for substr in re.finditer('start', original_column[i][1]):
            next_dot = original_column[i][1].find(',',substr.end()+2)
            temp.append(original_column[i][1][substr.end()+2:next_dot])
            
            end_ = original_column[i][1].find('end',next_dot)
            next_dot = original_column[i][1].find(',',end_+5)
            temp.append(original_column[i][1][end_+5:next_dot])
        try:
            temp_str_list = '(' + temp[0] + " " + temp[1] + ')'
            for j in range(2, len(temp), 2):
                temp_str = '(' + temp[j] + " " + temp[j+1] + ')'
                if temp_str not in temp_str_list:
                    temp_str_list = temp_str_list + " " + temp_str
            original_column[i][1] = temp_str_list
        except:
            original_column[i][1] = "" 
        try:
            original_column[i].append(predict_df[i][0])
        except:
            original_column[i].append("")
    
    data = ['\ufeff處理的字串', 'label', 'predict\n']

    with open('performance2.csv', 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(data)
        for i in range(len(original_column)):
            writer.writerow(original_column[i])

def read_data():
    df = pd.read_csv("./performance2.csv")

    for i in range(len(df['label'])):
        if pd.isna(df['處理的字串'][i]):
            df['處理的字串'][i] = ""
        if pd.isna(df['label'][i]):
            df['label'][i] = ""
        if pd.isna(df['predict\n'][i]):
            df['predict\n'][i] = ""
    df = df.to_numpy()

    true, pred = [], []
    for i in range(len(df)):
        temp, temp2 =[], []
        for j in range(len(df[i][0])):
            temp.append('O')
            temp2.append('O')
        df[i][1] = re.sub("\(|\)","",df[i][1])
        df[i][2] = re.sub("\(|\)","",df[i][2])

        try:
            true_pair = list(map(int, df[i][1].split(" ")))
        except: 
            true_pair = False
        try:
            predict_pair = list(map(int, df[i][2].split(" ")))
        except: 
            predict_pair = False
        
        if true_pair:
            for j in range(0,len(true_pair),2):
                for k in range(true_pair[j],true_pair[j+1]):
                    if k == true_pair[j]:
                        temp[k] = 'B'
                    else :
                        temp[k] = 'I'
        if predict_pair:
            for j in range(0,len(predict_pair),2):
                try:
                    for k in range(predict_pair[j], predict_pair[j+1]):
                        if k == predict_pair[j]:
                            temp2[k] = 'B'
                        else : 
                            temp2[k] = 'I'
                except:
                    break
        true.append(temp)
        pred.append(temp2)
    return true, pred    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_name', '-n', type=str, default='lin')
    args = parser.parse_args()

    label(args.file_name)
    true, pred = read_data()
    print(classification_report(true, pred, scheme=IOB2))