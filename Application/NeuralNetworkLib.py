import numpy
import time
import json
import pathlib

class NeuralNetwork(object):

    def __init__(self, layers, load = None):

        numpy.random.seed(1)
        self._weights = [2 * numpy.random.random((l, layers[p + 1])) -1 for p, l in enumerate(layers[:-1])]
        self.predict = self.think = self.feedForward # Alias

        if (isinstance(load, str)):

            self.loadNetwork(load)

    def __repr__(self):

        return f'[Object] NeuralNetwork: {self._weights}'

    @property
    def weights(self):

        return self._weights
        
    def _sigmoid(self, z):
    
        return 1 / (1 + numpy.exp(-z))

    def _sigmoidPrime(self, z):

        return z * (1 - z)

    def clean(self, toClean):

        return round(toClean, 0)
    
    def feedForward(self, inputs, training = False):

        layers = [inputs]
        for p, weight in enumerate(self._weights):

            layers.append(self._sigmoid(numpy.dot(layers[p], weight)))
            
        if training: return layers
        else: return layers[-1]

    def train(self, inputs, outputs, epochs, LOG = False, save = None):

        startingError = 0
        startTime = time.time()

        if (LOG):
            
            layers = self.feedForward(inputs, training = True)
            startingError = numpy.mean(numpy.abs(outputs.T - layers[-1]))
                
        for epoch in range(epochs):

            layers = self.feedForward(inputs, training = True)              # Get networks output

            layersError = [0 for layer in range(len(layers) - 1)]           # Minus one as we dont count the first layer
            layersAdjustment = [0 for layer in range(len(layers) - 1)]      # See above comment

            # layers[-1] = networks output

            layersError[-1] = outputs.T - layers[-1]

            if (LOG and epoch % (epochs*(1/5000)) == 0):

                percentageComplete = round((epoch/epochs) * 100, 2)
                length = 19 + len(str(epochs))*2
                
                print(f"[Epoch [{epoch}/{epochs}] ({percentageComplete}%)]".ljust(length),
                       "Error: " + str(numpy.mean(numpy.abs(layersError[-1]))))

            layersAdjustment[-1] = layersError[-1] * self._sigmoidPrime(layers[-1])

            for i in range(len(layersError[:-2]), -1, -1):
 
                layersError[i] = layersAdjustment[i + 1].dot(self._weights[i + 1].T)
                layersAdjustment[i] = layersError[i] * self._sigmoidPrime(layers[i + 1])

            for i in range(len(self._weights) - 1, -1, -1):

                self._weights[i] += layers[i].T.dot(layersAdjustment[i])

        if (LOG):

            finalTime = time.time()
            layers = self.feedForward(inputs, training = True)
            finalError = round(numpy.mean(numpy.abs(outputs.T - layers[-1])), 5)

            print(f'Training Complete Over {epochs} epochs In {round(finalTime - startTime, 2)}s',
                  f'Total Error Change: {finalError - startingError}')


        if (save != None):

            self.saveNetwork(f'{save}.config')

        else:

            if(input('Would you like to save this network? [Y/N] ').lower() == 'y'):

                self.saveNetwork(f'{input("Enter a save name: ")}.config')

    def interactive(self):

        userInput = input('>>> ').lower()
        while(userInput != 'quit'):

            if userInput == 'load':

                pass

            elif userInput == 'save':

                pass

            elif userInput == 'train':

                pass

            userInput = input('>>> ').lower() 

    def loadNetwork(self, name):

        try:
            config = None
            with open(f'{name}.config', 'r') as data:
                config = json.loads(data.read())
            self._weights = [numpy.asarray(w) for w in config['Weights']]
            print(f'Load Successful: {self.weights}')
                
        except IOError:

            print('IOError: File does not exist')
    
    def saveNetwork(self, name):
        
        file = pathlib.Path(f'/{name}')
        if (file.exists()):
            file.unlink()

        dataToSave = {'Layers': len(self._weights), 'Weights': [w.tolist() for w in self.weights]}
        
        with open(name, "w+") as data:

            data.write(json.dumps(dataToSave))
            print('Save Successful!')

if __name__ == '__main__':
    
    inputs = numpy.array([[9, 0, 1], [0, 9, 1], [9, 9, 9], [1, 1, 9], [9, 1, 0], [1, 1, 0], [0, 1, 9], [1, 9, 0], [9, 0, 0], [9, 1, 0], [1, 1, 1]])
    outputs = numpy.array([[1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0]])

    network = NeuralNetwork([3, 4, 1])
    print(end="\n\n")

    network.train(inputs, outputs, 10000, LOG = True)

    print(network.predict(numpy.array([1, 0, 1]))[0])
    print(network.feedForward(numpy.array([1, 0, 0])))
    print(network.feedForward(numpy.array([9, 0, 0])))
