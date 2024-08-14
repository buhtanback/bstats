import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QTreeWidget, QTreeWidgetItem, QLineEdit, QHBoxLayout, QSlider, QDoubleSpinBox, QCheckBox
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

        self.team_inputs = []
        self.bet_on_team_inputs = []  # Поля для команд, на які зроблена ставка
        self.event_inputs = []  # Поля для подій
        self.win_checkboxes = []
        self.lose_checkboxes = []
        for i in range(5):
            team_input = QLineEdit(self)
            team_input.setPlaceholderText(f"Team {i + 1}A vs Team {i + 1}B")
            self.team_inputs.append(team_input)
            self.layout.addWidget(team_input)

            bet_on_team_input = QLineEdit(self)
            bet_on_team_input.setPlaceholderText(f"Team you bet on for Match {i + 1}")
            self.bet_on_team_inputs.append(bet_on_team_input)
            self.layout.addWidget(bet_on_team_input)

            event_input = QLineEdit(self)
            event_input.setPlaceholderText(f"Event for Match {i + 1} (e.g., Total Goals, Handicap)")
            self.event_inputs.append(event_input)
            self.layout.addWidget(event_input)

            checkbox_layout = QHBoxLayout()

            win_checkbox = QCheckBox("Win", self)
            self.win_checkboxes.append(win_checkbox)
            checkbox_layout.addWidget(win_checkbox)

            lose_checkbox = QCheckBox("Lose", self)
            self.lose_checkboxes.append(lose_checkbox)
            checkbox_layout.addWidget(lose_checkbox)

            self.layout.addLayout(checkbox_layout)

        self.bet_amount_label = QLabel("Enter bet amount:", self)
        self.bet_amount_input = QLineEdit(self)
        self.bet_amount_input.setPlaceholderText("Enter bet amount")

        self.win_coefficient_label = QLabel("Select coefficient (1.00 to 10.00):", self)
        self.win_coefficient_slider = QSlider(Qt.Horizontal, self)
        self.win_coefficient_slider.setRange(100, 1000)  # Від 1.00 до 10.00
        self.win_coefficient_slider.setValue(100)
        self.win_coefficient_slider.setTickInterval(1)

        self.coefficient_display_label = QLabel("1.00", self)
        self.win_coefficient_slider.valueChanged.connect(self.update_coefficient_display)

        self.add_button = QPushButton('Add Bet', self)
        self.add_button.clicked.connect(self.add_bet)

        self.check_bet_button = QPushButton('Check Bet Outcome', self)
        self.check_bet_button.clicked.connect(self.check_bet_outcome)

        self.finish_button = QPushButton('Calculate Results', self)
        self.finish_button.clicked.connect(self.finish_betting)

        self.bets_tree = QTreeWidget(self)
        self.bets_tree.setColumnCount(3)
        self.bets_tree.setHeaderLabels(["Match", "Bet", "Result"])

        self.total_label = QLabel("Waiting for input...", self)

        self.withdraw_button = QPushButton('Withdraw Funds', self)  # Видалено зайвий рядок
        self.withdraw_input = QDoubleSpinBox(self)
        self.withdraw_input.setRange(0, self.get_current_balance())
        self.withdraw_input.setDecimals(2)
        self.withdraw_input.setSingleStep(10.0)

        self.layout.addWidget(self.deposit_label)
        self.layout.addWidget(self.balance_label)
        self.layout.addWidget(self.bet_amount_label)
        self.layout.addWidget(self.bet_amount_input)
        self.layout.addWidget(self.win_coefficient_label)
        self.layout.addWidget(self.win_coefficient_slider)
        self.layout.addWidget(self.coefficient_display_label)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.check_bet_button)
        self.layout.addWidget(self.finish_button)
        self.layout.addWidget(self.bets_tree)  # Заміна QListWidget на QTreeWidget
        self.layout.addWidget(self.total_label)

        withdraw_layout = QHBoxLayout()
        withdraw_layout.addWidget(self.withdraw_input)
        withdraw_layout.addWidget(self.withdraw_button)
        self.layout.addLayout(withdraw_layout)

        self.setLayout(self.layout)

    def update_coefficient_display(self):
        value = self.win_coefficient_slider.value() / 100.0
        self.coefficient_display_label.setText(f"{value:.2f}")

    def get_current_balance(self):
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

        win_coefficient = self.win_coefficient_slider.value() / 100.0 + 0.99  # Від 1.00 до 10.00

        self.total_bets += bet_amount
        win_amount = 0.0
        is_loss = False

        result_text = ""
        for team_input, bet_on_team_input, event_input, win_checkbox, lose_checkbox in zip(
                self.team_inputs, self.bet_on_team_inputs, self.event_inputs, self.win_checkboxes,
                self.lose_checkboxes):

            bet_on_team = bet_on_team_input.text().strip()
            event_text = event_input.text().strip()

            if lose_checkbox.isChecked():
                is_loss = True
                if bet_on_team:
                    result_text += f"Lost on: {bet_on_team}\n"
                if event_text:
                    result_text += f"Lost on event: {event_text}\n"
            elif win_checkbox.isChecked():
                win_amount += bet_amount * win_coefficient
                self.total_wins += bet_amount * win_coefficient
                if bet_on_team:
                    result_text += f"Won on: {bet_on_team}\n"
                if event_text:
                    result_text += f"Won on event: {event_text}\n"

        if is_loss or win_amount == 0.0:
            self.total_losses += bet_amount
            entry_result = 'Loss'
        else:
            entry_result = 'Win'

        bet_details = f"Bet: {bet_amount:.2f} UAH, Coefficient: {win_coefficient:.2f}"

        # Додавання до QTreeWidget
        parent_item = QTreeWidgetItem(self.bets_tree)
        parent_item.setText(0, bet_details)
        parent_item.setText(1, f"Win: {win_amount:.2f} UAH")
        parent_item.setText(2, f"{entry_result}\n{result_text.strip()}")  # Додаємо деталі в колонку Result

        # Додаємо матчі як піделементи
        for match in matches:
            match_item = QTreeWidgetItem(parent_item)
            match_item.setText(0, match)

        parent_item.setExpanded(True)  # Розгорнути запис для зручного перегляду

        # Збереження у файл з розривами рядків
        matches_file_str = '\n'.join(matches)
        self.save_bet_to_file(matches_file_str, bet_amount, win_coefficient, win_amount, entry_result)
        self.update_balance_labels()

        # Очищення полів після додавання ставки
        for input_field in self.team_inputs:
            input_field.clear()
        for bet_on_team_input in self.bet_on_team_inputs:
            bet_on_team_input.clear()
        for event_input in self.event_inputs:
            event_input.clear()
        for win_checkbox, lose_checkbox in zip(self.win_checkboxes, self.lose_checkboxes):
            win_checkbox.setChecked(False)
            lose_checkbox.setChecked(False)
        self.bet_amount_input.clear()
        self.win_coefficient_slider.setValue(100)
        self.coefficient_display_label.setText("1.00")

    def save_bet_to_file(self, matches_str, bet_amount, win_coefficient, win_amount, entry_result):
        with open('bet.txt', 'a') as file:
            file.write(f"{matches_str},{bet_amount:.2f},{win_coefficient:.2f},{win_amount:.2f},{entry_result}\n")

    def check_bet_outcome(self):
        all_wins = True
        any_losses = False
        for team_input, bet_on_team_input, event_input, win_checkbox, lose_checkbox in zip(self.team_inputs,
                                                                                           self.bet_on_team_inputs,
                                                                                           self.event_inputs,
                                                                                           self.win_checkboxes,
                                                                                           self.lose_checkboxes):
            team_text = team_input.text().strip()
            bet_on_team = bet_on_team_input.text().strip()
            event_text = event_input.text().strip()

            if not bet_on_team and not event_text:
                continue  # Якщо подія або команда, на яку зроблена ставка, не введені, пропустити

            # Перевірка результату матчу або події
            if bet_on_team in team_text or event_text:
                if win_checkbox.isChecked():
                    continue  # Якщо команда виграла або подія здійснилася, все добре
                elif lose_checkbox.isChecked():
                    all_wins = False
                    any_losses = True
            else:
                self.total_label.setText("Please ensure the team names or event details match the ones in the match.")
                return

        if any_losses:
            self.total_label.setText("Bet Unsuccessful. At least one match/event lost.")
        elif all_wins:
            self.total_label.setText("Bet Successful! All matches/events won.")
        else:
            self.total_label.setText("Bet Outcome Inconclusive. Not all matches/events won.")

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
                        match = ','.join(parts[:-4])  # Об'єднуємо все, що йде до останніх 4-х значень
                        bet_amount_str = parts[-4]
                        win_coefficient_str = parts[-3]
                        win_amount_str = parts[-2]
                        entry_result = parts[-1]
                        try:
                            bet_amount = float(bet_amount_str)
                            win_coefficient = float(win_coefficient_str)
                            win_amount = float(win_amount_str)
                        except ValueError:
                            continue  # Пропустити рядки з некоректними даними

                        parent_item = QTreeWidgetItem(self.bets_tree)
                        parent_item.setText(0, f"Bet: {bet_amount:.2f} UAH, Coefficient: {win_coefficient:.2f}")
                        parent_item.setText(1, f"Win: {win_amount:.2f} UAH")
                        parent_item.setText(2, f"Result: {entry_result}")

                        for match_line in match.split('\n'):
                            match_item = QTreeWidgetItem(parent_item)
                            match_item.setText(0, match_line)

                        parent_item.setExpanded(True)  # Розгорнути запис для зручного перегляду

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
