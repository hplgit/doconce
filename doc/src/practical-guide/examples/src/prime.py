def primes(n):
    primes = []
    prime_count = 0
    prime_candidate = 2
    while prime_count < n:
        candidate_is_prime = True
        for prime in primes:
            if prime_candidate % prime == 0:
                candidate_is_prime = False
                break
        if candidate_is_prime:
            primes.append(prime_candidate)
            prime_count += 1
        prime_candidate += 1
    return primes
