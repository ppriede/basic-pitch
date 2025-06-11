from flask import Flask, request, send_file, redirect, url_for
import tempfile
import os

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('audio_file')
        if not file or file.filename == '':
            return redirect(request.url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as inp:
            file.save(inp.name)
            _, midi_data, _ = predict(inp.name, ICASSP_2022_MODEL_PATH)
            out_fd, out_path = tempfile.mkstemp(suffix='.mid')
            os.close(out_fd)
            midi_data.write(out_path)
        return send_file(out_path, as_attachment=True, download_name='transcription.mid')

    return '''
    <!doctype html>
    <title>Basic Pitch Web</title>
    <h1>Upload audio file</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=audio_file accept="audio/*">
      <input type=submit value=Transcribe>
    </form>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
