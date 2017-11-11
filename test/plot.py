import matplotlib.pyplot as plt
import numpy as np


# plt.plot([1, 2, 3, 4], [1, 4, 9, 16], 'ro')
# plt.axis([0, 6, 0, 20])
# plt.show()

# t = np.arange(0., 5., 0.2)
# plt.plot(t, t, 'r--', t, t ** 2, 'bs', t, t ** 3, 'g^')


def f(t):
    return np.exp(-t) * np.cos(2 * np.pi * t)


t1 = np.arange(0, 5, 0.1)
t2 = np.arange(0, 5, 0.02)

plt.figure('demo1')
plt.subplot(2, 2, 1)
plt.plot(t1, f(t1), 'bo', t2, f(t2), 'r--')

plt.subplot(2, 2, 2)
plt.plot(t2, np.cos(2 * np.pi * t2), 'r--')
plt.plot([1, 2, 3, 4], [1, 4, 9, 16])

plt.subplot(2, 1, 2)
plt.plot([1, 2, 3, 4], [1, 4, 9, 16])

plt.figure('demo2')
plt.plot(t1, f(t1), 'bo', t2, f(t2), 'r--')

plt.show()
