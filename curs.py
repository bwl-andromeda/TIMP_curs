from PyQt5.QtWidgets import *
from datetime import datetime
import csv


class HeatingPaymentRecord:
    def __init__(self, id, date, amount, note, fio):
        self.id = id
        self.set_date(date)
        self.amount = amount
        self.note = note
        self.fio = fio

    def set_date(self, date):
        try:
            datetime.strptime(date, "%Y-%m-%d")
            self.date = date
        except ValueError:
            raise ValueError(
                "Ошибка: Неверный формат даты. Используйте формат YYYY-MM-DD."
            )

    def display(self):
        return f"ID: {self.id} ФИО: {self.fio} Дата: {self.date} Сумма: {self.amount} Описание: {self.note}"

    def contains_search_term(self, search_term):
        lower_search_term = search_term.lower()
        lower_data = f"{self.date} {self.id} {self.note} {self.fio}".lower()
        return lower_data.find(lower_search_term) != -1

    def __lt__(self, other):
        return self.date < other.date

    def __eq__(self, other):
        return self.id == other.id


class HeatingPaymentSystem:
    def __init__(self):
        self.records = []

    def add_record(self, record):
        if self.find_record_by_id(record.id) is not None:
            raise ValueError("Ошибка: запись с таким идентификатором уже существует.")

        if record.amount <= 0:
            raise ValueError("Ошибка: Сумма должна быть больше 0.")

        self.records.append(record)

    def find_record_by_id(self, id):
        for record in self.records:
            if record.id == id:
                return record
        return None

    def find_records_by_search_term(self, search_term):
        result = []
        for record in self.records:
            if record.contains_search_term(search_term):
                result.append(record)
        return result

    def sort_by_field(self, field):
        if not self.records:
            raise ValueError("Ошибка: Нет записей для сортировки.")
        if field not in vars(self.records[0]):
            raise ValueError(f"Ошибка: Поле {field} не существует.")
        self.records.sort(key=lambda x: getattr(x, field))

    def delete_record_by_id(self, id):
        for record in self.records:
            if record.id == id:
                self.records.remove(record)
                return True
        return False

    def edit_record(self, id, new_date, new_amount, new_note, new_fio):
        record = self.find_record_by_id(id)
        if record is not None:
            record.set_date(new_date)
            record.amount = new_amount
            record.note = new_note
            record.fio = new_fio
            return True
        return False

    def display_all_records(self):
        return [record.display() for record in self.records]

    def save_to_file(self, filename):
        with open(filename, "w", newline="",encoding="UTF-8") as file:
            writer = csv.writer(file, delimiter=";")
            for record in self.records:
                writer.writerow(
                    [record.id, record.date, record.amount, record.note, record.fio]
                )

    def load_from_file(self, filename):
        self.records.clear()
        try:
            with open(filename, "r", encoding="UTF-8") as file:
                reader = csv.reader(file, delimiter=";")
                for row in reader:
                    id, date, amount, note, fio = row
                    record = HeatingPaymentRecord(
                        int(id), date, float(amount), note, str(fio)
                    )
                    self.add_record(record)
            return True
        except FileNotFoundError:
            return False


class AddRecordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Добавить запись")
        layout = QFormLayout(self)

        self.id_input = QLineEdit(self)
        self.date_input = QLineEdit(self)
        self.amount_input = QLineEdit(self)
        self.note_input = QLineEdit(self)
        self.fio_input = QLineEdit(self)

        layout.addRow("ID:", self.id_input)
        layout.addRow("Дата (YYYY-MM-DD):", self.date_input)
        layout.addRow("Сумма:", self.amount_input)
        layout.addRow("Описание:", self.note_input)
        layout.addRow("ФИО:", self.fio_input)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        return {
            "id": int(self.id_input.text()),
            "date": self.date_input.text(),
            "amount": float(self.amount_input.text()),
            "note": self.note_input.text(),
            "fio": self.fio_input.text(),
        }


