import re
import pandas as pd
import sqlite3

from flask import Flask, jsonify, request, render_template, redirect, url_for
from data_cleansing import processing_text

from flasgger import Swagger
from flasgger import swag_from

from data_reading_and_writing import create_table, insert_to_table, read_table

# create flask object
app = Flask(__name__, template_folder='templates')

swagger_config = {
    "headers": [],
    "specs": [{"endpoint":"docs", "route": '/docs.json'}],
    "static_url_path": "/flasgger_static",
    "swagger_ui":True,
    "specs_route":"/docs/"
}

swagger = Swagger(app,
                  config = swagger_config
                 )

TABLE_NAME = "tweet_cleaning"

# ******************************************
# langkah awal set library pandas, regex, sqlite, flask, import page python reading and writing table, dan data cleansing

@app.route('/', methods=['GET', "POST"])
def homepage():
    if request.method == 'POST':
        go_to_page = request.form['inputText']
        if go_to_page == "1":
            return redirect(url_for("input_text"))
        elif go_to_page == "2":
            return redirect(url_for("input_file"))
        elif go_to_page == "3":
            return redirect(url_for("read_database"))
    else:
        return render_template("homepage.html")

# ******************************************
# langkah selanjutnya buat function homepage dengan render html, sebagai UI agar user bisa menggunakan API (input text, input file, dan read index)

@app.route('/text-processing',methods=['GET', 'POST'])
def input_text():
    if request.method == 'POST':
        previous_text=request.form['inputText']
        cleaned_text=processing_text(previous_text)
        create_table()
        insert_to_table(value_1=previous_text, 
                        value_2=cleaned_text) 
        json_response={'response':"SUCCESS",
                       'previous_text': previous_text,
                       'cleaned_text': cleaned_text
                      }
        json_response=jsonify(json_response)
        return json_response
    else:
        return render_template("input_text.html")

# ******************************************
# langkah selanjutnya buat function input text processing, dimana user bisa input text yang selanjutnya akan di cleansing dan di record di table database (original dan cleaned text nya)

@app.route('/file-processing',methods=['GET', 'POST'])
def input_file():
    if request.method == 'POST':
        input_file = request.files['inputFile']
        df = pd.read_csv(input_file, encoding='latin1')
        if("Tweet" in df.columns):
            list_of_tweets = df['Tweet'] #yang dari CSV
            list_of_cleaned_tweet = df['Tweet'].apply(lambda x: processing_text(x)) #ini yang hasil cleaning-an

            create_table()
            for previous_text, cleaned_text in zip(list_of_tweets, list_of_cleaned_tweet): # disini di-looping barengan
                insert_to_table(value_1=previous_text, value_2=cleaned_text)
            
            json_response={'response':"SUCCESS",
                           'list_of_tweets': list_of_tweets[0],
                           'list_of_cleaned_tweet': list_of_cleaned_tweet[0]
                          }
            json_response=jsonify(json_response)
            return json_response
        else:
            json_response={'ERROR_WARNING': "NO COLUMNS 'Tweet' APPEAR ON THE UPLOADED FILE"}
            json_response = jsonify(json_response)
            return json_response
        return json_response
    else:
        return render_template("test_file_input.html")

# ******************************************
# langkah selanjutnya buat function input file processing, dimana user bisa upload file csv yang ada column Tweet, untuk di cleansing dan hasil dari process tersebut di record di database

