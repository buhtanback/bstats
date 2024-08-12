import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QLineEdit, QComboBox)
from PyQt5.QtCore import Qt

class BettingTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_bets()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.bet_amount_label = QLabel("Введіть суму ставки:", self)
        self.bet_amount_input = QLineEdit(self)  # Поле для введення суми ставки
        self.bet_amount_input.setPlaceholderText("Введіть суму ставки")

        self.win_coefficient_label = QLabel("Виберіть коефіцієнт:", self)
        self.win_coefficient_combobox = QComboBox(self)
        self.win_coefficient_combobox.addItem("0.00")  # Опція для програшної ставки
        coefficient_values = [f"{i/100:.2f}" for i in range(100, 1001, 1)]  # 1.00 до 10.00 з кроком 0.01
        self.win_coefficient_combobox.addItems(coefficient_values)

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
        self.layout.addWidget(self.win_coefficient_label)
        self.layout.addWidget(self.win_coefficient_combobox)
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
        bet_amount = float(self.bet_amount_input.text()) if self.bet_amount_input.text() else 0
        win_coefficient = float(self.win_coefficient_combobox.currentText())

        self.total_bets += bet_amount
        if win_coefficient == 0:
            self.total_losses += bet_amount
            entry_result = 'Програш'
            win_amount = 0
        else:
            win_amount = bet_amount * win_coefficient
            self.total_wins += win_amount
            entry_result = 'Виграш'

        entry = f"{bet_amount},{win_coefficient},{win_amount},{entry_result}"
        self.bets_list.addItem(f"Ставка: {bet_amount}, Коефіцієнт: {win_coefficient}, Виграш: {win_amount}, Результат: {entry_result}")

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
        with open('bet.txt', 'a') as file:
            file.write(entry + "\n")

    def load_bets(self):
        try:
            with open('bet.txt', 'r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) == 4:
                        bet_amount, win_coefficient, win_amount, entry_result = parts
                        self.bets_list.addItem(f"Ставка: {bet_amount}, Коефіцієнт: {win_coefficient}, Виграш: {win_amount}, Результат: {entry_result}")
                        bet_amount = float(bet_amount)
                        win_amount = float(win_amount)
                        self.total_bets += bet_amount
                        if win_coefficient == '0':
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
