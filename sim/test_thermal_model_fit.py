import numpy as np

from linear_regression import LinearRegressionModel


# Create linear regression model for model parameters of 3R2C thermal model
lr_model = LinearRegressionModel('3R2C_model_params.csv', features=3, outputs=6)
lr_model.train_model(n_iterations=100, learning_rate=0.1)

# Expand training data by creating one data point for each year
lr_model_exp = LinearRegressionModel('3R2C_model_params.csv', features=3, outputs=6, expand=True)
lr_model_exp.train_model(n_iterations=100, learning_rate=0.1)

# Model with yoc as average of period: Final loss = 2.1793
# Model with yoc as expanded period: Final loss = 1.8301

#X_test, Y_test = lr_model.get_training_data()
X_test, Y_test = lr_model_exp.get_training_data()
X_test, Y_test = lr_model_exp.expand_training_data(X_test, Y_test)
# Get random subset of test data
idx = np.random.choice(X_test.shape[0], 10, replace=False)
X_test = X_test[idx] 
Y_test = Y_test[idx]
print(X_test.shape)

Y_pred_org = lr_model.predict(X_test)
Y_pred_exp = lr_model_exp.predict(X_test)

loss_org = np.mean((Y_pred_org - Y_test)**2) / 2
loss_exp = np.mean((Y_pred_exp - Y_test)**2) / 2

print(f"Original model: Final loss = {loss_org:.4f}")
print(f"Expanded model: Final loss = {loss_exp:.4f}")



X_test = np.array([[2005.5, 133, 1],
                    [2005.5, 133, 2],
                    [2005.5, 133, 3],
                    [2012.5, 160, 1],
                    [2012.5, 160, 2],
                    [2012.5, 160, 3],
                    [2016.0, 160, 1],
                    [2016.0, 160, 2],
                    [2016.0, 160, 3],
                    ])

Y_pred = lr_model_exp.predict(X_test)
print(Y_pred)

## MODEL VALIDATION ---------------------------------------------
# X, Y = lr_model.get_training_data()
# # Year of construction: 1850 - 2001
# years = np.arange(1850, 2002, 1)
# # Concatenate years three times
# years = np.concatenate((years, years, years))
# # Sort years in ascending order
# years = np.sort(years)

# X_train = np.zeros((len(years), 3))
# X_train[:, 0] = years
# Y_train = np.zeros((len(years), 6))

# for i, year in enumerate(years):
#     if year <= 1859:
#         n = 0
#     elif year > 1859 and year <= 1918:
#         n = 1
#     elif year > 1918 and year <= 1948:
#         n = 2
#     elif year > 1948 and year <= 1957:
#         n = 3
#     elif year > 1957 and year <= 1968:
#         n = 4
#     elif year > 1968 and year <= 1978:
#         n = 5
#     elif year > 1978 and year <= 1983:
#         n = 6
#     elif year > 1983 and year <= 1994:
#         n = 7
#     elif year > 1994 and year <= 2001:
#         n = 8

#     X_train[i, 1:] = X[i%3 + (n * 3), 1:]
#     Y_train[i, :] = Y[i%3 + (n * 3), :]

# # idx = 453
# # print(X_train[idx:idx+3])
# # print(Y_train[idx:idx+3])



