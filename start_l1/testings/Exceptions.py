import logging


class ProductKeyNotMatchException(Exception):
    pass


class DUTNotReadyException(Exception):
    pass


class DummyException(Exception):
    pass


class L1TimeOutException(Exception):
    pass


class L1InitFailException(Exception):
    pass


class CpriSyncFailException(Exception):
    pass


if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print("catch a error!")
        logging.info(msg=e)
