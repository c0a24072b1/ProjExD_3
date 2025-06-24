import pygame as pg
import sys

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SAMPLE_TEXT = "日本語フォントのテスト"

def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("日本語フォントテスター (Jキーで次, Fキーで前)")

    # PCで利用可能なフォントのリストを取得
    available_fonts = pg.font.get_fonts()
    font_index = 0
    total_fonts = len(available_fonts)

    # UI表示用のデフォルトフォント
    ui_font = pg.font.Font(None, 32)

    clock = pg.time.Clock()

    while True:
        # 現在のフォント名を取得
        current_font_name = available_fonts[font_index]

        # イベント処理
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_j:  # 次のフォントへ
                    font_index = (font_index + 1) % total_fonts
                if event.key == pg.K_f:  # 前のフォントへ
                    font_index = (font_index - 1) % total_fonts
        
        # 画面を黒でクリア
        screen.fill(BLACK)

        # 現在のフォント情報を表示
        font_info_text = f"({font_index + 1}/{total_fonts}) Font: {current_font_name}"
        font_info_surface = ui_font.render(font_info_text, True, WHITE)
        screen.blit(font_info_surface, (10, 10))

        # 操作説明を表示
        instructions_text = "Jキー: 次のフォント | Fキー: 前のフォント"
        instructions_surface = ui_font.render(instructions_text, True, WHITE)
        inst_rect = instructions_surface.get_rect(center=(WIDTH/2, HEIGHT - 30))
        screen.blit(instructions_surface, inst_rect)

        # --- サンプル日本語テキストの描画 ---
        try:
            # 現在のフォントでサンプルテキストを描画してみる
            test_font = pg.font.SysFont(current_font_name, 60)
            text_surface = test_font.render(SAMPLE_TEXT, True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(text_surface, text_rect)
        except pg.error:
            # フォントの読み込みに失敗した場合
            error_text = f"'{current_font_name}'は読み込めませんでした"
            error_surface = ui_font.render(error_text, True, (255, 100, 100)) # 赤色で表示
            error_rect = error_surface.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(error_surface, error_rect)

        # 画面を更新
        pg.display.update()
        clock.tick(30)

if __name__ == "__main__":
    main()