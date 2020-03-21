

import pygame

from pinyin2hanzi import Pinyin2Hanzi


pygame.init()
pygame.key.set_repeat(300, 100)


class TextBox:
    _font = pygame.font.SysFont('dengxian', 16)
    _py2hz = Pinyin2Hanzi()

    _text = ''
    _max_show = 9
    _text_offset = 8
    _state = 0
    _row = 0
    _col = 0
    _current_max_col = _max_show
    _current_row = 0
    _current_col = 0
    _candidate = []

    def __init__(self, size):
        self.size = size
        self.text = ''
        self.focus=False

    def update(self, event):
        if not self.focus: return

        if event.type == pygame.KEYDOWN:
            if self._text:
                if event.key == pygame.K_SPACE:
                    self._state = 1

                elif event.key in [pygame.K_UP]:
                    self._current_col -= 1
                    if self._current_col < 0:
                        if self._current_row > 0:
                            self._current_row -= 1
                            self._current_max_col = len(self._candidate[self._current_row])
                            self._current_col = self._current_max_col - 1
                        else:
                            self._current_col = 0
                
                elif event.key in [pygame.K_DOWN]:
                    self._current_col += 1
                    if self._current_col >= self._current_max_col:
                        if self._current_row + 1 < len(self._candidate):
                            self._current_row += 1
                            self._current_max_col = len(self._candidate[self._current_row])
                            self._current_col = 0
                        else:
                            self._current_col = self._current_max_col - 1
            else:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]

        elif event.type == pygame.TEXTEDITING and (event.text or self._text):
            text = event.text.replace("'", '')
            if text == self._text:
                return
            self._text = text
            hz = []
            if text:
                hz = self._py2hz.py2hz(text)
            self.set_candidate(hz)

        elif event.type == pygame.TEXTINPUT:
            if self._text:
                if self._state == 1 and self._candidate:
                    self.text += self._candidate[self._current_row][self._current_col][1]
                else:
                    self.text += self._text
            else:
                self.text += event.text
            self._text = ''
            self._state = 0
            self.set_candidate([])

    def set_candidate(self, candidate):
        if candidate:
            width = []
            words = []
            for hz in candidate:
                n = 0
                if hz[-1] == 1:
                    n = len(''.join(hz[0])) - len(self._text)
                s = ''.join(hz[1][0])
                if hz[-1] == 2:
                    s += hz[0][-1]
                words.append(["'".join(hz[0]), s, n])
                width.append(self._font.size('8.' + s)[0])
            row = 0
            col = 0
            blank_width = self._font.size(' ')[0]
            line_w = 0
            ret = []
            i = 0
            while i < len(width):
                if col == 0:
                    ret.append([])
                line_w += width[i]
                if col != 0:
                    line_w += blank_width
                if line_w > self.size[0] - self._text_offset * 2 or col >= self._max_show:
                    row += 1
                    if col == 0:
                        ret[-1].append(words[i])
                    else:
                        col = 0
                        line_w = 0
                        continue
                else:
                    col += 1
                    ret[-1].append(words[i])
                i += 1
            self._candidate = ret
            self._current_max_col = len(self._candidate[0])
        else:
            self._candidate = []
            self._current_max_col = 0
        self._current_row = 0
        self._current_col = 0

    def render(self):
        surf = pygame.Surface(self.size)
        surf.fill([250, 250, 250])
        pygame.draw.line(surf, [230, 230, 230], [0, self.size[1] // 2], [self.size[0], self.size[1] // 2], 1)
        pygame.draw.rect(surf, [0, 0, 0], surf.get_rect(), 1)

        offset = self._text_offset
        height = self._font.get_height()
        offsetY1 = (self.size[1] // 2 - height) // 2
        offsetY2 = (self.size[1] // 2 - height) // 2 + self.size[1] // 2
        if self.text:
            text_surf = self._font.render(self.text, 1, [0, 0, 0])
            surf.blit(text_surf, [offset, offsetY1])
            offset += text_surf.get_size()[0]
        if self._candidate:
            py, hz, n = self._candidate[self._current_row][self._current_col]
            self._font.set_underline(True)
            py_surf = self._font.render(py[:-n if n else None], 1, [0, 0, 0])
            surf.blit(py_surf, [offset, offsetY1])
            if n:
                completion_surf = self._font.render(py[-n:], 1, [255, 0, 255])
                surf.blit(completion_surf, [offset + py_surf.get_size()[0], offsetY1])
            self._font.set_underline(False)

            hzs = []
            offset = 8
            for i, (_, hz, _) in enumerate(self._candidate[self._current_row]):
                if i != self._current_col:
                    hzs.append('%d.%s' % (i + 1, hz))
                if i + 1 == self._current_col:
                    hzs = ' '.join(hzs)
                    hzs_surf = self._font.render(hzs, 1, [0, 0, 0])
                    surf.blit(hzs_surf, [offset, offsetY2])
                    offset += hzs_surf.get_size()[0]
                if i == self._current_col:
                    hzs = '%d.%s' % (i + 1, hz)
                    if i != 0:
                        hzs = ' ' + hzs
                    hzs_surf = self._font.render(hzs, 1, [255, 0, 255])
                    surf.blit(hzs_surf, [offset, offsetY2])
                    offset += hzs_surf.get_size()[0]
                    hzs = []
                if i + 1 == len(self._candidate[self._current_row]) and i != self._current_col:
                    hzs = ' '.join(hzs)
                    if i != 0:
                        hzs = ' ' + hzs
                    hzs_surf = self._font.render(hzs, 1, [0, 0, 0])
                    surf.blit(hzs_surf, [offset, offsetY2])
                    offset += hzs_surf.get_size()[0]
        elif self._text:
            _text_surf = self._font.render(self._text, 1, [0, 0, 0])
            surf.blit(_text_surf, [offset, offsetY1])
        return surf


def main():
    text_box = TextBox([400, 60])
    text_box.focus = True

    pygame.display.set_caption('')
    screen = pygame.display.set_mode([640, 480])
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            text_box.update(event)
        screen.fill([240, 240, 240])
        screen.blit(text_box.render(), [120, 210])
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()