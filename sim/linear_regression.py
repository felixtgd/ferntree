import numpy as np


class LinearRegressionModel():
    def __init__(self, dataset: str, features: int = 3, outputs: int = 6, expand: bool = False) -> None:
        self.dataset = str(dataset) # csv file with training data
        self.features = int(features) # input features
        self.outputs = int(outputs) # output features
        self.expand = bool(expand) # expand training data

    def preprocess_data(self):
        # Load training data from csv file
        X, Y = self.get_training_data()

        # Expand training data
        if self.expand:
            X, Y = self.expand_training_data(X, Y)

        # Apply feature scaling to input features X
        X, means, stds = self.feature_scaling(X)
        # Add bias term to input features X
        X = self.add_bias(X)

        self.X = X # input features
        self.Y = Y # output features
        self.means = means # mean of each column of X
        self.stds = stds # standard deviation of each column of X

    def expand_training_data(self, X, Y):
        # Year of construction: 1850 - 2001
        years = np.arange(1850, 2002, 1)
        # Concatenate years three times
        years = np.concatenate((years, years, years))
        # Sort years in ascending order
        years = np.sort(years)

        X_train = np.zeros((len(years), 3))
        X_train[:, 0] = years
        Y_train = np.zeros((len(years), 6))

        for i, year in enumerate(years):
            if year <= 1859:
                n = 0
            elif year > 1859 and year <= 1918:
                n = 1
            elif year > 1918 and year <= 1948:
                n = 2
            elif year > 1948 and year <= 1957:
                n = 3
            elif year > 1957 and year <= 1968:
                n = 4
            elif year > 1968 and year <= 1978:
                n = 5
            elif year > 1978 and year <= 1983:
                n = 6
            elif year > 1983 and year <= 1994:
                n = 7
            elif year > 1994 and year <= 2001:
                n = 8

            X_train[i, 1:] = X[i%3 + (n * 3), 1:]
            Y_train[i, :] = Y[i%3 + (n * 3), :]

        return X_train, Y_train

    def get_training_data(self):
        data = []
        with open(self.dataset, 'r') as file:
            lines = file.readlines()
            for line in lines:
                row = line.strip().split(',')
                data.append(row)
        
        if len(data) == 0:
            raise ValueError("No data in the file")
        
        data = np.array(data)
        if data.shape[1] != self.features + self.outputs:
            raise ValueError("Number of columns in the file does not match the number of features and outputs")
        
        # Split the data into input features and output features
        # First three columns are input features
        # Last six columns are output features
        X = np.array(data)[1:, :self.features].astype(float) # ["yoc", "area", "renov"]
        Y = np.array(data)[1:, self.features:].astype(float) # ["Ai", "Ce", "Ci", "Rea", "Ria", "Rie"]

        return X, Y
    
    def feature_scaling(self, X):
        # Get mean of each column
        means = np.mean(X, axis=0)
        # Get standard deviation of each column
        stds = np.std(X, axis=0)
        # Normalise the input features
        X = (X - means) / stds

        return X, means, stds
    
    def add_bias(self, X):
        # Add bias term to input features
        X = np.insert(X, 0, 1, axis=1)

        return X
    
    def train_model(self, n_iterations=100, learning_rate=0.1):
        self.preprocess_data()
        
        X = self.X
        Y = self.Y
        
        print("Training model...")
        print(f"X: {X.shape}, Y: {Y.shape}")
        
        # Determine the number of input features, output features, and samples
        n_samples = X.shape[0]
        n_features = X.shape[1]
        n_outputs = Y.shape[1]
        
        # Initialise the weights and biases
        np.random.seed(0)
        theta = np.random.randn(n_features, n_outputs)

        # Train the model
        loss = np.zeros(n_iterations)
        for i in range(n_iterations):
            # Calculate predictions with dot product X * theta
            Y_pred = np.dot(X, theta)

            # Calculate loss function
            loss[i] = np.mean((Y_pred - Y)**2) / 2

            # Calculate the gradient of the loss function
            grad = np.dot(X.T, (Y_pred - Y)) / n_samples

            # Update the weights and biases
            theta -= learning_rate * grad

            if i % 10 == 0:
                print(f"Iteration {i}: loss = {loss[i]:.4f}")

        print(f"Final loss: {loss[-1]:.4f}")

        self.theta = theta # weights and biases
    
    def predict(self, X_pred):
        # Normalise the input features and add bias
        X_pred = (X_pred - self.means) / self.stds
        X_pred = np.insert(X_pred, 0, 1, axis=1)

        # Calculate predictions
        Y_pred = np.dot(X_pred, self.theta)

        return Y_pred

