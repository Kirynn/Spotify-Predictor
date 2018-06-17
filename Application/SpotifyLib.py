import requests
import webbrowser
from kutils import prettyDict

class SpotifyError(Exception):

    def __init__(self, message, errors):

        super().__init__(message)
        self.errors = errors

class Spotify(object):

    def __init__(self):

        self._base = 'https://api.spotify.com'
        self._tokens = {'access': None, 'refresh': None}
        self._refreshData = {'id': None, 'secret': None, 'timeout': None}

    def getToken(self, ID, secret, callback):

        if ((ID or secret or callback) == ''): raise ValueError('ID, secret and callback cannot be empty')

        base = 'https://accounts.spotify.com/authorize/'
        url = f'{base}?client_id={ID}&response_type=code&redirect_uri={callback}&show_dialog=false&scope=user-library-read'
        webbrowser.open(url)
        
        code = input('Please enter the url you were redirected too: \n> ')

        self._refreshData['id'] = ID
        self._refreshData['secret'] = secret
        code = code[code.find('=')+1:]

        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': callback,
            'client_id': self._refreshData['id'],
            'client_secret': self._refreshData['secret']
            }
        url = 'https://accounts.spotify.com/api/token'
        req = requests.post(url, data=payload)
        response = req.json()
        self._tokens['access'] = response['access_token']
        self._tokens['refresh'] = response['refresh_token']
        self._refreshData['timeout'] = response['expires_in']

    def _makeRequest(self, url):

        if (self._tokens['access'] == None): raise ValueError('Access Token cannot be None')

        header = {'Authorization':'Bearer '+self._tokens['access']}
        resp = requests.get(url, headers=header)

        if ('error' in resp): return f'ERROR ({url}) see below:\n {prettyDict(r)}'
        else: return resp.json()

    def searchSingle(self, search, getMetaData):

        query = '+'.join(search.split(' '))

        url = f'{self._base}/v1/search?q={query}&type=track&limit=1'
        req = self._makeRequest(url)

        if (len(req['tracks']['items']) > 0):

            try: 

                search = req['tracks']['items'][0]

                data = {'Album': search['album']['name'],
                        'Artists': [artist['name'] for artist in search['artists']],
                        'Name': search['name'],
                        'URI': search['uri']}

            except KeyError: 

                print(req)

            except:

                raise SpotifyError('Something went very very wrong \n' + f'{req}, {url}')

            finally:

                track = Track(**data)
                if (getMetaData): track.metaData = self.getTrackMetaData(track.ID)
                return track

        else:

            print ('No Search Results')

    def getTrackByURI(self, URI, getMetaData):
        
        url = f'{self._base}/v1/tracks/{URI.replace("spotify:track:", "")}'
        req = self._makeRequest(url)

        try: 

            data = {'Album': req['album']['name'],
                    'Artists': [artist['name'] for artist in req['artists']],
                    'Name': req['name'],
                    'URI': req['uri']}

        except KeyError: 

            print(req)

        except:

            print('Something went very very wrong')
            print(f'{req}, {url}')

        track = Track(**data)
        if (getMetaData): track.metaData = self.getTrackMetaData(track.ID)
        return track

    def getTrackMetaData(self, trackID):

        if (self.validMetaData == None): raise ValueError('Set validMetaData before continuing')
        
        url = f'{self._base}/v1/audio-features/{trackID}'
        req = self._makeRequest(url)

        return {k:req[k] for k in self.validMetaData}

class Track(object):
    
    def __init__(self, **kwargs):

        self._metaData = None
        self.Name = kwargs['Name']
        self.Artists = kwargs['Artists']
        self.Album = kwargs['Album']
        self.URI = kwargs['URI']
        self.ID = kwargs['URI'].replace('spotify:track:', '')

    @property
    def metaData(self):

        return self._metaData

    @metaData.setter
    def metaData(self, value):

        if (not isinstance(value, dict)): raise TypeError('Value must be of type dict')
        else: self._metaData = value

    def __str__(self):

        return f'{self.Name} by {" & ".join(self.Artists)}'
