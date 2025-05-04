import socket, screeninfo, json, math
import pygame as  pg

pg.init()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(("localhost", 10000))

scr_width = screeninfo.get_monitors()[0].width / 2
scr_height = screeninfo.get_monitors()[0].height / 2

pg.display.set_caption("ping-pong")
screen = pg.display.set_mode((scr_width, scr_height))

vector = ""
old_vector = ""
fps = 60
font = pg.font.Font(None, math.ceil(scr_width * (20/640)))

score1 = font.render("P1: " + str(0), True, "green")
score1_rect = score1.get_rect()

running = True
clock = pg.time.Clock()

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    keys = pg.key.get_pressed()
    if keys[pg.K_w] and not keys[pg.K_s]:
        vector = json.dumps({"move": "up"})
    elif keys[pg.K_s] and not keys[pg.K_w]:
        vector = json.dumps({"move": "down"})
    else:
        vector = json.dumps({"move": "no"})

    if vector != old_vector:
        old_vector = vector
        try:
            sock.send(vector.encode())
        except:
            pass

    try:
        data = json.loads(sock.recv(1024).decode())
    except:
        pass

    screen.fill("black")
    
    try:
        pg.draw.rect(screen, data["p1"]["colour"], pg.Rect(scr_width * (data["p1"]["x"]/640), scr_height * (data["p1"]["y"]/360), scr_width * (data["p1"]["width"]/640), scr_height * (data["p1"]["height"]/360)))
    except:
        pass
    try:
        pg.draw.rect(screen, data["p2"]["colour"], pg.Rect(scr_width * (data["p2"]["x"]/640), scr_height * (data["p2"]["y"]/360), scr_width * (data["p2"]["width"]/640), scr_height * (data["p2"]["height"]/360)))
    except:
        pass
    try:
        pg.draw.circle(screen, "white", (scr_width * data["ball"]["center"][0]/640, scr_height * data["ball"]["center"][1]/360,), scr_width * (data["ball"]["radius"]/640))
    except:
        pass
    
    try:
        score1 = font.render("P1: " + str(data["p1"]["score"]), True, "green")
        score2 = font.render("P2: " + str(data["p2"]["score"]), True, "green")
    except:
        score1 = font.render("P1: " + str(0), True, "green")
        score2 = font.render("P2: " + str(0), True, "green")

    screen.blit(score1, (scr_width * (200/640), scr_height * (10/640)))
    screen.blit(score2, (scr_width - score1_rect.width - scr_width * (200/640), scr_height * (10/640)))

    clock.tick(fps)
    pg.display.update()
pg.quit()