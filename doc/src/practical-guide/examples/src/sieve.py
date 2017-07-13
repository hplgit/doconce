import math
import numpy as np

def primes_up_to(n):
    non_prime = np.zeros(n+1, dtype=bool)
    non_prime[0] = True
    non_prime[1] = True
    candidate = 2
    last_candidate = math.ceil(math.sqrt(n))
    while candidate <= last_candidate:
        while non_prime[candidate]:
            candidate += 1
        i = candidate
        while i*candidate <= n:
            non_prime[i*candidate] = True
            i += 1
        candidate += 1
    primes = []
    for i in xrange(n+1):
        if not non_prime[i]:
            primes.append(i)
    return primes
