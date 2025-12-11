"""
КРЕСТИКИ-НОЛИКИ с юнит-тестированием
Полный код в одном файле
"""

# ========== ОСНОВНАЯ ИГРА ==========
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.metrics import sp, dp
import random
import sys
import unittest

class MainMenuScreen(Screen):
    pass

class GameScreen(Screen):
    pass

class AnimatedButton(Button):
    scale = NumericProperty(1)
    
    def on_press(self):
        anim = Animation(scale=0.9, duration=0.1) + Animation(scale=1, duration=0.1)
        anim.start(self)

class TicTacToeApp(App):
    current_player = StringProperty('X')
    game_active = BooleanProperty(True)
    player_x_score = NumericProperty(0)
    player_o_score = NumericProperty(0)
    ties = NumericProperty(0)
    game_mode = StringProperty('friend')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = ['' for _ in range(9)]
        self.buttons = []
    
    def build(self):
        self.sm = ScreenManager()
        self.setup_menu_screen()
        self.setup_game_screen()
        return self.sm
    
    def setup_menu_screen(self):
        menu_screen = MainMenuScreen(name='menu')
        menu_layout = BoxLayout(orientation='vertical', padding=dp(50), spacing=dp(30))
        
        title_label = Label(
            text='[b]Крестики-нолики[/b]',
            font_size=sp(40),
            markup=True,
            size_hint=(1, 0.3)
        )
        menu_layout.add_widget(title_label)
        
        mode_label = Label(
            text='Выберите режим игры:',
            font_size=sp(24),
            size_hint=(1, 0.2)
        )
        menu_layout.add_widget(mode_label)
        
        mode_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint=(1, 0.5))
        
        vs_friend_btn = AnimatedButton(
            text='Играть с другом',
            font_size=sp(24),
            background_color=(0.2, 0.6, 0.2, 1),
            background_normal='',
            size_hint_y=None,
            height=dp(60),
            on_press=lambda x: self.start_game('friend')
        )
        
        vs_ai_btn = AnimatedButton(
            text='Играть с ИИ',
            font_size=sp(24),
            background_color=(0.2, 0.4, 0.8, 1),
            background_normal='',
            size_hint_y=None,
            height=dp(60),
            on_press=lambda x: self.start_game('ai')
        )
        
        mode_layout.add_widget(vs_friend_btn)
        mode_layout.add_widget(vs_ai_btn)
        menu_layout.add_widget(mode_layout)
        
        menu_screen.add_widget(menu_layout)
        self.sm.add_widget(menu_screen)
    
    def setup_game_screen(self):
        self.game_screen = GameScreen(name='game')
        self.sm.add_widget(self.game_screen)

    def start_game(self, mode):
        self.game_mode = mode
        self.reset_game()
        self.sm.current = 'game'
        self.build_game_screen()
    
    def build_game_screen(self):
        self.game_screen.clear_widgets()
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        # Верхняя панель
        top_panel = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=dp(10))
        
        back_btn = Button(
            text='← Меню',
            font_size=sp(16),
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1),
            background_normal='',
            on_press=self.back_to_menu
        )
        
        mode_info = Label(
            text=f'Режим: {"с другом" if self.game_mode == "friend" else "с ИИ"}',
            font_size=sp(18),
            halign='center'
        )
        
        self.score_label = Label(
            text=f"X: {self.player_x_score} | O: {self.player_o_score} | Ничьи: {self.ties}",
            font_size=sp(16),
            halign='right'
        )
        
        top_panel.add_widget(back_btn)
        top_panel.add_widget(mode_info)
        top_panel.add_widget(self.score_label)
        main_layout.add_widget(top_panel)
        
        # Статус игры
        self.status_label = Label(
            text=self.get_status_text(),
            font_size=sp(24),
            markup=True,
            size_hint=(1, 0.1)
        )
        main_layout.add_widget(self.status_label)
        
        # Игровое поле
        self.game_grid = GridLayout(cols=3, spacing=dp(8), size_hint=(1, 0.6))
        self.buttons = []
        
        for i in range(9):
            btn = AnimatedButton(
                text='',
                font_size=sp(50),
                background_color=(0.15, 0.15, 0.15, 1),
                background_normal='',
                on_press=lambda instance, pos=i: self.make_move(instance, pos)
            )
            self.buttons.append(btn)
            self.game_grid.add_widget(btn)
        
        main_layout.add_widget(self.game_grid)
        
        # Панель управления
        control_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint=(1, 0.15))
        
        new_game_btn = Button(
            text='Новая игра',
            font_size=sp(18),
            background_color=(0.2, 0.7, 0.3, 1),
            background_normal='',
            on_press=self.reset_game
        )
        
        control_layout.add_widget(new_game_btn)
        main_layout.add_widget(control_layout)
        
        self.game_screen.add_widget(main_layout)
        
        # Автоматический ход ИИ если нужно
        if self.game_mode == 'ai' and self.current_player == 'O':
            Clock.schedule_once(lambda dt: self.make_ai_move(), 0.5)

    def get_status_text(self):
        if self.game_mode == 'friend':
            color = "ff5555" if self.current_player == 'X' else "5555ff"
            return f"[b]Ходит игрок:[/b] [color={color}]{self.current_player}[/color]"
        else:
            if self.current_player == 'X':
                return "[b]Ваш ход[/b] [color=ff5555](X)[/color]"
            else:
                return "[b]Ходит ИИ[/b] [color=5555ff](O)[/color]"
    
    def make_move(self, button, position):
        if not self.game_active or self.board[position] != '':
            return
        
        button.text = self.current_player
        self.board[position] = self.current_player
        
        if self.current_player == 'X':
            button.background_color = (0.8, 0.2, 0.2, 1)
        else:
            button.background_color = (0.2, 0.2, 0.8, 1)
        
        anim = Animation(font_size=sp(60), duration=0.2) + Animation(font_size=sp(50), duration=0.1)
        anim.start(button)
        
        self.check_game_result()
    
    def make_ai_move(self, instance=None):
        if not self.game_active or self.game_mode != 'ai' or self.current_player != 'O':
            return
        
        available_moves = [i for i, cell in enumerate(self.board) if cell == '']
        if available_moves:
            move = self.find_winning_move('O')
            if move is None:
                move = self.find_winning_move('X')
            if move is None:
                move = self.take_center()
            if move is None:
                move = self.take_corner()
            if move is None:
                move = random.choice(available_moves)
            
            Clock.schedule_once(lambda dt: self.execute_ai_move(move), 0.7)
    
    def execute_ai_move(self, position):
        if self.game_active and self.board[position] == '':
            self.make_move(self.buttons[position], position)
    
    def find_winning_move(self, player):
        for i in range(9):
            if self.board[i] == '':
                self.board[i] = player
                if self.check_winner() == player:
                    self.board[i] = ''
                    return i
                self.board[i] = ''
        return None
    
    def take_center(self):
        return 4 if self.board[4] == '' else None
    
    def take_corner(self):
        corners = [0, 2, 6, 8]
        available_corners = [c for c in corners if self.board[c] == '']
        return random.choice(available_corners) if available_corners else None
    
    def check_game_result(self):
        winner = self.check_winner()
        
        if winner:
            self.game_active = False
            self.show_winner_popup(winner)
            self.update_score(winner)
            self.highlight_winning_line()
        elif all(cell != '' for cell in self.board):
            self.game_active = False
            self.show_tie_popup()
            self.ties += 1
            self.update_score_display()
        else:
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            self.status_label.text = self.get_status_text()
            
            if self.game_mode == 'ai' and self.current_player == 'O':
                Clock.schedule_once(lambda dt: self.make_ai_move(), 0.3)
    
    def check_winner(self):
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        
        for line in lines:
            if self.board[line[0]] == self.board[line[1]] == self.board[line[2]] != '':
                return self.board[line[0]]
        return None
    
    def highlight_winning_line(self):
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        
        for line in lines:
            if self.board[line[0]] == self.board[line[1]] == self.board[line[2]] != '':
                for pos in line:
                    anim = Animation(background_color=(0, 1, 0, 0.7), duration=0.5)
                    anim.start(self.buttons[pos])
                break
    
    def show_winner_popup(self, winner):
        if self.game_mode == 'friend':
            message = f'Игрок [color=ff5555]{winner}[/color] побеждает!' if winner == 'X' else f'Игрок [color=5555ff]{winner}[/color] побеждает!'
        else:
            if winner == 'X':
                message = '[color=00ff00]Вы победили![/color] '
            else:
                message = '[color=ff0000]ИИ победил![/color] '
        
        self.show_popup('Игра окончена!', message)
    
    def show_tie_popup(self):
        self.show_popup('Игра окончена!', 'Ничья! ')
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        message_label = Label(
            text=message,
            font_size=sp(26),
            markup=True
        )
        
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=0.4)
        
        menu_btn = Button(
            text='В меню',
            font_size=sp(18),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        
        again_btn = Button(
            text='Играть ещё',
            font_size=sp(18),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        
        def close_popup_and_action(instance, action):
            popup.dismiss()
            action()
        
        menu_btn.bind(on_press=lambda x: close_popup_and_action(x, self.back_to_menu))
        again_btn.bind(on_press=lambda x: close_popup_and_action(x, self.reset_game))
        
        button_layout.add_widget(menu_btn)
        button_layout.add_widget(again_btn)
        
        content.add_widget(message_label)
        content.add_widget(button_layout)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
        popup.open()
    
    def update_score(self, winner):
        if winner == 'X':
            self.player_x_score += 1
        else:
            self.player_o_score += 1
        self.update_score_display()
    
    def update_score_display(self):
        if hasattr(self, 'score_label'):
            self.score_label.text = f"X: {self.player_x_score} | O: {self.player_o_score} | Ничьи: {self.ties}"
    
    def reset_game(self, instance=None):
        self.board = ['' for _ in range(9)]
        self.game_active = True
        self.current_player = 'X'
        
        if hasattr(self, 'buttons'):
            for button in self.buttons:
                button.text = ''
                button.background_color = (0.15, 0.15, 0.15, 1)
                button.font_size = sp(50)
        
        if hasattr(self, 'status_label'):
            self.status_label.text = self.get_status_text()
        
        if self.game_mode == 'ai' and self.current_player == 'O':
            Clock.schedule_once(lambda dt: self.make_ai_move(), 0.5)
    
    def back_to_menu(self, instance=None):
        self.sm.current = 'menu'

# ========== ЮНИТ-ТЕСТЫ ==========

class TestTicTacToe(unittest.TestCase):
    """Юнит-тесты для игры Крестики-нолики"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.game = TicTacToeApp()
        self.game.board = [''] * 9
        self.game.game_active = True
        self.game.current_player = 'X'
    
    def test_check_winner_horizontal(self):
        """Тест: X побеждает по горизонтали"""
        self.game.board = ['X', 'X', 'X', '', '', '', '', '', '']
        self.assertEqual(self.game.check_winner(), 'X')
        
        self.game.board = ['', '', '', 'O', 'O', 'O', '', '', '']
        self.assertEqual(self.game.check_winner(), 'O')
        
        self.game.board = ['', '', '', '', '', '', 'X', 'X', 'X']
        self.assertEqual(self.game.check_winner(), 'X')
    
    def test_check_winner_vertical(self):
        """Тест: O побеждает по вертикали"""
        self.game.board = ['O', '', '', 'O', '', '', 'O', '', '']
        self.assertEqual(self.game.check_winner(), 'O')
        
        self.game.board = ['', 'X', '', '', 'X', '', '', 'X', '']
        self.assertEqual(self.game.check_winner(), 'X')
        
        self.game.board = ['', '', 'O', '', '', 'O', '', '', 'O']
        self.assertEqual(self.game.check_winner(), 'O')
    
    def test_check_winner_diagonal(self):
        """Тест: X побеждает по диагонали"""
        self.game.board = ['X', '', '', '', 'X', '', '', '', 'X']
        self.assertEqual(self.game.check_winner(), 'X')
        
        self.game.board = ['', '', 'O', '', 'O', '', 'O', '', '']
        self.assertEqual(self.game.check_winner(), 'O')
    
    def test_check_winner_no_winner(self):
        """Тест: нет победителя"""
        self.game.board = ['X', 'O', 'X', '', '', '', '', '', '']
        self.assertIsNone(self.game.check_winner())
        
        self.game.board = [''] * 9
        self.assertIsNone(self.game.check_winner())
    
    def test_check_winner_tie(self):
        """Тест: ничья"""
        self.game.board = ['X', 'O', 'X', 'X', 'O', 'O', 'O', 'X', 'X']
        self.assertIsNone(self.game.check_winner())
        self.assertTrue(all(cell != '' for cell in self.game.board))
    
    def test_find_winning_move_x(self):
        """Тест: X находит выигрышный ход"""
        self.game.board = ['X', 'X', '', '', '', '', '', '', '']
        move = self.game.find_winning_move('X')
        self.assertEqual(move, 2)
    
    def test_find_winning_move_o(self):
        """Тест: O находит выигрышный ход"""
        self.game.board = ['O', '', '', 'O', '', '', '', '', '']
        move = self.game.find_winning_move('O')
        self.assertEqual(move, 6)
    
    def test_find_winning_move_none(self):
        """Тест: выигрышного хода нет"""
        self.game.board = ['X', 'O', 'X', '', '', '', '', '', '']
        move = self.game.find_winning_move('X')
        self.assertIsNone(move)
    
    def test_take_center_empty(self):
        """Тест: центр свободен"""
        self.game.board = [''] * 9
        center = self.game.take_center()
        self.assertEqual(center, 4)
    
    def test_take_center_occupied(self):
        """Тест: центр занят"""
        self.game.board = ['', '', '', '', 'X', '', '', '', '']
        center = self.game.take_center()
        self.assertIsNone(center)
    
    def test_take_corner(self):
        """Тест: выбор угла"""
        self.game.board = [''] * 9
        corner = self.game.take_corner()
        self.assertIn(corner, [0, 2, 6, 8])
    
    def test_take_corner_no_corners(self):
        """Тест: все углы заняты"""
        self.game.board = ['X', '', 'O', '', 'X', '', 'O', '', 'X']
        corner = self.game.take_corner()
        self.assertIsNone(corner)
    
    def test_reset_game(self):
        """Тест: сброс игры"""
        # Заполняем доску
        self.game.board = ['X', 'O', 'X', 'O', 'X', 'O', 'O', 'X', 'O']
        self.game.current_player = 'O'
        self.game.game_active = False
        self.game.player_x_score = 5
        self.game.player_o_score = 3
        self.game.ties = 2
        
        # Сбрасываем
        self.game.reset_game()
        
        # Проверяем
        self.assertTrue(all(cell == '' for cell in self.game.board))
        self.assertEqual(self.game.current_player, 'X')
        self.assertTrue(self.game.game_active)
        # Счет не должен сбрасываться!
        self.assertEqual(self.game.player_x_score, 5)
        self.assertEqual(self.game.player_o_score, 3)
        self.assertEqual(self.game.ties, 2)
    
    def test_update_score_x(self):
        """Тест: обновление счета для X"""
        self.game.player_x_score = 0
        self.game.update_score('X')
        self.assertEqual(self.game.player_x_score, 1)
        self.assertEqual(self.game.player_o_score, 0)
    
    def test_update_score_o(self):
        """Тест: обновление счета для O"""
        self.game.player_o_score = 0
        self.game.update_score('O')
        self.assertEqual(self.game.player_o_score, 1)
        self.assertEqual(self.game.player_x_score, 0)
    
    def test_update_score_multiple(self):
        """Тест: несколько обновлений счета"""
        self.game.player_x_score = 0
        self.game.player_o_score = 0
        
        self.game.update_score('X')
        self.game.update_score('X')
        self.game.update_score('O')
        self.game.update_score('X')
        self.game.update_score('O')
        
        self.assertEqual(self.game.player_x_score, 3)
        self.assertEqual(self.game.player_o_score, 2)
    
    def test_game_mode(self):
        """Тест: режимы игры"""
        self.game.game_mode = 'friend'
        self.assertEqual(self.game.game_mode, 'friend')
        
        self.game.game_mode = 'ai'
        self.assertEqual(self.game.game_mode, 'ai')
    
    def test_board_size(self):
        """Тест: размер доски"""
        self.assertEqual(len(self.game.board), 9)
    
    def test_initial_state(self):
        """Тест: начальное состояние"""
        self.assertEqual(self.game.current_player, 'X')
        self.assertTrue(self.game.game_active)
        self.assertTrue(all(cell == '' for cell in self.game.board))
    
    def test_switch_player_logic(self):
        """Тест: логика смены игрока"""
        self.game.current_player = 'X'
        self.game.current_player = 'O' if self.game.current_player == 'X' else 'X'
        self.assertEqual(self.game.current_player, 'O')
        
        self.game.current_player = 'O' if self.game.current_player == 'X' else 'X'
        self.assertEqual(self.game.current_player, 'X')

def run_all_tests():
    """Запуск всех юнит-тестов"""
    print("=" * 70)
    print("ЗАПУСК ЮНИТ-ТЕСТОВ ДЛЯ ИГРЫ 'КРЕСТИКИ-НОЛИКИ'")
    print("=" * 70)
    
    # Создаем test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestTicTacToe)
    
    # Запускаем тесты
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("\n⚠️  ЕСТЬ ПРОБЛЕМЫ В ТЕСТАХ")
        for failure in result.failures:
            print(f"\n❌ Провален: {failure[0]}")
            print(f"   Ошибка: {failure[1]}")
    
    print("=" * 70)
    return result.wasSuccessful()

# ========== ГЛАВНЫЙ БЛОК ЗАПУСКА ==========

def main():
    """Главная функция запуска"""
    import sys
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # Запускаем тесты
            success = run_all_tests()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == 'help':
            print("\nИспользование:")
            print("  python main.py           - запустить игру")
            print("  python main.py test      - запустить юнит-тесты")
            print("  python main.py help      - показать эту справку")
            sys.exit(0)
    
    # Запускаем игру
    print("Запуск игры Крестики-нолики...")
    TicTacToeApp().run()

if __name__ == '__main__':
    main()
