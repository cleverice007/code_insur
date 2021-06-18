from flask import Flask, redirect, url_for
from flask import jsonify, request, render_template
import pandas as pd
from collections import defaultdict
import json

app = Flask(__name__) 
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

cor = pd.read_csv('cor.csv', encoding='big5')
num2ch = defaultdict(dict)
options = defaultdict(list)

with open('insur.json', 'r', encoding='utf-8-sig') as f:
    ch2num = json.load(f)

for insur_t, pairs in ch2num.items():
    for name, nums in pairs.items():
        for num in nums:
            num2ch[insur_t][num] = name
        options[insur_t].append(name)
        ch2num[insur_t][name] = set(ch2num[insur_t][name])

types = ['車體險', '責任險', '竊盜險', '傷害險', '金融機構從業人員汽車綜合保險',
         '機車車損綜合保險', '機車第三人責任綜合保險', '其他']

data = pd.read_csv('processed_data2.csv', encoding='big5')
data = data.filter(regex=("buy.*"))
cor = data.corr(method ='pearson')

def get_mapping(insur_t, inquiry, types):
    if types == 'num2ch':
        return num2ch[insur_t][inquiry]
    elif types == 'ch2num':
        return ch2num[insur_t]
    return inquiry

@app.route("/") 
def index():
    return render_template('index.html', types=types, options=options)

@app.route("/results")
def results():
    data = request.args['data']
    data = json.loads(data)
    return render_template('results.html', types=types, data=data)

@app.route("/recommendations", methods=['POST'])
def get_recommendation():
    data = request.get_json()
    rtn = dict()
    for insur_t in data:
        rtn[insur_t] = dict()
        recommend = get_max_cor(insur_t, data[insur_t])
        if not data[insur_t]:
            rtn[insur_t]['choosed'] = [""]
        else:
            rtn[insur_t]['choosed'] = data[insur_t]
        rtn[insur_t]['recommendation'] = recommend

    return jsonify({'redirect': url_for('results', data=json.dumps(rtn))})
    # return redirect(url_for('results', data=json.dumps(rtn)))

def get_max_cor(insur_t, choosed):
    choosed_num = set()
    for insur in choosed:
        for num in ch2num[insur_t][insur]:
            choosed_num.add(num)

    drop_list = []
    for c in choosed_num:
        if f"buy_{c}" in cor.columns:
            drop_list.append(f"buy_{c}")

    deleted_cor = cor.drop(drop_list)

    _max = float('-inf')
    _max_col = None
    for c in drop_list:
        possible = deleted_cor[c]
        p_col = possible.idxmax()
        p = possible.max()
        if p > _max:
            _max = p
            _max_col = p_col
    
    if not _max_col or _max < 0:
        return "No Recommendation"
    else:
        target_num = int(_max_col[4:])
        if target_num in num2ch[insur_t]:
            return num2ch[insur_t][target_num]
        else:
            for nums_pair in num2ch.values():
                if target_num in nums_pair:
                    return nums_pair[target_num]
        return "No Recommendation"

app.run(debug = True)