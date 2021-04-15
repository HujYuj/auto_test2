from stopit import threading_timeoutable as timeoutable
import time
@timeoutable()
def test():
    for i in range(10):
        print(i)
        time.sleep(1)
print(test(timeout=5))