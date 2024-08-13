import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QListWidget, QLineEdit, QHBoxLayout, QSlider, QDoubleSpinBox
)
from PyQt5.QtCore import Qt

class BettingTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.total_deposited = 500.0  # Початковий депозит
        self.total_withdrawn = 0.0
        self.total_bets = 0.0
        self.total_wins = 0.0
        self.total_losses = 0.0
        self.initUI()
        self.load_bets()

    def initUI(self):
        self.setWindowTitle("Betting Tracker")
        self.layout = QVBoxLayout()

        self.deposit_label = QLabel(f"Initial deposit: {self.total_deposited:.2f} UAH")
        self.balance_label = QLabel(f"Current balance: {self.get_current_balance():.2f} UAH")

        # Поля для введення матчів
        self.team_inputs = []
        for i in range(5):
            team_input = QLineEdit(self)
            team_input.setPlaceholderText(f"Team {i+1}A vs Team {i+1}B")
            self.team_inputs.append(team_input)
            self.layout.addWidget(team_input)

        # Поле для введення суми ставки
        self.bet_amount_label = QLabel("Enter bet amount:", self)
        self.bet_amount_input = QLineEdit(self)
        self.bet_amount_input.setPlaceholderText("Enter bet amount")

        # Слайдер для вибору коефіцієнта
        self.win_coefficient_label = QLabel("Select coefficient (0.00 to 10.00):", self)
        self.win_coefficient_slider = QSlider(Qt.Horizontal, self)
        self.win_coefficient_slider.setRange(0, 900)  # Від 0 до 900 (0 = 0.00, 1 = 1.00, ..., 900 = 10.00)
        self.win_coefficient_slider.setValue(0)  # Початкове значення = 0 (програш)
        self.win_coefficient_slider.setTickInterval(1)

        # Мітка для відображення поточного значення слайдера
        self.coefficient_display_label = QLabel("0.00", self)
        self.win_coefficient_slider.valueChanged.connect(self.update_coefficient_display)

        # Кнопка для додавання ставки
        self.add_button = QPushButton('Add Bet', self)
        self.add_button.clicked.connect(self.add_bet)

        # Кнопка для розрахунку результатів
        self.finish_button = QPushButton('Calculate Results', self)
        self.finish_button.clicked.connect(self.finish_betting)

        # Список для відображення ставок
        self.bets_list = QListWidget(self)

        # Мітка для відображення загальної інформації
        self.total_label = QLabel("Waiting for input...", self)

        # Поле та кнопка для зняття коштів
        self.withdraw_button = QPushButton('Withdraw Funds', self)
        self.withdraw_button.clicked.connect(self.withdraw_funds)
        self.withdraw_input = QDoubleSpinBox(self)
        self.withdraw_input.setRange(0, self.get_current_balance())
        self.withdraw_input.setDecimals(2)
        self.withdraw_input.setSingleStep(10.0)

        # Додавання віджетів до макету
        self.layout.addWidget(self.deposit_label)
        self.layout.addWidget(self.balance_label)
        self.layout.addWidget(self.bet_amount_label)
        self.layout.addWidget(self.bet_amount_input)
        self.layout.addWidget(self.win_coefficient_label)
        self.layout.addWidget(self.win_coefficient_slider)
        self.layout.addWidget(self.coefficient_display_label)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.finish_button)
        self.layout.addWidget(self.bets_list)
        self.layout.addWidget(self.total_label)

        withdraw_layout = QHBoxLayout()
        withdraw_layout.addWidget(self.withdraw_input)
        withdraw_layout.addWidget(self.withdraw_button)
        self.layout.addLayout(withdraw_layout)

        self.setLayout(self.layout)

    def update_coefficient_display(self):
        value = self.win_coefficient_slider.value()
        if value == 0:
            coefficient = 0.00  # Програш
        else:
            coefficient = value / 100.0 + 0.99  # Від 1.00 до 10.00
        self.coefficient_display_label.setText(f"{coefficient:.2f}")

    def get_current_balance(self):
        # Поточний баланс = Початковий депозит + Виграші - Програші - Зняті кошти
        return self.total_deposited + self.total_wins - self.total_losses - self.total_withdrawn

    def add_bet(self):
        matches = [input.text() for input in self.team_inputs if input.text().strip()]
        if not matches:
            self.total_label.setText("Please enter at least one match.")
            return

        bet_amount_text = self.bet_amount_input.text().strip()
        if not bet_amount_text:
            self.total_label.setText("Please enter bet amount.")
            return

        try:
            bet_amount = float(bet_amount_text)
            if bet_amount <= 0:
                self.total_label.setText("Bet amount must be positive.")
                return
        except ValueError:
            self.total_label.setText("Invalid bet amount.")
            return

        current_balance = self.get_current_balance()
        if bet_amount > current_balance:
            self.total_label.setText(f"Insufficient balance. Available: {current_balance:.2f} UAH")
            return

        value = self.win_coefficient_slider.value()
        if value == 0:
            win_coefficient = 0.00  # Програш
        else:
            win_coefficient = value / 100.0 + 0.99  # Від 1.00 до 10.00

        self.total_bets += bet_amount
        if win_coefficient == 0.00:
            self.total_losses += bet_amount
            entry_result = 'Loss'
            win_amount = 0.0
        else:
            win_amount = bet_amount * win_coefficient
            self.total_wins += win_amount
            entry_result = 'Win'

        matches_str = ', '.join(matches)
        entry = (
            f"Matches: {matches_str}, Bet: {bet_amount:.2f} UAH, "
            f"Coefficient: {win_coefficient:.2f}, Win: {win_amount:.2f} UAH, Result: {entry_result}"
        )
        self.bets_list.addItem(entry)
        self.update_balance_labels()

        # Очистка полів після додавання ставки
        for input_field in self.team_inputs:
            input_field.clear()
        self.bet_amount_input.clear()
        self.win_coefficient_slider.setValue(0)
        self.coefficient_display_label.setText("0.00")

    def update_balance_labels(self):
        current_balance = self.get_current_balance()
        self.balance_label.setText(f"Current balance: {current_balance:.2f} UAH")
        self.withdraw_input.setMaximum(current_balance)

    def withdraw_funds(self):
        amount = self.withdraw_input.value()
        current_balance = self.get_current_balance()
        if amount <= current_balance:
            self.total_withdrawn += amount
            self.update_balance_labels()
            self.total_label.setText(f"Withdrew {amount:.2f} UAH.")
            self.withdraw_input.setValue(0.0)
        else:
            self.total_label.setText("Insufficient balance to withdraw.")

    def finish_betting(self):
        net_profit = self.total_wins - self.total_losses
        total_info = (
            f"Total bets: {self.total_bets:.2f} UAH\n"
            f"Total wins: {self.total_wins:.2f} UAH\n"
            f"Total losses: {self.total_losses:.2f} UAH\n"
            f"Net profit (or loss): {net_profit:.2f} UAH\n"
            f"Total withdrawn: {self.total_withdrawn:.2f} UAH\n"
            f"Current balance: {self.get_current_balance():.2f} UAH"
        )
        self.total_label.setText(total_info)

    def load_bets(self):
        try:
            with open('bet.txt', 'r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 5:
                        match, bet_amount_str, win_coefficient_str, win_amount_str, entry_result = parts
                        try:
                            bet_amount = float(bet_amount_str)
                            win_coefficient = float(win_coefficient_str)
                            win_amount = float(win_amount_str)
                        except ValueError:
                            continue  # Пропустити рядки з некоректними даними
                        self.bets_list.addItem(
                            f"Match: {match}, Bet: {bet_amount:.2f} UAH, "
                            f"Coefficient: {win_coefficient:.2f}, Win: {win_amount:.2f} UAH, Result: {entry_result}"
                        )
                        self.total_bets += bet_amount
                        if entry_result.strip().lower() == 'loss':
                            self.total_losses += bet_amount
                        elif entry_result.strip().lower() == 'win':
                            self.total_wins += win_amount
                self.update_balance_labels()
        except FileNotFoundError:
            pass  # Якщо файл не знайдено, починаємо з чистого листа

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BettingTracker()
    ex.show()
    sys.exit(app.exec_())
