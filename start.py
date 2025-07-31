from flask import Flask, request, jsonify
from flask_cors import CORS
import vosk_server

app = Flask( __name__ )
CORS( app )
# Инициализация класса сервера
server = vosk_server.VoskServer( "vosk-model-small-ru-0.22" )
# Добавляем обработку запроса на stt
@app.route( '/stt' , methods = [ 'POST' ] )
def stt() :
    # Если ключ audio пуст
    if 'audio' not in request.files:
        return jsonify( { "error" : "No audio file" } ) , 400
    # Получаем текст из wav файла
    file       = request.files[ 'audio' ]
    speechtext = server.GetTextFromFile( file )
    # Возврат результата
    return jsonify({
        "speech" : speechtext ,
        "filename" : file.filename
    })

# Стартуем сервер
app.run( host = '127.0.0.1' , port = 5666 , debug = True )