
import math

frame_rate = 60*1000/1001
line_rate = 262.5 * frame_rate
line_duration = 1000000/line_rate
color_sub_carrier = line_rate*455/2
color_burst_duration = 9*1000000/color_sub_carrier
start_of_burst = 19*1000000/color_sub_carrier
line_blanking_interval = 39*1000000/color_sub_carrier


def magic(ratio):
    return 2*math.pi * 9 / (color_burst_duration*10*ratio)


def give_ntsc_signal(r, g, b, t, ratio):
    r = r * 100
    g = g * 100
    b = b * 100

    w = magic(ratio)

    y = 0.299*r + 0.587*g + 0.114*b
    i = 0.736*(r-y) - 0.269*(b-y)
    q = 0.478*(r-y) + 0.413*(b-y)

    ntsc = y+q*math.sin(w*t+(2*math.pi*33/360))+i*math.cos(w*t+(2*math.pi*33/360))

    return ntsc


def write_front_porch(line, d):
    for i in range(d):
        line.append(0)


def write_sync_tip(line, d):
    for i in range(d):
        line.append(-40)


def write_breezeway(line, d):
    for i in range(d):
        line.append(0)


def write_back_porch(line, d):
    for i in range(d):
        line.append(0)


def write_color_burst(line, t, d, ratio, is_odd):
    size = len(line)

    odd = 180 if is_odd else 0
    for i in range(d):
        line.append(math.sin((2*math.pi*odd/360)+magic(ratio)*(t+size+i))*20)


def write_active_video(line, t, d, ratio, data):
    size = len(line)

    for i in range(compute_length(3, ratio)):
        line.append(7.5)

    for i in range(len(data)):
        r, g, b = data[i]
        line.append(give_ntsc_signal(r/255, g/255, b/255, t + len(line), ratio))

    for i in range(size+d-len(line)):
        line.append(0)


def write_horizontal_blanking(line, ratio, t, odd, front_porch):
    # Line-blanking interval (µs) 10.9±0.2
    should_end_at = len(line) + compute_length(line_blanking_interval*10, ratio) - front_porch
    # Synchronizing pulse (µs)
    write_sync_tip(line, compute_length(47, ratio))  # 4.7±0.1
    # Start of sub-carrier burst (µs)
    write_breezeway(line, compute_length(start_of_burst*10, ratio)-len(line))  # 5.3 - 4.7 = 0.6
    # Duration of sub-carrier burst (µs)
    write_color_burst(line, t, compute_length(10*color_burst_duration, ratio), ratio, odd)  # 2.23 to 3.11(9±1 cycles)

    write_back_porch(line, should_end_at - len(line))


def compute_length(duration, ratio):
    return int(duration*ratio)


def get_video_length(ratio):
    return compute_length(528.56,ratio)


def write_line(t, ratio, data, front_porch):

    line = []

    maxt = 2*math.pi/magic(ratio)
    while t > maxt:
        t -= maxt

    write_horizontal_blanking(line, ratio, t, True, front_porch)
    write_active_video(line, t, get_video_length(ratio), ratio, data)

    front_porch = compute_length(635.555, ratio) - len(line)
    for i in range(front_porch):
        line.append(0)

    return line


def write_equalizing_pulse(line, ratio):
    H = 635.555/2
    for i in range(compute_length(20, ratio)):
        line.append(-40)
    for i in range(compute_length(H, ratio)-compute_length(20, ratio)):
        line.append(0)


def write_sync_pulse(line, ratio):
    H = 635.555/2
    for i in range(compute_length(H, ratio)-compute_length(20, ratio)):
        line.append(-40)
    for i in range(compute_length(20, ratio)):
        line.append(0)


def write_field_sync_odd(ratio):
    line = []
    for i in range(6):
        write_equalizing_pulse(line, ratio)
    for i in range(5):
        write_sync_pulse(line, ratio)
    for i in range(5):
        write_equalizing_pulse(line, ratio)
    return line


def write_field_sync_even(ratio):
    line = []
    for i in range(5):
        write_equalizing_pulse(line, ratio)
    for i in range(5):
        write_sync_pulse(line, ratio)
    for i in range(4):
        write_equalizing_pulse(line, ratio)
    return line
