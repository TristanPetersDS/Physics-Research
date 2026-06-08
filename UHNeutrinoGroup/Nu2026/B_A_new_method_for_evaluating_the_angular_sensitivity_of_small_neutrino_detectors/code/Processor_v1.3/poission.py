import numpy as np
from scipy.stats import poisson
import matplotlib.pyplot as plt

# Example data
data = np.random.poisson(5, 1000)

# Fit the Poisson distribution
mu = np.mean(data)  # Estimate lambda (rate parameter) from the data
dist = poisson(mu)

# Plot the histogram of the data and the fitted Poisson distribution
plt.hist(data, bins=np.arange(data.max() + 2) - 0.5, density=True, alpha=0.5, label='Data')
x = np.arange(0, data.max() + 1)
plt.plot(x, dist.pmf(x), 'ro-', label='Fitted Poisson')
plt.xlabel('Number of Events')
plt.ylabel('Probability')
plt.legend()
plt.show()
