from flask import Flask, request, Response
from nltk.tokenize import sent_tokenize
import json
from translate import translate_onesentence
from store import storeonesent2mysql, update_table_viamysql, update_mysql_viafile
from src.logger import create_logger
import datetime
logger = create_logger('access.log')

app = Flask(__name__)

# bilingual dictionary
# provided to update and translate function
TAGTABLE = {}
number = update_table_viamysql(TAGTABLE, 'pe', 'zh')
logger.info(f'loading {number} pairs from table')


@app.route('/api/split', methods=['POST'])
def split_sentence():
    if request.method == 'POST':
        now = datetime.datetime.now()
        year, month, day = now.year, now.month, now.day
        left_month = 13-((year-2020)*12 + (month-3))
        if left_month < 0:
            result = {}
            result['errorCode'] = 1
            result['error'] = '试用已经过期，请联系管理员。'
            return Response(json.dumps(result), mimetype='application/javascript')
        else:
            logger.info('剩余试用时间:%d个月!', left_month )
        data = json.loads(request.get_data(as_text=True))
        sourceLang = data['sourceLang']
        targetLang = data['targetLang']
        text = data['text'].strip()
        result = {}
        sents = sent_tokenize(text)
        new_sents = []
        for sent in sents:
            new_sents.extend([subsent.strip() for subsent in sent.split('\n') if len(subsent.strip())>0])
        result['sentences'] = new_sents
        result['errorCode'] = 0
        return Response(json.dumps(result), mimetype='application/javascript')

@app.route('/api/itranslate', methods=['POST'])
def itranslate():
    if request.method == 'POST':
        data = json.loads(request.get_data(as_text=True))
        sourceLang = data['sourceLang']
        targetLang = data['targetLang']
        text = data['text']
        prefix = data['prefix']
        withtable = data['withtable']
        result = {}
        
        try:
            if withtable == 'True':
                res = translate_onesentence(text, prefix=prefix, table=TAGTABLE)
            else:
                res = translate_onesentence(text, prefix=prefix, table=None)
        except Exception as e:
            res = ""
            result['errorCode'] = 1 
            result['error'] = str(e)
        else:
            result['errorCode'] = 0
            result['translation'] = res
        return Response(json.dumps(result), mimetype='application/javascript')

@app.route('/api/store_onesentence', methods=['POST'])
def store_onesentence():
    if request.method == 'POST':
        data = json.loads(request.get_data(as_text=True))
        sourceLang = data['sourceLang']
        targetLang = data['targetLang']
        sourceText = data['sourceText']
        targetText = data['targetText']
        result = {}
        if len(sourceText)>0 and len(targetText)>0:
            try:
                storeonesent2mysql(sourceText, targetText, sourceLang, targetLang)
            except Exception as e:
                result['errorCode'] = 1
                result['error'] = str(e)
            else:
                result['errorCode'] = 0
        else:
            result['errorCode'] = 1
            result['error'] = 'empty content error!'
        return Response(json.dumps(result), mimetype='application/javascript')

@app.route('/api/update_table', methods=['POST'])
def update_table():
    if request.method == 'POST':
        data = json.loads(request.get_data(as_text=True))
        sourceLang = data['sourceLang']
        targetLang = data['targetLang']
        result = {}
        if 'table' in data:
            # add table to mysql and update
            ret = update_mysql_viafile(data['table'], sourceLang, targetLang)
            if ret is not None:
                result['errorCode'] = 1
                result['error'] = str(ret)
                return Response(json.dumps(result), mimetype='application/javascript')
        try:
            number = update_table_viamysql(TAGTABLE, sourceLang, targetLang)
        except Exception as e:
            result['errorCode'] = 1
            result['error'] = str(e)
        else:
            result['errorCode'] = 0
            result['info'] = f'现在使用{number}对双语词语。'
        return Response(json.dumps(result), mimetype='application/javascript')


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=6431, threaded=True)
