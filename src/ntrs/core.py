import math
import zlib
import numpy as np
from typing import Tuple, Optional
from PIL import Image, ImageDraw
from reedsolo import RSCodec, ReedSolomonError

Image.MAX_IMAGE_PIXELS = None 

class NTRS:
    def __init__(self, password: str):
        self.seed_bytes = self._nebula_hash(password.encode())
        self.rs = RSCodec(10)

    def _rotate_left(self, val, r_bits, max_bits=32):
        return (val << r_bits % max_bits) & (2**max_bits-1) | \
               ((val & (2**max_bits-1)) >> (max_bits - (r_bits % max_bits)))

    def _nebula_hash(self, input_bytes: bytes, rounds: int = 64) -> bytes:
        state = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A]
        data = bytearray(input_bytes)
        while len(data) % 4 != 0: data.append(0)
        for r in range(rounds):
            for i in range(0, len(data), 4):
                chunk = int.from_bytes(data[i:i+4], 'big')
                state[0] = self._rotate_left(state[0], 7) ^ chunk
                state[1] = (state[0] + state[1] + 0x9E3779B9) % (2**32)
                state[2] = self._rotate_left(state[1], 11) ^ state[3]
                state[3] = (state[2] + state[0]) % (2**32)
                state[0], state[1], state[2], state[3] = state[3], state[0], state[1], state[2]
        output = bytearray()
        for val in state:
            output.extend(val.to_bytes(4, 'big'))
            output.extend((val ^ 0xFFFFFFFF).to_bytes(4, 'big')) 
        return bytes(output)

    def _generate_chaos_indices(self, count, seed_bytes):
        indices = np.arange(count, dtype=np.uint32)
        rounds = math.ceil((count * 4) / 32)
        chaos_buffer = bytearray()
        current_hash = seed_bytes
        for _ in range(rounds + 1):
            current_hash = self._nebula_hash(current_hash, rounds=16)
            chaos_buffer.extend(current_hash)
        chaos_ints = np.frombuffer(chaos_buffer[:count*4], dtype=np.uint32)
        return np.argsort(chaos_ints)

    def _get_coordinates_numpy(self, data: bytes) -> tuple:
        binary_str = ''.join(format(byte, '08b') for byte in data)
        coordinates = np.array([i for i, bit in enumerate(binary_str) if bit == '1'], dtype=np.uint32)
        return coordinates, len(binary_str)

    def _reconstruct_numpy(self, coordinates: np.ndarray, total_length: int) -> bytes:
        bit_array = np.zeros(total_length, dtype=np.uint8)
        if len(coordinates) > 0: bit_array[coordinates] = 1
        remainder = total_length % 8
        if remainder:
            padding = 8 - remainder
            bit_array = np.pad(bit_array, (0, padding), 'constant')
        packed = np.packbits(bit_array)
        return packed.tobytes()

    def _encrypt_coordinates_numpy(self, coordinates: np.ndarray, seed_bytes: bytes) -> bytes:
        perm_map = self._generate_chaos_indices(len(coordinates), seed_bytes)
        shuffled_coords = coordinates[perm_map]
        high_bytes = (shuffled_coords >> 8).astype(np.uint8)
        low_bytes  = (shuffled_coords & 0xFF).astype(np.uint8)
        packed_bytes = np.empty(shuffled_coords.size * 2, dtype=np.uint8)
        packed_bytes[0::2] = high_bytes
        packed_bytes[1::2] = low_bytes
        salt = b"NTRS_SALT"
        mask_seed = self._nebula_hash(seed_bytes + salt)
        rounds = math.ceil(packed_bytes.size / 32)
        mask_buffer = bytearray()
        curr = mask_seed
        for _ in range(rounds):
            curr = self._nebula_hash(curr, rounds=8)
            mask_buffer.extend(curr)
        mask_array = np.frombuffer(mask_buffer[:packed_bytes.size], dtype=np.uint8)
        return np.bitwise_xor(packed_bytes, mask_array).tobytes()

    def _decrypt_coordinates_numpy(self, data: bytes, seed_bytes: bytes) -> np.ndarray:
        encrypted_array = np.frombuffer(data, dtype=np.uint8)
        salt = b"NTRS_SALT"
        mask_seed = self._nebula_hash(seed_bytes + salt)
        rounds = math.ceil(encrypted_array.size / 32)
        mask_buffer = bytearray()
        curr = mask_seed
        for _ in range(rounds):
            curr = self._nebula_hash(curr, rounds=8)
            mask_buffer.extend(curr)
        mask_array = np.frombuffer(mask_buffer[:encrypted_array.size], dtype=np.uint8)
        decrypted_array = np.bitwise_xor(encrypted_array, mask_array)
        if decrypted_array.size % 2 != 0: decrypted_array = decrypted_array[:-1]
        high_bytes = decrypted_array[0::2].astype(np.uint32)
        low_bytes  = decrypted_array[1::2].astype(np.uint32)
        return (high_bytes << 8) | low_bytes

    def _render_2d_matrix(self, binary_string, filename):
        bits = np.array([int(c) for c in binary_string], dtype=np.uint8)
        total_bits = len(bits)
        min_radius = math.ceil(math.sqrt(total_bits / math.pi))
        radius = min_radius + 5
        width = radius * 2
        y, x = np.ogrid[-radius:radius, -radius:radius]
        mask_circle = (x*x + y*y <= radius*radius)
        available_pixels = np.count_nonzero(mask_circle)
        while available_pixels < total_bits:
            radius += 1
            width = radius * 2
            y, x = np.ogrid[-radius:radius, -radius:radius]
            mask_circle = (x*x + y*y <= radius*radius)
            available_pixels = np.count_nonzero(mask_circle)
        img_array = np.zeros((width, width, 4), dtype=np.uint8)
        img_array[mask_circle, 3] = 255
        circle_y, circle_x = np.nonzero(mask_circle)
        target_y = circle_y[:total_bits]
        target_x = circle_x[:total_bits]
        ones_indices = (bits == 1)
        final_y = target_y[ones_indices]
        final_x = target_x[ones_indices]
        img_array[final_y, final_x, 3] = 254
        img = Image.fromarray(img_array, 'RGBA')
        img.save(filename, optimize=True)

    def _scan_2d_matrix(self, input_filename):
        img = Image.open(input_filename).convert('RGBA')
        img_array = np.array(img)
        width = img_array.shape[0]
        radius = width // 2
        y, x = np.ogrid[-radius:radius, -radius:radius]
        mask_circle = (x*x + y*y <= radius*radius)
        alphas = img_array[:, :, 3]
        circle_pixels = alphas[mask_circle]
        bits = []
        for val in circle_pixels:
            if val == 254: bits.append('1')
            elif val == 255: bits.append('0')
        return "".join(bits)

    def _bytes_to_binary(self, data: bytes) -> str:
        return ''.join(format(byte, '08b') for byte in data)

    def _binary_to_bytes(self, binary_str: str) -> bytes:
        remainder = len(binary_str) % 8
        if remainder: binary_str += '0' * (8 - remainder)
        return bytes(int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8))

    def encode(self, secret_text: str, output_filename: str):
        compressed = zlib.compress(secret_text.encode())
        coords, total_bits = self._get_coordinates_numpy(compressed)
        encrypted_map = self._encrypt_coordinates_numpy(coords, self.seed_bytes)
        length_header = total_bits.to_bytes(2, 'big')
        payload = length_header + encrypted_map
        protected_data = self.rs.encode(payload)
        payload_bits = self._bytes_to_binary(protected_data)
        total_stream_len = len(payload_bits)
        outer_header = format(total_stream_len, '032b')
        final_stream = outer_header + payload_bits
        self._render_2d_matrix(final_stream, output_filename)

    def decode(self, input_filename: str) -> str:
        try:
            raw_bits = self._scan_2d_matrix(input_filename)
            if len(raw_bits) < 32: return "Error: Image too small."
            header_bits = raw_bits[:32]
            stream_len = int(header_bits, 2)
            if len(raw_bits) < 32 + stream_len: return "Error: Data truncated."
            clean_bits = raw_bits[32 : 32 + stream_len]
            try:
                protected_bytes = self._binary_to_bytes(clean_bits)
                decoded_bytes, _, _ = self.rs.decode(protected_bytes)
            except ReedSolomonError: return "Error: Data damaged."
            length_bytes = decoded_bytes[:2]
            total_bits = int.from_bytes(length_bytes, 'big')
            map_data = decoded_bytes[2:]
            coords = self._decrypt_coordinates_numpy(map_data, self.seed_bytes)
            decompressed = self._reconstruct_numpy(coords, total_bits)
            return zlib.decompress(decompressed).decode()
        except Exception as e: return "Error: " + str(e)