import sensor, pyb, ustruct, time

# ---------- 常量 ----------
HEAD  = 0x40
TAIL  = 0x23
UART_BAUD = 9600

# ---------- 外设初始化 ----------
uart = pyb.UART(3, UART_BAUD, timeout_char=1000)

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)      # 320×240
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.skip_frames(time=2000)

# ---------- 任务函数 ----------
def task_qrcode():
    while True:
        img = sensor.snapshot()
        for qr in img.find_qrcodes():
            try:
                val = int(qr.payload())
            except ValueError:
                continue

            if 0 <= val <= 255:                     # 协议范围
                pkt = ustruct.pack(">BBB", HEAD, val, TAIL)
                uart.write(pkt)
                time.sleep_ms(100)

                # ★保留退出通道：主机发 0xFF 表示结束任务
                if uart.read(1) == b'\xFF':
                    return
        time.sleep_ms(300)

# 任务映射表，方便后续扩展
TASK_MAP = {
    0x01: task_qrcode,
    # 0x10: task_other,
}

# ---------- 主循环 ----------
while True:
    buf = uart.read(3)            # 只处理固定 3 字节帧
    if not buf or len(buf) != 3:
        continue

    if buf[0] == HEAD and buf[2] == TAIL:
        task_code = buf[1]
        func = TASK_MAP.get(task_code)
        if func:
            func()                # 执行任务，任务函数结束后回到待机
        else:
            uart.write(b'ERR')     # 未知任务
