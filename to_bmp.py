import ntsc
from PIL import Image

line_duration = 635.555
res_x = 1000
ratio = res_x / line_duration
print(1000000 * res_x / (line_duration / 10))

def write_frames(tabline):
    frame = []
    t = 0

    line = ntsc.write_field_sync_even(ratio)
    t += len(line)
    frame.extend(line)

    front_porch=17

    for i in range(262):
        line = ntsc.write_line(t, ratio, tabline[i*2+1], front_porch)
        t += len(line)
        frame.extend(line)

    line = ntsc.write_line(t, ratio, tabline[263*2+1], front_porch)[0:int(res_x/2)]
    t += len(line)
    frame.extend(line)

    line = ntsc.write_field_sync_odd(ratio)
    t += len(line)
    frame.extend(line)

    line = ntsc.write_line(t, ratio, tabline[0], front_porch)[int(res_x/2):res_x-1]
    t += len(line)
    frame.extend(line)

    for i in range(262):
        line = ntsc.write_line(t, ratio, tabline[i*2], front_porch)
        t += len(line)
        frame.extend(line)
    return frame


im = Image.open("ps1.png")
pix = im.convert('RGB')
tabline = []
for j in range(528):
    line = []
    for i in range(ntsc.get_video_length(ratio)):
        line.append(pix.getpixel((int(i*im.size[0]/ntsc.get_video_length(ratio)), int(im.size[1]*j/528))))
    tabline.append(line)

frame = write_frames(tabline)
img = Image.new('L', (res_x, int(len(frame)/res_x)+1), "black")
pixels = img.load()  # Create the pixel map

for i in range(1000):
    frame.append(-40)

for j in range(int(img.size[1]/2)):
    for i in range(img.size[0]):    # For every pixel:
        p = j*img.size[0]+i
        v = int((frame[p] + 40) * 255/160)
        pixels[i, j*2] = v  # Set the colour accordingly
for j in range(int(img.size[1]/2)):
    for i in range(img.size[0]):    # For every pixel:
        p = j*img.size[0]+i
        v = int((frame[p] + 40) * 255/160)
        pixels[i, j*2+1] = v  # Set the colour accordingly

img.save('test.bmp','BMP')
img.show()