import struct
import zlib

def make_png(width, height, pixels_func, path):
    """Generate a simple PNG from a pixel function (x,y) -> (r,g,b,a)."""
    def make_chunk(chunk_type, data):
        return struct.pack('>I', len(data)) + chunk_type + data + struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr = make_chunk(b'IHDR', ihdr_data)

    raw = b''
    for y in range(height):
        raw += b'\x00'
        for x in range(width):
            r, g, b, a = pixels_func(x, y)
            raw += bytes([r, g, b, a])
    idat = make_chunk(b'IDAT', zlib.compress(raw))
    iend = make_chunk(b'IEND', b'')

    with open(path, 'wb') as f:
        f.write(sig + ihdr + idat + iend)

def make_icon(fg, bg, shape, path):
    W, H = 64, 64
    def px(x, y):
        cx, cy = W/2, H/2
        if shape == 'home':
            # House shape
            roof = y >= 16 and y < 30 and abs(x - cx) <= (30 - y) * 1.2
            body = y >= 26 and y < 52 and abs(x - cx) <= 14
            door = y >= 40 and y < 52 and abs(x - cx) <= 4
            fill = roof or body
            is_door = door
            if fill:
                if is_door:
                    return fg[0], fg[1], fg[2], 255
                return fg[0], fg[1], fg[2], 255
            return 0, 0, 0, 0
        elif shape == 'book':
            # Open book shape
            top = y >= 18 and y < 22
            left_page = y >= 22 and y < 50 and x >= 12 and x <= 30
            right_page = y >= 22 and y < 50 and x >= 34 and x <= 52
            spine = x == 32 and y >= 18 and y < 50
            lines = y in [28, 36, 44] and ((x >= 14 and x <= 28) or (x >= 36 and x <= 50))
            fill = top or left_page or right_page or spine or lines
            if fill:
                if lines:
                    return 255, 255, 255, 255
                return fg[0], fg[1], fg[2], 255
            return 0, 0, 0, 0
        elif shape == 'user':
            # Person shape
            head = (x - cx)**2 + (y - 22)**2 <= 10**2
            body = y >= 34 and y < 52 and abs(x - cx) <= 12
            fill = head or body
            if fill:
                return fg[0], fg[1], fg[2], 255
            return 0, 0, 0, 0
        return 0, 0, 0, 0

    make_png(W, H, px, path)

out = "C:/Users/35864/Desktop/全国大学生18届/mini-program/miniprogram/assets/tabbar"

# Default color (gray)
gray = (142, 142, 147)
# Active color (green)
green = (7, 193, 96)

make_icon(gray, (255,255,255), 'home', f"{out}/home.png")
make_icon(green, (255,255,255), 'home', f"{out}/home-active.png")
make_icon(gray, (255,255,255), 'book', f"{out}/book.png")
make_icon(green, (255,255,255), 'book', f"{out}/book-active.png")
make_icon(gray, (255,255,255), 'user', f"{out}/user.png")
make_icon(green, (255,255,255), 'user', f"{out}/user-active.png")

print("TabBar icons generated.")