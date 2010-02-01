from scitools.std import *

# data in two-dimensional array, the elements in a row form
# a cluster of bars, one cluster for each row:
data = array([[0.2, 1], [0.4, 0.8], [0.3, 0.6]])
figure()
bar(data,
    barticks=['method1', 'method2',  'method3'],
    legend=('optimized', 'standard'),
    axis=[-1,data.shape[0], 0,1.2],
    ylabel='normalized CPU-time',
    title='Comparison of optimized vs. standard run')

# equivalent dictionary:
data = {'method1': {'optimized': 0.2, 'standard': 1},
        'method2': {'optimized': 0.4, 'standard': 0.8},
        'method3': {'optimized': 0.3, 'standard': 0.6},
        }
figure()
bar(data)

raw_input("Press Return key to quit: ")
