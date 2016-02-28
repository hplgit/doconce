import numpy as np

def readfile(filename):
    """Read tabular data from file and return as numpy array."""
    f = open(filename, 'r')
    data = []  # list of rows in table
    for line in f:
        if line.startswith('#'):
            continue   # drop comment lines
        numbers = [float(w) for w in line.split()]
        data.append(numbers)
    return np.array(data)

def analyze(data):
    """Return statistical measures of an array data."""
    return np.mean(data), \
           np.std(data), \
           np.corrcoef(data)

if __name__ == '__main__':
    data = readfile('mydat.txt')
    # Treat each column as a variable
    m, s, c = analyze(data.transpose())
    print """
mean=%f
st.dev=%f
correlation matrix:
%s
""" % (m, s, c)
