# Creamos las funciones de manejo de bits 

def get_bits(input_buf, input_pos, bit_offset, num_bits):
    result = 0
    for i in range(num_bits): # Iterar tantos bits como queremos leer
        if input_pos >= len(input_buf): # Comprobar que el byte que queremos leer existe
            return None, None, None

        current_byte = input_buf[input_pos] # Obtenemos el byte de la posición input_pos
        bit = (current_byte >> bit_offset) & 1 # Hacemos una mascara para obtener el bit de la posición bit_offset
        result |= bit << i # Añadir el bit que hemos leído al resultado

        bit_offset += 1 # Pasamos al siguiente bit
        if bit_offset == 8: # Comparamos con 8 porque el último bit de un byte es el 8 (un byte tiene 8 bits)
            bit_offset = 0
            input_pos += 1 # Pasamos al siguiente byte
    return result, input_pos, bit_offset


def reverse_bits(value, bit_length):
    result = 0
    for _ in range(bit_length):
        result = (result << 1) | (value & 1) # Desplazamos un bit de result a la izquierda y añadimos un bit de value
        value >>= 1 # Desplazamos un bit de value a la derecha y asi queda el siguiente bit
    return result


# Creamos las funciones de codificación de Huffman
def generate_huffman_codes(code_length):
    max_code_length = max(code_length)
    bl_count = [0] * (max_code_length + 1)
    for length in code_length:
        bl_count[length] += 1

    code = 0
    next_code = [0] * (max_code_length + 1)
    for bits in range(1, max_code_length):
        code = (code + bl_count[bits-1]) << 1
        next_code[bits] = code
    
    huffman_code = {}
    for n in range(len(code_length)):
        length = code_length[n]
        if length != 0:
            code = next_code[length]
            next_code[length] += 1
            code_reverse = reverse_bits(code, length)
            huffman_code[code_reverse] = {'symbol': n, 'length': length}
    return huffman_code

def read_code(input_buf, input_pos, bit_offset, huffman_codes):
    max_code_length = max(code_info['length'] for code_info in huffman_codes.values())
    code = 0
    for i in range(1, max_code_length):
        bit, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, 1)
        if bit is None or input_pos is None or bit_offset is None:
            return None, None, None
        code |= bit << (i - 1) 
        print(f"Code {code} - Huffman codes {huffman_codes[code]} - Huffman codes code length {huffman_codes[code]['length']} - i: {i}\n")
        if code in huffman_codes and huffman_codes[code]['length'] >= i:
            symbol = huffman_codes[code]['symbol']
            return symbol, input_pos, bit_offset 
    print("Invalid code in compressed data")
    return None, None, None

# Creamos las funciones de descompresión INFLATE

def inflate_decompress_uncompressed(input_buf, input_pos, bit_offset, output_buf):
    if bit_offset != 0:
        bit_offset = 0
        input_buf += 1
    
    if input_pos + 4 > len(input_buf):
        print("Invalid uncompressed block: not enough data")
        return None, None
    
    len_bytes = input_buf[input_pos:input_pos + 2]
    nlen_bytes = input_buf[input_pos + 2:input_pos + 2]
    input_pos += 4

    len_value = len_bytes[0] | (len_bytes[1] << 8)
    nlen_value = nlen_bytes[0] | (nlen_bytes[1] << 8)

    if len_value != (~nlen_value & 0xFFFF):
        print("Invalid uncompressed block: len and nlen not complementary")
        return None, None
    
    if input_pos + len_value > len(input_buf):
        print("Invalid uncompressed block: length exceeds input size")
        return None, None
    
    output_buf.extend(input_buf[input_pos:input_pos + len_value])
    input_pos += len_value
    return input_pos, bit_offset

def inflate_decompress_static_huffman(input_buf, input_pos, bit_offset, output_buf):
    while True:
        value, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, 8)
        if value is None or input_pos is None or bit_offset is None:
            return None, None
        
        if value < 256:
            output_buf.append(value)
        elif value == 256:
            break
        else:
            print("Error in length")
    return input_pos, bit_offset

