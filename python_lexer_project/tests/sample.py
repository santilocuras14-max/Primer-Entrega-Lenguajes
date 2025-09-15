
# sample.py: casos de prueba
def fib(n):
    '''Retorna la secuencia de Fibonacci hasta n (exclusivo).'''
    a, b = 0, 1
    out = []
    for i in range(n):
        out.append(a)
        a, b = b, a + b  # suma
    return out

if __name__ == "__main__":
    for v in fib(10):
        print(v)
