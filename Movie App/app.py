from flask import Flask, render_template, request
import requests

app = Flask(__name__)

TMDB_API_KEY = '8e652554b8631ad7f966e0501a942671'
BASE_URL = 'https://api.themoviedb.org/3'

@app.route('/', methods=['GET', 'POST'])
def index():
    movies = []
    actor_name = ""
    
    if request.method == 'POST':
        actor_name = request.form.get('actor_name')
        if actor_name:
            # Најди го актерот
            search_person = requests.get(f"{BASE_URL}/search/person", params={
                'api_key': TMDB_API_KEY, 'query': actor_name
            }).json()

            if search_person['results']:
                actor_id = search_person['results'][0]['id']
                
                # Земи филмови на македонски јазик
                mk_credits = requests.get(f"{BASE_URL}/person/{actor_id}/movie_credits", params={
                    'api_key': TMDB_API_KEY, 'language': 'mk-MK'
                }).json().get('cast', [])

                # Земи филмови на англиски јазик 
                en_credits = requests.get(f"{BASE_URL}/person/{actor_id}/movie_credits", params={
                    'api_key': TMDB_API_KEY, 'language': 'en-US'
                }).json().get('cast', [])

                # Комбинирај ги - ако мк е празно, земи од англиски
                en_map = {m['id']: m['overview'] for m in en_credits}
                
                for movie in mk_credits:
                    # Опис на македонски и англиски јазик
                    if not movie.get('overview'):
                        movie['overview'] = en_map.get(movie['id'], "No description available.")
                    movies.append(movie)

                movies = sorted(movies, key=lambda x: x.get('popularity', 0), reverse=True)

    return render_template('index.html', movies=movies, query=actor_name)

if __name__ == '__main__':
    app.run(debug=True)