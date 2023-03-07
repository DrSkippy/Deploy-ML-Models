import json
import numpy as np
import psutil
import time

const_float = 0.346723846287346
LOAD_CALIBRATION_SCALE = 15000


def load_function(n=1):
    """
    CPU loading function
    """
    start_time = time.time()
    for _ in range(n):
        for _ in range(LOAD_CALIBRATION_SCALE):
            _ = const_float * const_float
    return 1000. * (time.time() - start_time), n, LOAD_CALIBRATION_SCALE


def memory_function(size=1):
    """
    Allocate memory for this process

    size = 1 ~ 2 MB
    """
    memory_handle = np.ones((1024, 1024, size), dtype=np.uint8)
    return memory_handle


def calibrate():
    """
    Calculate the approximate load factor for translating time into multiplications
    for this platform.
    """
    data = []
    for i in range(1, 100, 10):
        dt, n, cal = load_function(i)
        data.append(dt / float(i))
    return np.average(data)  # ms


class DelayWithStrategy:
    def __init__(self, strategy):
        self.strategy = strategy  # ms
        pass

    def sleep_remaining(self, t0, dt=None):
        if dt is None:
            dt = self.strategy.sample()  # delay in ms
        remaining = max(0, dt - t0)
        return t0 + self.sleep(dt=remaining)

    def sleep(self, dt=None):
        if dt is None:
            dt = self.strategy.sample()  # delay in ms
        dt = max(dt, 0)
        time.sleep(dt / 1000.)  # sleep in seconds
        return dt

class ConstantStrategy:
    def __init__(self, const=10):
        self.const = const  # ms

    def sample(self, size=1):
        if size == 1:
            return self.const
        else:
            return np.ones(size) * self.const

class LogNormalStrategy:

    def __init__(self, mu=10, sigma=10, seed=None):
        np.random.seed(seed)
        mu2 = mu * mu
        sigma2 = sigma * sigma
        self.a = np.log(mu2 / np.sqrt(mu2 + sigma2))
        self.b = np.sqrt(np.log(1. + (sigma2 / mu2)))

    def sample(self, size=1):
        """lognormal distributions"""
        if size == 1:
            # This value needs to be json serializable
            return float(np.random.lognormal(self.a, self.b, size=size)[0])
        else:
            # For generating a pre-deterministic list
            return np.random.lognormal(self.a, self.b, size=(size,))


class NormalStrategy:

    def __init__(self, mu=10, sigma=2, seed=None):
        np.random.seed(seed)
        self.mu = mu
        self.sigma = sigma

    def sample(self, size=1):
        """truncated normal distributions"""
        res = []
        for i in range(size):
            a = -1
            while a < 0:
                # return values must be positive
                a = float(np.random.normal(self.mu, self.sigma, size=size)[0])
            res.append(a)
        if size == 1:
            # This value needs to be json serializable
            return res[0]
        else:
            # For generating a pre-deterministic list
            return res


class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)


if __name__ == "__main__":
    i = 1
    print(f"step={i} time={time.time()} ==>");
    i += 1
    print(f"memory_info = {psutil.Process().memory_info().rss / (1024 * 1024):5.2f} MB")
    print(f"step={i} time={time.time()} ==>");
    i += 1
    a = memory_function(2)
    print(f"step={i} time={time.time()} ==>");
    i += 1
    print(f"memory_info = {psutil.Process().memory_info().rss / (1024 * 1024):5.2f} MB")
    print(f"step={i} time={time.time()} ==>");
    i += 1
    b = memory_function(4)
    print(f"step={i} time={time.time()} ==>");
    i += 1
    print(f"memory_info = {psutil.Process().memory_info().rss / (1024 * 1024):5.2f} MB")
    print(f"step={i} time={time.time()} ==>");
    i += 1
    del a
    del b
    time.sleep(2)
    print(f"step={i} time={time.time()} ==>");
    i += 1
    print(f"memory_info = {psutil.Process().memory_info().rss / (1024 * 1024):5.2f} MB")
    print(f"step={i} time={time.time()} ==>");
    i += 1
    print(f"_load_function with scale={LOAD_CALIBRATION_SCALE} takes {calibrate():5.4f} ms on this platform.")
    print(f"step={i} time={time.time()} ==>");
    i += 1
    print(f"_load_function with scale={LOAD_CALIBRATION_SCALE} takes {calibrate():5.4f} ms on this platform.")
    print(f"step={i} time={time.time()} ==>");
    i += 1
    ds = ConstantStrategy()
    print(f"delay = {ds.sample(1)}")
    print(f"delay = {ds.sample(5)}")
    print(f"step={i} time={time.time()} ==>");
    i += 1
    ds_ = DelayWithStrategy(ds)
    print(f"sleeping= {ds_.sleep()} ms")
    print(f"step={i} time={time.time()} ==>");
    i += 1
    ds = NormalStrategy()
    print(f"delay = {ds.sample(1)}")
    print(f"delay = {ds.sample(5)}")
    print(f"step={i} time={time.time()} ==>");
    i += 1
    ds_ = DelayWithStrategy(ds)
    print(f"sleeping= {ds_.sleep()} ms")
    print(f"step={i} time={time.time()} ==>");
    i += 1
    ds = LogNormalStrategy()
    print(f"delay = {ds.sample(1)}")
    print(f"delay = {ds.sample(5)}")
    print(f"step={i} time={time.time()} ==>");
    i += 1
    ds_ = DelayWithStrategy(ds)
    print(f"sleeping= {ds_.sleep()} ms")
    print(f"step={i} time={time.time()} ==>");
    i += 1