@app.route('/read-database',methods=['GET', 'POST'])
def read_database():
    if request.method == "POST":
        showed_index=request.form['inputIndex']
        showed_keywords = request.form['inputKeywords']
        if len(showed_index)>0:
            print("AAAAAAAAAA")
            result_from_reading_database = read_table(target_index=showed_index)
            previous_text=result_from_reading_database[0].decode('latin1')
            cleaned_text=result_from_reading_database[1].decode('latin1')
            json_response={'Index': showed_index,
                           'Previous_text': previous_text,
                           'Cleaned_text': cleaned_text
                          }
            json_response = jsonify(json_response)
            return json_response
        elif len(showed_keywords)>0:
            print("BBBBBBBBB")
            results = read_table(target_keywords=showed_keywords)
            json_response={'showed_keywords': showed_keywords,
                           'previous_text': results[0][0].decode('latin1'),
                           'cleaned_text': results[0][1].decode('latin1')
                          }
            json_response = jsonify(json_response)
            return json_response
        else:
            print("CCCCCCCC")
            json_response={'ERROR_WARNING': "INDEX OR KEYWORDS IS NONE"}
            json_response = jsonify(json_response)
            return json_response
    else:
        return render_template("read_database.html")

# ******************************************
# langkah selanjutnya buat function read index dan word mentioned, dimana user bisa cek entry untuk data tweet atau text yang terakhir di input dalam database 

# @app.route('/',methods=['GET', "POST"])
# def hello_world():
#     text = request.form.get('inputText')
#     json_response={
#         'original_text': text,
#         'cleaned_text': processing_text(text)
#     }
#     response_data = jsonify(json_response)
#     return render_template("index_2.html")

# @app.route("/<tweet>", methods=['GET'])
# def cleansing(tweet):
#     cleaned_tweet = processing_text(tweet)
#     response_data = jsonify({"previous_tweet":tweet, "cleaned_tweet":cleaned_tweet})
#     return response_data

# @app.route('/input-processing-2',methods=['GET'])
# def input_processing_2():
#     # text = request.form.get('text')
#     # cleaned_tweet = processing_text(text)
#     # results = read_table(table_name=TABLE_NAME)
#     # last_index = len(results)
#     # insert_to_table(value_1=last_index, 
#     #                 value_2=cleaned_tweet, 
#     #                 table_name=TABLE_NAME) 
#     response_data = jsonify({"response":"INPUT_PROCESSING_2"})
#     return response_data



# @swag_from("docs/input_processing.yml", methods=['POST'])
# @app.route('/input-processing',methods=['POST'])
# def input_processing():
#     text = request.form.get('text')
#     cleaned_tweet = processing_text(text)
#     results = read_table(table_name=TABLE_NAME)
#     last_index = len(results)
#     insert_to_table(value_1=last_index, 
#                     value_2=cleaned_tweet, 
#                     table_name=TABLE_NAME)
    
#     response_data = jsonify({"response":"SUCCESS"})
#     return response_data


# @swag_from("docs/file_processing.yml", methods=['POST'])
# @app.route('/file-processing',methods=['POST'])
# def file_processing():
#     """
#         Memproses file yang akan di upload di swagger_ui atau di HTML.
#     """
#     # 1 method untuk upload file
#     # df = pd.read_csv('data/data.csv', encoding='latin1') # baca datanya
#     create_table() # create tablenya
#     df = request.form.get('upload_file')
#     print(df)
#     df = pd.read_csv(df)
#     # iterasi untuk setiap tweet yang ada di kolom tweet yang ada di dataframe 'DF'
#     for idx, tweet in enumerate(df['Tweet']):
#         cleaned_tweet = processing_text(tweet) # process tweetnya
#         insert_to_table(value_1=idx,
#                         value_2=cleaned_tweet, 
#                         table_name=TABLE_NAME) # insert to table tweet yang sudah di cleaned.
    
#     response_data = jsonify({"response":"SUCCESS"}) # karena kita ga butuh response apa2 dari proses ini, selama tidak ada error, return "SUCCESS"
#     return response_data

# @swag_from("docs/read_index_data.yml", methods=['POST'])
# @app.route('/read-index-data',methods=['POST'])
# def read_index_data():
#     index = request.form.get('index')
#     result = read_table(target_index=int(index),
#                          table_name=TABLE_NAME)
#     response_data = jsonify({"tweets":result})
#     return response_data


if __name__ == '__main__':
    app.run(debug=True)
