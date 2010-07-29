import sys

if sys.version_info[0] == 2:
    def print(*args):
        print *args

def output(arg):
    print("MANUAL: arg=", arg)


def main():
    import vimpdb; vimpdb.set_trace()
    for abc in range(10):
        output(abc)

if __name__ == "__main__":
    main()
