from flask import Flask, request, jsonify
from nameday_data import namedays

app = Flask(__name__)

@app.route('/api/nameday', methods=['GET'])
def get_nameday():
    country = request.args.get('country', 'cz').lower()
    date = request.args.get('date')  # format: MM-DD
    if not date:
        return jsonify({'error': 'Missing date parameter'}), 400
    names = namedays.get(country, {}).get(date)
    if names:
        return jsonify({'country': country, 'date': date, 'names': names})
    else:
        return jsonify({'country': country, 'date': date, 'names': []})

if __name__ == '__main__':
    app.run(port=5001)
