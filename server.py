import socket, json, random, math
import pygame as pg

pg.init()

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(("localhost", 10000))
main_socket.setblocking(0)
main_socket.listen(5)

print("Server stated")

class Player():
    def __init__(self, conn, addr, width, height):
        self.conn = conn
        self.addr = addr
        self.y = win_height / 2 - win_height / 6 / 2
        self.width = width
        self.height = height
        self.number = len(players) + 1
        if self.number == 1:
            self.x = 15
            self.colour = "blue"
        elif self.number == 2:
            self.x = win_width - self.width - 15
            self.colour = "red"
        self.rect = pg.rect.Rect(self.x, self.y, self.width, self.height)
        self.errors = 0
        self.data = {"move":"no"}
    def move(self):
        global players
        if len(players) == 2:
            try:
                self.data = json.loads(self.conn.recv(1024).decode())
            except:
                pass
            if self.data["move"] == "up" and self.rect.y > 0:
                self.rect.y -= speed
            if self.data["move"] == "down" and self.rect.y < win_height - self.rect.height:
                self.rect.y += speed
    def collect_data(self):
        global message, players, p1_score, p2_score
        if self.number == 1:
            if len(players) == 1:
                self.rect.x = self.x
                self.rect.y = self.y
                self.rect.width = self.width
                self.rect.height = self.height
                p1_score = 0
                p2_score = 0
                try:
                    del message["p2"]    
                except:
                    pass         
            message["p1"] = {
            "x": self.rect.x,
            "y": self.rect.y,
            "width": self.rect.width,
            "height": self.rect.height,
            "colour": self.colour,
            "score": p1_score}
        elif self.number == 2:
            if len(players) == 1:
                self.rect.x = self.x
                self.rect.y = self.y
                self.rect.width = self.width
                self.rect.height = self.height
                p1_score = 0
                p2_score = 0
                try:
                    del message["p1"]    
                except:
                    pass 
            message["p2"] = {
            "x": self.rect.x,
            "y": self.rect.y,
            "width": self.rect.width,
            "height": self.rect.height,
            "colour": self.colour,
            "score": p2_score}

class Ball():
    def __init__(self, x, y, colour, radius):
        self.x = x
        self.y = y
        self.colour = colour
        self.radius = radius
        self.rect = pg.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        self.vector = [random.choice([-1, 1]), random.choice([-1, 1])]
    def move(self):
        global speed, players
        if len(players) == 2:
            self.rect.x += speed * self.vector[0]
            self.rect.y += speed * self.vector[1]
        else:
            self.rect.x = win_width / 2
            self.rect.y = win_height / 2
    def colide(self):
        global win_height, players, p1_score, p2_score
        if self.rect.y <= 0 or self.rect.y >= win_height - self.radius * 2:
            self.vector[1] *= -1
        if self.rect.x <= 0:
            self.rect.center = (win_width / 2, random.randint(self.radius * 2, math.ceil(win_height - self.radius * 2)))
            self.vector = [random.choice([-1, 1]), random.choice([-1, 1])]
            p2_score += 1
        if self.rect.x >= win_width - self.radius * 2:
            self.rect.center = (win_width / 2, random.randint(self.radius * 2, math.ceil(win_height - self.radius * 2)))
            self.vector = [random.choice([-1, 1]), random.choice([-1, 1])]
            p1_score += 1
        for player in players:
            if self.rect.colliderect(player.rect):
                if player.number == 1:
                    self.vector[0] = 1
                else:
                    self.vector[0] = -1
    def collect_data(self):
        global message
        message["ball"] = {
            "center": self.rect.center,
            "radius": self.radius
        }

players = []

win_width, win_height = 640, 360
fps = 60
speed = 5
max_players = 2
p1_score = 0
p2_score = 0
message = {}

font = pg.font.Font(None, 20)
score1 = font.render("P1: " + str(p1_score), True, "green")
score1_rect = score1.get_rect()

ball = Ball(win_width / 2, random.randint(10, math.ceil(win_height - 10)), "white", 5)

clock = pg.time.Clock()

server_vorking = True

while server_vorking:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            server_vorking = False
    if not len(players) >= max_players:
        try:
            new_socket, addr = main_socket.accept()
            print(addr, "successfully connected")
            players.append(Player(new_socket, addr, 5, win_height / 6))
            new_socket.setblocking(0)
        except:
            pass 

    for player in players:
        try:
            player.conn.send(json.dumps(message).encode())
            player.errors = 0
        except:
            player.errors += 1
            players.remove(player)
            player.conn.close()
            print(player.addr, "disconnected")

    for player in players:
        player.move()
        player.collect_data()

    ball.colide()
    ball.move()
    ball.collect_data()

    score1 = font.render("P1: " + str(p1_score), True, "green")
    score2 = font.render("P2: " + str(p2_score), True, "green")

    clock.tick(fps)

pg.quit()
main_socket.close()