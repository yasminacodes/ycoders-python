import sys

def read_args(argv):
    output = {}
    i = 1
    while i < len(argv):
        if argv[i] == '-f' and len(argv) > i + 1:
            output['filepath'] = argv[i + 1]
            i += 2
        else:
            i += 1
    return output

def main():
    args = read_args(sys.argv)
    if 'filepath' not in args:
        filepath = None
        print("Not filepath found")
        sys.exit(1)
    
if __name__ == '__main__':
    main()