from decimal import Decimal
from decimal import getcontext
import sys

def pi(precision):
    getcontext().prec=precision
    return sum(1/Decimal(16)**k * 
        (Decimal(4)/(8*k+1) - 
         Decimal(2)/(8*k+4) - 
         Decimal(1)/(8*k+5) -
         Decimal(1)/(8*k+6)) for k in range (precision))

n = int(sys.argv[1])
pi(n)
print("COMPLETED BARE METAL PI with N: " + str(n))
