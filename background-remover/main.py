import sys
import os
import tkinter as tk
#import zlib
from modules.Inflate import inflate_decompress

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

def process_path(path):
    if not os.path.exists(path):
        return None
    
    binary_data = None
    try:
        with open(path, 'rb') as f:
            binary_data = bytearray(f.read())
    except Exception as e:
        print("Error reading file: {0}".format(e))
    finally:
        return binary_data
    
def read_type_file(data):
    if len(data) >= 8 and data[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    else:
        return None

def binary_to_png(data):
    width = height = depth = color_type = compression_method = interlace_method = None
    IDAT_data = bytearray()

    offset = 8
    while offset < len(data):
        chunk_length = int.from_bytes(data[offset:offset + 4], 'big')
        chunk_type = data[offset + 4: offset + 8]

        offset += 8

        if chunk_type == b'IHDR':
            width = int.from_bytes(data[offset:offset + 4], 'big')
            height = int.from_bytes(data[offset + 4:offset + 8], 'big')
            depth = data[offset + 8]
            color_type = data[offset + 9]
            compression_method = data[offset + 10]
            interlace_method = data[offset + 11]
        elif chunk_type == b'IDAT':
            IDAT_data.extend(data[offset:offset + chunk_length])
        elif chunk_type == b'IEND':
            break
        else:
            print('Unknown chunk type: {chunk_type}')
        
        offset += chunk_length + 4

    #decompressed_data = zlib.decompress(IDAT_data)
    decompressed_data = inflate_decompress(IDAT_data)

    img_matrix = []
    offset = 0
    for row in range(height):
        row_pixels = []
        offset += 1
        for col in range(width):
            r = decompressed_data[offset]
            g = decompressed_data[offset + 1]
            b = decompressed_data[offset + 2]
            row_pixels.append((r, g, b))
            offset += 3
        img_matrix.append(row_pixels)

    return img_matrix

def display_rgb_matrix(data):
    tk_root = tk.Tk()
    width = len(data[0])
    height = len(data)

    img = tk.PhotoImage(width=width, height=height)
    color_data = []
    for y in range(height):
        row = []
        if(len(data[y]) == width):
            for x in range(width):
                r, g, b = data[y][x]
                color_hex = f'#{r:02x}{g:02x}{b:02x}'
                row.append(color_hex)
            color_data.append("{" + " ".join(row) + "}")
    img.put(" ".join(color_data))

    tk_lbl = tk.Label(tk_root, image=img)
    tk_lbl.pack()
    tk_root.mainloop()

def main():
    args = read_args(sys.argv)
    if 'filepath' not in args:
        print("Not filepath found")
        sys.exit(1)
    else: 
        binary_data = process_path(args['filepath'])
        if binary_data is None:
            print("Binary data not found")
            sys.exit(1)

        filetype = read_type_file(binary_data)
        if(filetype == 'png'):
            img_matrix = binary_to_png(binary_data)
            display_rgb_matrix(img_matrix)
            print(img_matrix)
    
if __name__ == '__main__':
    main()