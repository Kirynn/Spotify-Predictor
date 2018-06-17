from NeuralNetworkLib import NeuralNetwork
import SpotifyLib
import callbackHost
import json
import numpy
import sys
import threading

def FormatData(data):

    return list(data.metaData.values())

def CleanResult(result):

    return f'{round(result[0] * 100, 2)}%'

if __name__ == '__main__':

    thread = threading.Thread(target = callbackHost.Run)
    thread.start()

    # Import settings
    with open('settings.json') as settings:

        SETTINGS = json.load(settings)

    spotify = SpotifyLib.Spotify()
    spotify.getToken(SETTINGS['ID'], SETTINGS['Secret'], SETTINGS['Callback'])
    spotify.validMetaData = [key for key in SETTINGS['ValidMetaData']]

    try:

        if (sys.argv[1] == '-genNet'):

            print('Loading Input Library')

            with open(SETTINGS['InputLibrary']) as file:
                   
                library = json.load(file)
                LibraryInputs = [spotify.getTrackByURI(i, getMetaData = True) for i in library['Likes']] + [spotify.getTrackByURI(i, getMetaData = True) for i in library['Dislikes']]
                LibraryOutputs = [1 for i in library['Likes']] + [0 for i in library['Dislikes']]

            inputs = numpy.array([[*FormatData(i)] for i in LibraryInputs])
            outputs = numpy.array([LibraryOutputs])

            network = NeuralNetwork(SETTINGS['NetworkLayers'])

            print('Training Network')
            network.train(inputs, outputs, SETTINGS['Epochs'], LOG = True, save = SETTINGS['NetworkName'])
            print(f'Trained Network to: {network.weights}')

        else:

            print('Unknown Arg')

    except IndexError:
        
        network = NeuralNetwork(SETTINGS['NetworkLayers'], SETTINGS['NetworkName'])

        while(True):

            track = spotify.searchSingle(input('Enter a song to search for: '), getMetaData = True)
            print(f'Predicting: {track}...')
            print(CleanResult(network.predict(FormatData(track))))