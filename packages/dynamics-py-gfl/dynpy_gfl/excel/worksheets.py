from openpyxl.formatting import Rule
from openpyxl.styles import PatternFill
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.worksheet.worksheet import Worksheet


class WorksheetManager:
    def __init__(self, worksheet: Worksheet) -> None:
        self._worksheet = worksheet
        try:
            self._column_headers = list(worksheet.values)[0]
        except IndexError:
            self._column_headers = []

    def highlight_row_by_column_value(self, column_name: str, value: str, color_hex: str):
        ws = self._worksheet
        if column_name not in self._column_headers:
            return
        status_col_index = self._column_headers.index(column_name)

        fill = PatternFill(bgColor=f"00{color_hex}")
        dxf = DifferentialStyle(fill=fill)
        rule = Rule(type="expression", dxf=dxf)
        rule.formula = [f'${ws.cell(row=2, column=status_col_index + 1).coordinate}="{value}"']
        range_string = f"A2:{ws.cell(row=ws.max_row, column=ws.max_column).coordinate}"
        ws.conditional_formatting.add(range_string, rule)

    def highlight_one_cell(self, row: int, column: int, color_hex: str):
        ws = self._worksheet
        fill = PatternFill(start_color=color_hex, end_color=color_hex, fill_type="solid")
        ws.cell(row=row, column=column).fill = fill