class ActionDialog(QDialog):
    def __init__(self, action_text, input_prompt, action_function, parent=None):
        super().__init__(parent)

        self.setWindowTitle(action_text)
        layout = QVBoxLayout(self)

        self.input_label = QLabel(input_prompt, self)
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Введите значение")

        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)

        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.result_text)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        button_box.accepted.connect(lambda: self.run_action(action_function))
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def run_action(self, action_function):
        try:
            input_value = self.input_field.text()
            result = action_function(input_value)
            self.result_text.setPlainText(result)
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))


class SortDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Выберите поле для сортировки")
        layout = QVBoxLayout(self)

        self.sort_options = ["ID", "Дата", "Сумма", "Описание", "ФИО"]
        self.sort_combobox = QComboBox(self)
        self.sort_combobox.addItems(self.sort_options)

        layout.addWidget(self.sort_combobox)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_sort_field(self):
        return self.sort_combobox.currentText()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.payment_system = HeatingPaymentSystem()

        self.central_widget = QWidget(self)
        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel("Выберите действие:", self)
        self.layout.addWidget(self.label)

        self.button_add = QPushButton("Добавить запись", self)
        self.button_add.clicked.connect(self.show_add_record_dialog)
        self.layout.addWidget(self.button_add)

        self.button_search = QPushButton("Поиск записей", self)
        self.button_search.clicked.connect(self.show_search_dialog)
        self.layout.addWidget(self.button_search)

        self.button_sort = QPushButton("Сортировка записей", self)
        self.button_sort.clicked.connect(self.show_sort_dialog)
        self.layout.addWidget(self.button_sort)

        self.button_delete = QPushButton("Удалить запись по ID", self)
        self.button_delete.clicked.connect(self.show_delete_dialog)
        self.layout.addWidget(self.button_delete)

        self.button_edit = QPushButton("Редактировать запись по ID", self)
        self.button_edit.clicked.connect(self.show_edit_dialog)
        self.layout.addWidget(self.button_edit)

        self.button_save = QPushButton("Сохранение записей в файл", self)
        self.button_save.clicked.connect(self.show_save_dialog)
        self.layout.addWidget(self.button_save)

        self.button_load = QPushButton("Загрузить записи из файла", self)
        self.button_load.clicked.connect(self.show_load_dialog)
        self.layout.addWidget(self.button_load)

        self.table_widget = QTableWidget(self)
        self.layout.addWidget(self.table_widget)

        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(
            ["ID", "Дата", "Сумма", "Описание", "ФИО"]
        )
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.setCentralWidget(self.central_widget)

    def update_table(self):
        self.table_widget.setRowCount(0)
        for row, record in enumerate(self.payment_system.records):
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(record.id)))
            self.table_widget.setItem(row, 1, QTableWidgetItem(record.date))
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(record.amount)))
            self.table_widget.setItem(row, 3, QTableWidgetItem(record.note))
            self.table_widget.setItem(row, 4, QTableWidgetItem(record.fio))

    def show_sort_dialog(self):
        dialog = SortDialog(self)
        if dialog.exec_():
            sort_field = dialog.get_selected_sort_field()
            field_mapping = {
                "ID": "id",
                "Дата": "date",
                "Сумма": "amount",
                "Описание": "note",
                "ФИО": "fio",
            }

            try:
                self.payment_system.sort_by_field(field_mapping[sort_field])
                self.update_table()
                QMessageBox.information(self, "Успех", "Записи отсортированы.")
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def show_save_dialog(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить файл", "", "CSV Files (*.csv)"
            )
            if filename:
                self.payment_system.save_to_file(filename)
                return f"Записи успешно сохранены в файле {filename}."
            else:
                return "Сохранение отменено."
        except Exception as e:
            return str(e)

    def show_load_dialog(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Загрузить файл", "", "CSV Files (*.csv)"
            )
            if filename:
                if self.payment_system.load_from_file(filename):
                    self.update_table()
                    return f"Записи успешно загружены из файла {filename}."
                else:
                    return "Файл пуст или имеет неверный формат."
            else:
                return "Загрузка отменена."
        except Exception as e:
            return str(e)

    def show_delete_dialog(self):
        def delete_record(id_to_delete):
            try:
                id_to_delete = int(id_to_delete)
                if self.payment_system.delete_record_by_id(id_to_delete):
                    self.update_table()
                    return f"Запись с ID {id_to_delete} успешно удалена."
                else:
                    return f"Запись с ID {id_to_delete} не найдена."
            except ValueError as e:
                return str(e)

        self.show_action_dialog(
            "Удаление записи",
            "Введите ID записи для удаления:",
            lambda id_to_delete: delete_record(id_to_delete)
            if id_to_delete
            else "ID не введен",
        )

    def show_add_record_dialog(self):
        dialog = AddRecordDialog(self)
        if dialog.exec_():
            try:
                data = dialog.get_data()
                record = HeatingPaymentRecord(
                    data["id"], data["date"], data["amount"], data["note"], data["fio"]
                )
                self.payment_system.add_record(record)
                self.update_table()
                QMessageBox.information(self, "Успех", "Запись успешно добавлена.")
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def show_search_dialog(self):
        self.show_action_dialog(
            "Поиск записей", "Введите поисковый запрос:", self.search_records
        )

    def show_display_dialog(self):
        records = self.payment_system.display_all_records()
        if records:
            QMessageBox.information(self, "Все записи", "\n".join(records))
        else:
            QMessageBox.information(self, "Все записи", "Записей не найдено.")

    def search_records(self, search_term):
        search_results = self.payment_system.find_records_by_search_term(search_term)
        if not search_results:
            return "Совпадающих записей не найдено."
        else:
            return "\n".join([record.display() for record in search_results])

    def show_action_dialog(self, action_text, input_prompt, action_function):
        dialog = ActionDialog(action_text, input_prompt, action_function, self)
        dialog.exec_()

    def show_edit_dialog(self):
        def edit_record(id_to_edit):
            try:
                id_to_edit = int(id_to_edit)
                record = self.payment_system.find_record_by_id(id_to_edit)
                if record:
                    dialog = EditRecordDialog(record, self)
                    if dialog.exec_():
                        new_data = dialog.get_data()
                        record.set_date(new_data["date"])
                        record.amount = new_data["amount"]
                        record.note = new_data["note"]
                        record.fio = new_data["fio"]
                        self.update_table()
                        return f"Запись с ID {id_to_edit} успешно отредактирована."
                    else:
                        return "Редактирование отменено."
                else:
                    return f"Запись с ID {id_to_edit} не найдена."
            except ValueError as e:
                return str(e)

        self.show_action_dialog(
            "Редактирование записи",
            "Введите ID записи для редактирования:",
            lambda id_to_edit: edit_record(id_to_edit)
            if id_to_edit
            else "ID не введен",
        )


class EditRecordDialog(QDialog):
    def __init__(self, record, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Редактировать запись")
        layout = QFormLayout(self)

        self.date_input = QLineEdit(self)
        self.amount_input = QLineEdit(self)
        self.note_input = QLineEdit(self)
        self.fio_input = QLineEdit(self)

        self.date_input.setText(record.date)
        self.amount_input.setText(str(record.amount))
        self.note_input.setText(record.note)
        self.fio_input.setText(record.fio)

        layout.addRow("Дата (YYYY-MM-DD):", self.date_input)
        layout.addRow("Сумма:", self.amount_input)
        layout.addRow("Описание:", self.note_input)
        layout.addRow("ФИО:", self.fio_input)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        return {
            "date": self.date_input.text(),
            "amount": float(self.amount_input.text()),
            "note": self.note_input.text(),
            "fio": self.fio_input.text(),
        }


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
