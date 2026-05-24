import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SHEET_MEMBERS = "الأعضاء"
SHEET_PAYMENTS = "الدفعات الشهرية"
SHEET_DISTRIBUTIONS = "التوزيع"

COL_NAME = "الاسم"
COL_SHARES = "عدد الأسهم"
COL_MONTHLY = "قيمة الدفع الشهري"
COL_TOTAL_PAID = "مجموع ما دفعه"
TOTALS_ROW_NAME = "الاجمالي"

PAY_COL_MEMBER = "العضو"
PAY_COL_MONTH = "الشهر"
PAY_COL_AMOUNT = "المبلغ المدفوع"
PAY_COL_TYPE = "طريقة الدفع"
PAY_COL_DATE = "تاريخ الدفع"

DIST_COL_MONTH = "الشهر"
DIST_COL_MEMBER = "المستفيد"
DIST_COL_AMOUNT = "المبلغ المستلم"
DIST_COL_METHOD = "طريقة التوزيع"


class SheetsClient:
    def __init__(self, sheet_id: str, credentials_path: str):
        creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        self._gc = gspread.authorize(creds)
        self._sheet = self._gc.open_by_key(sheet_id)

    def _worksheet(self, name: str):
        return self._sheet.worksheet(name)

    def _header_map(self, rows: list) -> dict:
        return {col: idx for idx, col in enumerate(rows[0])}

    def get_members(self) -> list[dict]:
        ws = self._worksheet(SHEET_MEMBERS)
        rows = ws.get_all_values()
        headers = self._header_map(rows)

        members = []
        for row in rows[1:]:
            name = row[headers[COL_NAME]]
            if not name or name == TOTALS_ROW_NAME:
                continue
            members.append({
                "name": name,
                "shares": int(row[headers[COL_SHARES]]),
                "monthly_amount": int(row[headers[COL_MONTHLY]]),
            })
        return members

    def write_payment(self, member: str, month: str, date: str,
                      amount: int, transfer_type: str = "تحويل") -> None:
        ws = self._worksheet(SHEET_PAYMENTS)
        rows = ws.get_all_values()
        h = self._header_map(rows)

        for i, row in enumerate(rows[1:], start=2):
            if row[h[PAY_COL_MEMBER]] == member and row[h[PAY_COL_MONTH]] == month:
                sheet_row = i
                ws.update_cell(sheet_row, h[PAY_COL_AMOUNT] + 1, amount)
                ws.update_cell(sheet_row, h[PAY_COL_TYPE] + 1, transfer_type)
                ws.update_cell(sheet_row, h[PAY_COL_DATE] + 1, date)
                return
        raise ValueError(f"لم يُعثر على صف للعضو '{member}' في الشهر '{month}'")

    def get_payment(self, member: str, month: str) -> dict:
        ws = self._worksheet(SHEET_PAYMENTS)
        rows = ws.get_all_values()
        h = self._header_map(rows)

        for row in rows[1:]:
            if row[h[PAY_COL_MEMBER]] == member and row[h[PAY_COL_MONTH]] == month:
                return {
                    "amount": int(row[h[PAY_COL_AMOUNT]]),
                    "date": row[h[PAY_COL_DATE]],
                }
        raise ValueError(f"لم يُعثر على دفعة للعضو '{member}' في '{month}'")

    def get_paid_months(self, member: str) -> list[str]:
        ws = self._worksheet(SHEET_PAYMENTS)
        rows = ws.get_all_values()
        h = self._header_map(rows)

        return [
            row[h[PAY_COL_MONTH]]
            for row in rows[1:]
            if row[h[PAY_COL_MEMBER]] == member and row[h[PAY_COL_AMOUNT]]
        ]

    def get_unpaid_months(self, member: str) -> list[str]:
        ws = self._worksheet(SHEET_PAYMENTS)
        rows = ws.get_all_values()
        h = self._header_map(rows)

        return [
            row[h[PAY_COL_MONTH]]
            for row in rows[1:]
            if row[h[PAY_COL_MEMBER]] == member and not row[h[PAY_COL_AMOUNT]]
        ]

    def get_distributed_months(self) -> list[dict]:
        ws = self._worksheet(SHEET_DISTRIBUTIONS)
        rows = ws.get_all_values()
        h = self._header_map(rows)

        results = []
        for i, row in enumerate(rows[1:], start=2):
            if row[h[DIST_COL_MEMBER]]:
                results.append({
                    "month": row[h[DIST_COL_MONTH]],
                    "row": i,
                    "member": row[h[DIST_COL_MEMBER]],
                    "amount": int(row[h[DIST_COL_AMOUNT]]) if row[h[DIST_COL_AMOUNT]] else 0,
                })
        return results

    def write_distribution(self, row: int, member: str, amount: int, method: str = "") -> None:
        ws = self._worksheet(SHEET_DISTRIBUTIONS)
        rows = ws.get_all_values()
        h = self._header_map(rows)

        ws.update_cell(row, h[DIST_COL_MEMBER] + 1, member)
        ws.update_cell(row, h[DIST_COL_AMOUNT] + 1, amount)
        ws.update_cell(row, h[DIST_COL_METHOD] + 1, method)

    def get_next_distribution(self) -> dict:
        ws = self._worksheet(SHEET_DISTRIBUTIONS)
        rows = ws.get_all_values()
        h = self._header_map(rows)

        for i, row in enumerate(rows[1:], start=2):
            if not row[h[DIST_COL_MEMBER]]:
                return {"month": row[h[DIST_COL_MONTH]], "row": i}
        raise ValueError("لا توجد شهور توزيع متاحة")

    def get_balance(self, member: str) -> int:
        ws = self._worksheet(SHEET_MEMBERS)
        rows = ws.get_all_values()
        h = self._header_map(rows)

        for row in rows[1:]:
            if row[h[COL_NAME]] == member:
                return int(row[h[COL_TOTAL_PAID]])
        raise ValueError(f"العضو '{member}' غير موجود")