def inflate_decompress_dynamic_huffman(input_buf, input_pos, bit_offset, output_buf):
    # Read HLIT (5 bit)
    hlit, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, 5)
    if hlit is None or input_pos is None or bit_offset is None:
        return None
    hlit += 257 # Nº de codigos literales/length
    
    # Read HDIST (5 bit)
    hdist, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, 5)
    if hdist is None or input_pos is None or bit_offset is None:
        return None
    hdist += 1 # Nº de codigos de distancia/distance

    # Read HCLEN (4 bit)
    hclen, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, 4)
    if hclen is None or input_pos is None or bit_offset is None:
        return None
    hclen += 4 # Nº de longitud de códigos

    # Leer Huffman codes length
    code_length_order = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11 , 4, 12, 3, 13, 2, 14, 1, 15]
    code_length_code_length = [0] * 19
    for i in range(hclen):
        length, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, 3)
        if length is None or input_pos is None or bit_offset is None:
            return None
        code_length_code_length[code_length_order[i]] = length
    
    # Generar códigos de Huffman
    code_length_codes = generate_huffman_codes(code_length_code_length)

    # Leer las longitudes de los codigos para los literales y distancias
    total_code_lengths = hlit + hdist
    code_lengths = []

    while len(code_lengths) < total_code_lengths:
        symbol, input_pos, bit_offset = read_code(input_buf, input_pos, bit_offset, code_length_codes)
        if input_pos is None or bit_offset is None:
            return None, None
        if symbol <= 15:
            code_lengths.append(symbol)
        elif symbol == 16:
            if len(code_lengths) == 0:
                print("Error: no se ha encontrado código repetido")
                return None, None 
            prev_code_length = code_lengths[-1]
            repeat_count, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, 2)
            if repeat_count is None and input_pos is None and bit_offset:
                return None, None
            repeat_count += 3
            code_lengths.extend([prev_code_length] * repeat_count)
        elif symbol == 17:
            repeat_count, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, 3)
            if repeat_count is None and input_pos is None and bit_offset:
                return None, None
            repeat_count += 3
            code_lengths.extend([0] * repeat_count)
        elif symbol == 18:
            repeat_count, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, 7)
            if repeat_count is None and input_pos is None and bit_offset:
                return None, None
            repeat_count += 11
            code_lengths.extend([0] * repeat_count)
        else:
            print("Error invalid symbol")
            return None, None 
    
    if len(code_lengths) != total_code_lengths:
        print("Incorrect number of code lengths")
        return None, None
    
    litlen_code_lengths = code_lengths[:hlit]
    distlen_code_lengths = code_lengths[hlit:]

    litlen_codes = generate_huffman_codes(litlen_code_lengths)
    dist_codes = generate_huffman_codes(distlen_code_lengths)

    while True:
        symbol, input_pos, bit_offset = read_code(input_buf, input_pos, bit_offset, litlen_codes)
        if symbol is not None or input_pos is None or bit_offset is None:
            return None, None
        if symbol < 256:
            output_buf.append(symbol)
        elif symbol == 256:
            break
        else:
            length_extra_bits_table = [
	            (257, 3, 0), (258, 4, 0), (259, 5, 0), (260, 6, 0),
	            (261, 7, 0), (262, 8, 0), (263, 9, 0), (264, 10, 0),
	            (265, 11, 1), (266, 13, 1), (267, 15, 1), (268, 17, 1),
	            (269, 19, 2), (270, 23, 2), (271, 27, 2), (272, 31, 2),
	            (273, 35, 3), (274, 43, 3), (275, 51, 3), (276, 59, 3),
	            (277, 67, 4), (278, 83, 4), (279, 99, 4), (280, 115, 4),
	            (281, 131, 5), (282, 163, 5), (283, 195, 5), (284, 227, 5),
	            (285, 258, 0)
	        ]
            for code, base_length, extra_bits in length_extra_bits_table:
                if code == symbol:
                    length_base = base_length
                    extra_bits_length = extra_bits
                    break
            
            extra_length = 0
            if extra_bits_length > 0:
                extra_length, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, extra_bits_length)
                if extra_length is None or input_pos is None or bit_offset is None:
                    return None
            length = length_base + extra_length

            dist_symbol, input_pos, bit_offset = read_code(input_buf, input_pos, bit_offset, dist_codes)
            if dist_symbol is None or input_pos is None or bit_offset is None:
                return None, None
            dist_extra_bits_table = [
	            (0, 1, 0), (1, 2, 0), (2, 3, 0), (3, 4, 0),
	            (4, 5, 1), (5, 7, 1), (6, 9, 2), (7, 13, 2),
	            (8, 17, 3), (9, 25, 3), (10, 33, 4), (11, 49, 4),
	            (12, 65, 5), (13, 97, 5), (14, 129, 6), (15, 193, 6),
	            (16, 257, 7), (17, 385, 7), (18, 513, 8), (19, 769, 8),
	            (20, 1025, 9), (21, 1537, 9), (22, 2049, 10), (23, 3073, 10),
	            (24, 4097, 11), (25, 6145, 11), (26, 8193, 12), (27, 12289, 12),
	            (28, 16385, 13), (29, 24577, 13)
	        ]
            if dist_symbol > 29:
                print("Invalid distance code")
                return None
            dist_base_value = dist_extra_bits_table[dist_symbol][1]
            extra_bits_dist = dist_extra_bits_table[dist_symbol][2]
            extra_distance = 0
            if extra_bits_dist > 0:
                extra_distance, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, extra_bits_dist)
                if extra_distance is None or input_pos is None or bit_offset is None:
                    return None
                distance = dist_base_value + extra_distance
                if distance > len(output_buf):
                    print("Invalid distance")
                    return None, None
                for _ in range(length):
                    output_buf.append(output_buf[-distance])
    return input_pos, bit_offset

# Creamos la función principal de descompresión
def inflate_decompress(input_buf):
    input_pos = 0 # Bytes donde empezamos a leer el buffer de entrada
    bit_offset = 0 # Bits donde empezamos a leer el buffer de entrada
    output_buf = bytearray() 

    # Manejar encabezado ZLIB
    if len(input_buf) < 2:
        return None
    
    zlib_header = input_buf[0] << 8 | input_buf[1]
    if (zlib_header % 31) != 0:
        print("Invalid ZLIB header")
        return None
    
    input_pos += 2
    while True:
        is_final, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, 1)
        if is_final is None or input_pos is None or bit_offset is None:
            return None
        
        if is_final:
            break

        block_type, input_pos, bit_offset = get_bits(input_buf, input_pos, bit_offset, 2)
        if block_type is None or input_pos is None or bit_offset is None:
            return None
        
        if block_type == 0: # Uncompressed block
            input_pos, bit_offset = inflate_decompress_uncompressed(input_buf, input_pos, bit_offset, output_buf)
        elif block_type == 1: # Static Huffman
            input_pos, bit_offset = inflate_decompress_static_huffman(input_buf, input_pos, bit_offset, output_buf)
        elif block_type == 2: # Dynamic Huffman
            input_pos, bit_offset = inflate_decompress_dynamic_huffman(input_buf, input_pos, bit_offset, output_buf)
        else:
            print("Invalid block type")
            return None
        
        if input_pos is None or bit_offset is None:
            return None
    
    return output_buf

    
