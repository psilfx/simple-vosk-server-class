import wave, os, time , requests , json
from vosk import Model, KaldiRecognizer
from datetime import datetime

# Простая реализация класса для сервера Vosk STT
class VoskServer:
    # Используемая модель для анализа файла
    model   = ''
    # Папка для сохранения файлов .wav
    filedir = 'audio'
    # Папка для сохранения файлов текста
    textdir = 'text'
    # Разрешенные типы данных
    allowed = [ '.mp3' , '.ogg' , '.wav' ]
    def __init__( self , model ) :
        self.model = Model( model )
        os.makedirs( self.filedir , exist_ok = True )
        os.makedirs( self.textdir , exist_ok = True )
    def DownloadFile( url , path ) :
        # Делаем запрос по ссылке
        response = requests.get( url , stream = True )
        response.raise_for_status()
        # Получаем тип файла
        contentType = response.headers.get( 'Content-Type' )
        # Если это не аудиофайл
        if 'audio' not in contentType :
            return ""
        # Читаем по частям и пишем файл в бинарном режиме
        with open( path , 'wb' ) as file :
            for chunk in response.iter_content( chunk_size = 8192 ) :
                file.write( chunk )
        return path
    def GetTimestamp( self ) :
        return datetime.now().strftime( "%Y%m%d_%H%M%S" )
    def GetFilename( self ) :
        return f"temp_audio_{ self.GetTimestamp() }"
    def IsAllowed( self , extension ):
        return extension in self.allowed
    # Конвертируем в правильный .wav формат, если требуется
    def ConvertFile( self , file ) :
        filename  = self.GetFilename()
        extension = os.path.splitext( file.filename )[1]
        # Проверяем расширение, если не прошло, возвращаем пустую строку
        if not self.IsAllowed( extension ) :
            return ""
        # Изначальное имя для файла, с оригинальным расширением
        origname  = f"{ filename }{ extension }"
        # Файл в формате .wav
        wavname   = f"{ filename }.wav"
        file.save( f"{ self.filedir }/{ origname }" )
        # Если расширение не .wav конвертим в .wav
        if not extension.lower() == '.wav' :
            os.system( f"ffmpeg -i { self.filedir }/{ origname } -ar 16000 -ac 1 { self.filedir }/{ wavname } -y" )
        
        return wavname
    def GetTextFromWav( self , path ) :
        # Распознаем текст
        wavfile   = wave.open( f"{ self.filedir }/{ path }" , 'rb' )
        speechrec = KaldiRecognizer( self.model , wavfile.getframerate() )
        # Читаем файл
        result = []
        while True:
            data = wavfile.readframes( 4000 )
            # Если данные закончились, обрываем цикл
            if len( data ) == 0 :
                break
            # Кладём считанную фреймдату в массив, если она считалась
            if speechrec.AcceptWaveform( data ) :
                obj = json.loads( speechrec.Result() )
                result.append( obj[ 'text' ] )
        # Собираем массив в текст
        speechtext = ", ".join( str( e ) for e in result )
        with open( f"{ self.textdir }/{ path }.txt" , 'w' , encoding = 'utf-8' ) as f :
            f.write( speechtext )
        return speechtext
        
    def GetTextFromFile( self , file ) :
        wav  = self.ConvertFile( file )
        # Если wav пустой, значит файл не прошёл проверку
        if wav == "" :
            return ""
        text = self.GetTextFromWav( wav )
        return text