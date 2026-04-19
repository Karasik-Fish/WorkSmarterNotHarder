from pwn import *
context.arch = "amd64"
context.log_level = "debug"
context.os = "linux"

#p = process(["/challenge/quest.py"], pty=True)
p = process(["/challenge/quest.py"], stdin=PTY, stdout=PTY)
data = p.recvn(numb=12)
res_str = ""
seen_coords = set()
# 70 x 20
main_w = 70
main_h = 20
goal_x = -1
goal_y = -1
prev_w = -1
prev_h = -1
bomb_x = -1
bomb_y = -1
pl_x = -1
pl_y = -1

sprite_counter = -1
flush_counter = 0

prev_dir_x = 0
prev_dir_y = 0

is_it_end = 0

real_goal_x = -1
real_goal_y = -1
while True:
    data = p.recvn(numb=2)
    if data:
        if u16(data) == 2:  #R_patch
            data = p.recvn(numb=4)
            base_x, base_y, w, h = struct.unpack("<4B", data)
            data = p.recvn(numb=w * h * 4)
            if real_goal_x != -1 and real_goal_y != -1:
                if (real_goal_x < base_x + w) and (real_goal_x >= base_x) and (real_goal_y < base_y + h) and (real_goal_y >= base_y):
                    #res_str += chr(data[(goal_y - base_y) * prev_w + (goal_x - base_x)])
                    index = ((real_goal_y - base_y) * w + (real_goal_x - base_x)) * 4 + 3
                    if chr(data[index]) in "-_1234567890qwertyuiop[{}]asdfghjklzxcvbnm,./QWERTYUIOPASDFGHJKLZXCVBNM":
                        res_str += chr(data[index])
                        real_goal_x = -1
                        real_goal_y = -1
                        print("asddsad")
                        print(res_str)
            for i in range(h):
                for u in range(w):
                    if data[i * w * 4 + u * 4 + 3] == ord("?"):
                        goal_x = base_x + u
                        goal_y = base_y + i
                        prev_w = w
                        prev_h = h
                    elif data[i * w * 4 + u * 4 + 3] == ord("B"):
                        bomb_x = base_x + u
                        bomb_y = base_y + i
                        prev_w = w
                        prev_h = h
        elif u16(data) == 1:
            data = p.recvn(numb=main_w * main_h * 4)
        elif u16(data) == 3:
            data = p.recvn(numb=3)
            id, w, h = struct.unpack("<3B", data)
            data = p.recvn(numb=w * h)
        elif u16(data) == 4:
            data = p.recvn(numb=9)
            sprite_counter += 1
            num, r, g, b, x, y, tile_x, tile_y, t = struct.unpack("<9B", data)
            pl_x, pl_y = x, y
        elif u16(data) == 5:
            #data = p.recvn(numb=0x102)
            data = p.recvn(numb=1)
            w, h = data[1], data[2]
        elif u16(data) == 6:
            data = p.recvn(numb=1)
            flush_counter += 1
        elif u16(data) == 7:
            data = p.recvn(numb=4)
        else:
            print("kaka prishla")
            break

        if sprite_counter != 0 and goal_x != -1 and goal_y != -1 and bomb_y != -1 and pl_y != -1 and bomb_x != -1 and pl_x != -1:
            det_x, det_y = goal_x - pl_x, goal_y - pl_y
            my_way = 0

            if det_x > 0 and prev_dir_x == 0:
                if bomb_x in (pl_x + 1, pl_x + 2, pl_x + 3) and bomb_y in (pl_y, pl_y + 1):
                    if prev_dir_y != 0:
                        if prev_dir_y < 0:
                            p.send(b"s")
                        else:
                            p.send(b"w")
                    elif pl_y > main_h // 2:
                        if prev_dir_y == 0:
                            prev_dir_y = 1
                        p.send(b"w")
                    else:
                        if prev_dir_y == 0:
                            prev_dir_y = -1
                        p.send(b"s")
                else:
                    prev_dir_y = 0
                    p.send(b"d")
            elif det_x < 0  and prev_dir_x == 0:
                if bomb_x in (pl_x - 1, pl_x, pl_x + 1) and bomb_y in (pl_y, pl_y + 1):
                    if prev_dir_y != 0:
                        if prev_dir_y < 0:
                            p.send(b"s")
                        else:
                            p.send(b"w")
                    elif pl_y > main_h // 2:
                        if prev_dir_y == 0:
                            prev_dir_y = 1
                        p.send(b"w")
                    else:
                        if prev_dir_y == 0:
                            prev_dir_y = -1
                        p.send(b"s")
                else:
                    prev_dir_y = 0
                    p.send(b"a")
            elif det_y > 0:
                if bomb_y in (pl_y + 1, pl_y + 2) and bomb_x in (pl_x, pl_x + 1, pl_x + 2):
                    if prev_dir_x != 0:
                        if prev_dir_x < 0:
                            p.send(b"a")
                        else:
                            p.send(b"d")
                    elif pl_x > main_w // 2:
                        if prev_dir_x == 0:
                            prev_dir_x = -1
                        p.send(b"a")
                    else:
                        if prev_dir_x == 0:
                            prev_dir_x = 1
                        p.send(b"d")
                else:
                    prev_dir_x = 0
                    p.send(b"s")
            elif det_y < 0:
                if bomb_y in (pl_y - 1, pl_y) and bomb_x in (pl_x, pl_x + 1, pl_x + 2):
                    if prev_dir_x != 0:
                        if prev_dir_x < 0:
                            p.send(b"a")
                        else:
                            p.send(b"d")
                    elif pl_x > main_w // 2:
                        if prev_dir_x == 0:
                            prev_dir_x = -1
                        p.send(b"a")
                    else:
                        if prev_dir_x == 0:
                            prev_dir_x = 1
                        p.send(b"d")
                else:
                    prev_dir_x = 0
                    p.send(b"w")
            else:
                prev_dir_y = 0
                prev_dir_x = 0
                real_goal_x = goal_x
                real_goal_y = goal_y
                print(real_goal_x, real_goal_y)
                p.send(b"l")

            sprite_counter = 0
            is_it_end = 0

        elif flush_counter >= 1 and sprite_counter == -1:
            sprite_counter = 0
            is_it_end = 0
            p.send(b"\n")
        else:
            is_it_end += 1
            if is_it_end == 1000:
                p.send(b"\x03")
                break

    else:
        print("pysto")
        break

print("asddsad")
print(res_str)