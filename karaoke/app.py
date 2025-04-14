from flask import Flask, render_template, request, redirect, url_for
import qrcode
import socket

app = Flask(__name__)
song_queue = []  # In-memory list

# Generate local IP
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/')
def request_page():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_song():
    name = request.form['name']
    song = request.form['song']
    song_queue.append({'name': name, 'song': song})
    return redirect(url_for('request_page'))

@app.route('/queue')
def view_queue():
    return render_template('queue.html', queue=song_queue)

@app.route('/qrcode')
def get_qr():
    return app.send_static_file('qrcode.png')

if __name__ == '__main__':
    host_ip = get_local_ip()
    qr = qrcode.make(f'http://{host_ip}:5001/')
    qr.save('static/qrcode.png')
    print(f"Karaoke app running! Access it at http://{host_ip}:5001/")
    app.run(host='0.0.0.0', port=5001, debug=True)
