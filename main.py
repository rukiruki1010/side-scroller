
import pygame as pg, sys, traceback
from level import Level, aabb_overlap
from inputmap import InputMap

W,H=480,270; FPS=60; SKY=(140,190,255); BLACK=(0,0,0)
PLAYER_W,PLAYER_H=16,24; MOVE=2.0; JUMP=-7.0; GRAV=0.35; MAXFALL=8.0
RED1=(220,60,60); RED2=(200,40,40); WHITE=(255,255,255)

def draw_error(screen, msg_lines):
    screen.fill((30,0,0))
    font = pg.font.Font(None, 20)
    y=10
    for ln in msg_lines[:10]:
        surf = font.render(ln, True, (255,180,180))
        screen.blit(surf, (10,y))
        y += 18
    pg.display.flip()

class Player:
    def __init__(self,x,y):
        self.rect=pg.Rect(x,y,PLAYER_W,PLAYER_H)
        self.vx=0.0; self.vy=0.0; self.on_ground=False; self.facing=1; self.coins=0; self.anim=0
    def update(self,cmds,level:Level):
        self.vx=0.0
        if cmds["left"]: self.vx-=MOVE; self.facing=-1
        if cmds["right"]: self.vx+=MOVE; self.facing=1
        if cmds["jump"] and self.on_ground: self.vy=JUMP; self.on_ground=False
        self.vy=min(self.vy+GRAV, MAXFALL)
        ref=[self.on_ground]; self.vx,self.vy=level.move_and_collide(self.rect,(self.vx,self.vy),ref); self.on_ground=ref[0]
        got=[c for c in level.coins if aabb_overlap(self.rect,c)]
        for c in got: level.coins.remove(c); self.coins+=1
        self.anim=(self.anim+1)%30 if abs(self.vx)>0.1 and self.on_ground else 0
    def draw(self,screen,cx):
        color=RED1 if self.anim<15 else RED2
        body=pg.Rect(self.rect.x-cx,self.rect.y,self.rect.w,self.rect.h)
        pg.draw.rect(screen,color,body)
        pg.draw.circle(screen,WHITE,(body.centerx+(4*self.facing), body.y+8),2)

def game_main():
    pg.init()
    screen=pg.display.set_mode((W,H)); clock=pg.time.Clock()
    font=pg.font.Font(None,18)
    level=Level("levels/level1.json"); player=Player(*level.spawn); inp=InputMap()
    camera_x=0; running=True
    while running:
        for e in pg.event.get():
            if e.type==pg.QUIT: running=False
        cmds=inp.query()
        if cmds["escape"]: running=False
        level.update_enemies(); player.update(cmds,level)
        camera_x=max(0, player.rect.centerx - W//2)
        screen.fill(SKY); level.draw(screen,camera_x); player.draw(screen,camera_x)
        screen.blit(font.render(f"Coins:{player.coins}", True, BLACK),(8,8))
        pg.display.flip(); clock.tick(FPS)
    pg.quit()

if __name__=="__main__":
    try:
        # ブート確認（赤点滅の代わりに一瞬だけ初期画面に青帯）
        pg.init()
        s=pg.display.set_mode((W,H))
        s.fill((0,30,80)); pg.display.flip()
        game_main()
    except Exception as e:
        # 例外を画面に描画 & コンソールにも出す
        tb = traceback.format_exc().splitlines()
        try:
            draw_error(pg.display.get_surface(), ["Python exception:"]+tb[-8:])
        except Exception:
            pass
        print("=== EXCEPTION ===")
        print("\\n".join(tb))
        # しばらく静止して読めるように
        import time
        time.sleep(6)
        raise
