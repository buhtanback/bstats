import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget

class BettingTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_bets()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.bet_amount_label = QLabel("Введіть суму ставки:", self)
        self.bet_amount_input = QLineEdit(self)

        self.win_amount_label = QLabel("Введіть суму виграшу (0 якщо програш):", self)
        self.win_amount_input = QLineEdit(self)

        self.add_button = QPushButton('Додати ставку', self)
        self.add_button.clicked.connect(self.add_bet)

        self.finish_button = QPushButton('Розрахувати', self)
        self.finish_button.clicked.connect(self.finish_betting)

        self.close_button = QPushButton('Закрити програму', self)
        self.close_button.clicked.connect(self.close)

        self.bets_list = QListWidget(self)

        self.total_label = QLabel("Чекаю вводу даних...", self)

        self.layout.addWidget(self.bet_amount_label)
        self.layout.addWidget(self.bet_amount_input)
        self.layout.addWidget(self.win_amount_label)
        self.layout.addWidget(self.win_amount_input)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.finish_button)
        self.layout.addWidget(self.bets_list)
        self.layout.addWidget(self.total_label)
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)

        self.total_bets = 0
        self.total_wins = 0
        self.total_losses = 0

    def add_bet(self):
        bet_amount = float(self.bet_amount_input.text())
        win_amount = float(self.win_amount_input.text())

        self.total_bets += bet_amount
        if win_amount == 0:
            self.total_losses += bet_amount
            entry_result = 'Програш'
        else:
            self.total_wins += win_amount
            entry_result = 'Виграш'

        entry = f"{bet_amount},{win_amount},{entry_result}"
        self.bets_list.addItem(f"Ставка: {bet_amount}, Результат: {entry_result}, Сума: {win_amount}")

        self.bet_amount_input.clear()
        self.win_amount_input.clear()

        # Запис даних до файлу
        self.save_bet(entry)

    def finish_betting(self):
        total_info = (
            f"Загальна сума ставок: {self.total_bets}\n"
            f"Загальні виграші: {self.total_wins}\n"
            f"Загальні збитки: {self.total_losses}\n"
            f"Чистий прибуток (або збиток): {self.total_wins - self.total_losses}"
        )
        self.total_label.setText(total_info)

    def save_bet(self, entry):
        with open('b.txt', 'a') as file:
            file.write(entry + "\n")

    def load_bets(self):
        try:
            with open('b.txt', 'r') as file:
                for line in file:
                    bet_amount, win_amount, entry_result = line.strip().split(',')
                    self.bets_list.addItem(f"Ставка: {bet_amount}, Результат: {entry_result}, Сума: {win_amount}")
                    bet_amount = float(bet_amount)
                    win_amount = float(win_amount)
                    self.total_bets += bet_amount
                    if win_amount == 0:
                        self.total_losses += bet_amount
                    else:
                        self.total_wins += win_amount
        except FileNotFoundError:
            pass  # Якщо файл не знайдено, починаємо з чистого аркуша

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BettingTracker()
    ex.show()
    sys.exit(app.exec_())
