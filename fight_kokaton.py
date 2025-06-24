import os
import random
import sys
import math
import time
import pygame as pg

WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5   # 爆弾の数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル.
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.dire = (+5, 0)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)

class Score:
    """
    スコアを表示するクラス
    """
    def __init__(self):
        """
        スコア表示用のフォントや初期値を設定する
        """
        self.fonto = pg.font.SysFont("microsoftjhenghei", 30) # 環境に依存しないデフォルトフォント
        self.color = (0, 0, 255)
        self.score = 0
        self.img = self.fonto.render(f"スコア: {self.score}", True, self.color)
        self.rct = self.img.get_rect()
        self.rct.center = (100, HEIGHT - 50)

    def update(self, screen: pg.Surface):
        """
        現在のスコアで文字列Surfaceを再生成し、画面に描画する
        """
        self.img = self.fonto.render(f"スコア: {self.score}", True, self.color)
        screen.blit(self.img, self.rct)

class Beam:
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird):
        # birdの向きに応じてビームの速度vx, vyを設定 
        self.vx, self.vy = bird.dire

        # ビームの角度を計算し、画像を回転させる 
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.img = pg.transform.rotozoom(pg.image.load("fig/beam.png"), angle, 1.0)

        self.rct = self.img.get_rect()

        # ビームの初期位置を、こうかとんの中心および向きに合わせて調整 
        self.rct.centerx = bird.rct.centerx + bird.rct.width * self.vx / 5
        self.rct.centery = bird.rct.centery + bird.rct.height * self.vy / 5

    def update(self, screen: pg.Surface):
        """
        ビームを速度vxにしたがって移動させる
        引数 screen: 表示対象のスクリーンSurface
        """
        # 4. 設定した速度に応じて座標を更新 
        self.rct.move_ip(self.vx, self.vy)

        # 5. 更新後の座標にビームの画像をスクリーンにblit（描画） 
        screen.blit(self.img, self.rct)  


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Explosion:
    """
    爆発エフェクトに関するクラス
    """
    def __init__(self, bomb: Bomb, life: int):
        """
        爆発エフェクトを生成する
        引数1 bomb: 爆発した爆弾（Bombクラスのインスタンス）
        引数2 life: 爆発エフェクトの表示時間（フレーム数）
        """
        img = pg.image.load("fig/explosion.png")
        self.imgs = [img, pg.transform.flip(img, True, True)] # 通常画像と上下左右反転した画像のリスト
        self.img_idx = 0
        self.rct = self.imgs[0].get_rect()
        self.rct.center = bomb.rct.center # 爆発の中心を、元々爆弾がいた位置に設定
        self.life = life # 表示時間を設定

    def update(self, screen: pg.Surface):
        """
        表示時間が残っている間、爆発アニメーションを更新して描画する
        引数 screen: 描画対象のスクリーンSurface
        """
        self.life -= 1 # 表示時間を1減らす
        # 3フレームごとに画像を切り替えることで、チカチカするアニメーションを表現
        if self.life % 3 == 0:
            self.img_idx = (self.img_idx + 1) % len(self.imgs)

        # 現在のフレームで表示すべき画像を選択
        img_to_show = self.imgs[self.img_idx]
        screen.blit(img_to_show, self.rct)

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    score = Score()
    
    # 複数のオブジェクトを管理するためのリストを準備
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beams = []
    exps = []

    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)] # bomb変数をbombsリストに変更
    beam = None
    clock = pg.time.Clock()
    tmr = 0
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # 複数のビームをリストに追加する
                beams.append(Beam(bird))
                beam = Beam(bird)
        
        screen.blit(bg_img, [0, 0])
        
        for i, bomb in enumerate(bombs):
            # ビームと爆弾の衝突判定
            if beam is not None:
                if beam.rct.colliderect(bomb.rct):
                    beam = None
                    bombs[i] = None
                    bird.change_img(6, screen)

            # こうかとんと爆弾の衝突判定
            if bomb is not None:
                if bird.rct.colliderect(bomb.rct):
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(1)
                    return
        
        # forループの外でリストを更新
        bombs = [bomb for bomb in bombs if bomb is not None]

        screen.blit(bg_img, [0, 0])

        # --- 当たり判定 ---
        # ビームと爆弾の当たり判定
        for i, beam in enumerate(beams):
            for j, bomb in enumerate(bombs):
                if beam is not None and bomb is not None:
                    if beam.rct.colliderect(bomb.rct):
                        beams[i] = None
                        bombs[j] = None
                        bird.change_img(6, screen)
                        score.score += 1
                        exps.append(Explosion(bomb, 50)) # 爆発エフェクトを生成

        # こうかとんと爆弾の当たり判定
        for bomb in bombs:
            if bomb is not None:
                if bird.rct.colliderect(bomb.rct):
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(1)
                    return

        # --- 不要になったインスタンスをリストから削除 ---
        bombs = [bomb for bomb in bombs if bomb is not None]
        beams = [beam for beam in beams if beam is not None and check_bound(beam.rct)[0]]
        exps = [exp for exp in exps if exp.life > 0]

        # --- 各オブジェクトの更新と描画 ---
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        for bomb in bombs:
            bomb.update(screen)
        for beam in beams:
            beam.update(screen)
        for exp in exps:
            exp.update(screen)
        score.update(screen)

        pg.display.update()
        if beam is not None:
            beam.update(screen)
            
        pg.display.update() # 画面更新の呼び出し
        
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
