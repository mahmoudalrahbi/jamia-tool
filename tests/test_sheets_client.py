from unittest.mock import MagicMock, patch
import pytest
from src.sheets_client import SheetsClient


def make_mock_spreadsheet(members_rows=None, payments_rows=None, dist_rows=None):
    """Build a mock gspread spreadsheet with configurable sheet data."""
    spreadsheet = MagicMock()

    members_sheet = MagicMock()
    members_sheet.get_all_values.return_value = members_rows or []

    payments_sheet = MagicMock()
    payments_sheet.get_all_values.return_value = payments_rows or []

    dist_sheet = MagicMock()
    dist_sheet.get_all_values.return_value = dist_rows or []

    def worksheet_side_effect(name):
        return {
            "الأعضاء": members_sheet,
            "الدفعات الشهرية": payments_sheet,
            "التوزيع": dist_sheet,
        }[name]

    spreadsheet.worksheet.side_effect = worksheet_side_effect
    return spreadsheet, members_sheet, payments_sheet, dist_sheet


MEMBERS_HEADER = ["الاسم", "عدد الأسهم", "قيمة الدفع الشهري", "مجموع ما دفعه",
                  "عدد الدفعات", "الحالة", "مجموع ما استلمه", "إجمالي ملزم بدفعه",
                  "المتبقي", "الدين (المستلم)"]

MEMBERS_DATA = [
    MEMBERS_HEADER,
    ["محمود", "1", "20", "280", "14", "نشط", "440", "440", "0", ""],
    ["خالد",  "2", "40", "560", "28", "نشط", "440", "880", "0", ""],
    ["الاجمالي", "11", "220", "3060", "153", "", "2620", "4840", "", ""],
]

PAYMENTS_HEADER = ["العضو", "الشهر", "عدد الأسهم", "المبلغ المدفوع",
                   "طريقة الدفع", "تاريخ الدفع", "حالة الدفع", "ملاحظه", "", "id"]

PAYMENTS_DATA = [
    PAYMENTS_HEADER,
    ["محمود", "04/2025", "1", "20", "تحويل", "23/04/2025", "مدفوع", "", "", "2"],
    ["خالد",  "04/2025", "2", "40", "تحويل", "23/04/2025", "مدفوع", "", "", "3"],
    ["محمود", "05/2025", "1", "",  "",        "",            "متأخر", "", "", "11"],
    ["خالد",  "05/2025", "2", "",  "",        "",            "متأخر", "", "", "12"],
]

DIST_HEADER = ["الشهر", "المستفيد", "تم الاستلام؟", "المبلغ المستلم", "طريقة التوزيع", "ملاحظات"]

DIST_DATA = [
    DIST_HEADER,
    ["05/2025", "محمود", "TRUE", "440", "حجز", ""],
    ["07/2025", "خالد",  "TRUE", "440", "حجز", ""],
    ["09/2026", "أمي",   "",     "",    "حجز", ""],
    ["11/2026", "",      "",     "",    "",     ""],
    ["01/2027", "",      "",     "",    "",     ""],
]


def test_col_label_returns_single_letter_for_low_indices():
    assert SheetsClient._col_label(0) == "A"
    assert SheetsClient._col_label(25) == "Z"


def test_col_label_returns_double_letter_for_index_26():
    assert SheetsClient._col_label(26) == "AA"


@patch("src.sheets_client.gspread")
@patch("src.sheets_client.Credentials")
def test_get_members_returns_all_active_members(mock_creds, mock_gspread):
    spreadsheet, _, _, _ = make_mock_spreadsheet(members_rows=MEMBERS_DATA)
    mock_gspread.authorize.return_value.open_by_key.return_value = spreadsheet

    client = SheetsClient(sheet_id="fake-id", credentials_path="fake.json")
    members = client.get_members()

    assert len(members) == 2
    assert members[0]["name"] == "محمود"
    assert members[0]["shares"] == 1
    assert members[0]["monthly_amount"] == 20
    assert members[1]["name"] == "خالد"
    assert members[1]["shares"] == 2
    assert members[1]["monthly_amount"] == 40


@patch("src.sheets_client.gspread")
@patch("src.sheets_client.Credentials")
def test_get_members_excludes_totals_row(mock_creds, mock_gspread):
    spreadsheet, _, _, _ = make_mock_spreadsheet(members_rows=MEMBERS_DATA)
    mock_gspread.authorize.return_value.open_by_key.return_value = spreadsheet

    client = SheetsClient(sheet_id="fake-id", credentials_path="fake.json")
    members = client.get_members()

    names = [m["name"] for m in members]
    assert "الاجمالي" not in names


@patch("src.sheets_client.gspread")
@patch("src.sheets_client.Credentials")
def test_write_payment_fills_correct_row(mock_creds, mock_gspread):
    spreadsheet, _, payments_sheet, _ = make_mock_spreadsheet(
        members_rows=MEMBERS_DATA,
        payments_rows=PAYMENTS_DATA,
    )
    mock_gspread.authorize.return_value.open_by_key.return_value = spreadsheet

    client = SheetsClient(sheet_id="fake-id", credentials_path="fake.json")
    client.write_payment(member="محمود", month="05/2025", date="21/05/2025",
                         amount=20, transfer_type="تحويل")

    # محمود 05/2025 is sheet row 4; amount=D, type=E, date=F — three independent cells
    payments_sheet.batch_update.assert_called_once_with([
        {"range": "D4", "values": [[20]]},
        {"range": "E4", "values": [["تحويل"]]},
        {"range": "F4", "values": [["21/05/2025"]]},
    ])


@patch("src.sheets_client.gspread")
@patch("src.sheets_client.Credentials")
def test_get_unpaid_months_returns_only_empty_amount_rows(mock_creds, mock_gspread):
    spreadsheet, _, _, _ = make_mock_spreadsheet(
        members_rows=MEMBERS_DATA,
        payments_rows=PAYMENTS_DATA,
    )
    mock_gspread.authorize.return_value.open_by_key.return_value = spreadsheet

    client = SheetsClient(sheet_id="fake-id", credentials_path="fake.json")
    months = client.get_unpaid_months("محمود")

    assert months == ["05/2025"]


@patch("src.sheets_client.gspread")
@patch("src.sheets_client.Credentials")
def test_get_distributed_months_returns_rows_with_member(mock_creds, mock_gspread):
    spreadsheet, _, _, _ = make_mock_spreadsheet(
        members_rows=MEMBERS_DATA,
        dist_rows=DIST_DATA,
    )
    mock_gspread.authorize.return_value.open_by_key.return_value = spreadsheet

    client = SheetsClient(sheet_id="fake-id", credentials_path="fake.json")
    results = client.get_distributed_months()

    assert len(results) == 3  # 05/2025, 07/2025, 09/2026 (أمي has member but no amount)
    assert results[0] == {"month": "05/2025", "row": 2, "member": "محمود", "amount": 440}
    assert results[1] == {"month": "07/2025", "row": 3, "member": "خالد",  "amount": 440}
    assert results[2]["member"] == "أمي"


@patch("src.sheets_client.gspread")
@patch("src.sheets_client.Credentials")
def test_write_distribution_fills_correct_cells(mock_creds, mock_gspread):
    spreadsheet, _, _, dist_sheet = make_mock_spreadsheet(
        members_rows=MEMBERS_DATA,
        dist_rows=DIST_DATA,
    )
    mock_gspread.authorize.return_value.open_by_key.return_value = spreadsheet

    client = SheetsClient(sheet_id="fake-id", credentials_path="fake.json")
    client.write_distribution(row=5, member="خالد", amount=440, method="حجز")

    # cols B (member), D (amount), E (method) — three independent single-cell entries
    dist_sheet.batch_update.assert_called_once_with([
        {"range": "B5", "values": [["خالد"]]},
        {"range": "D5", "values": [[440]]},
        {"range": "E5", "values": [["حجز"]]},
    ])


@patch("src.sheets_client.gspread")
@patch("src.sheets_client.Credentials")
def test_get_payment_returns_amount_and_date(mock_creds, mock_gspread):
    spreadsheet, _, _, _ = make_mock_spreadsheet(
        members_rows=MEMBERS_DATA,
        payments_rows=PAYMENTS_DATA,
    )
    mock_gspread.authorize.return_value.open_by_key.return_value = spreadsheet

    client = SheetsClient(sheet_id="fake-id", credentials_path="fake.json")
    payment = client.get_payment("محمود", "04/2025")

    assert payment["amount"] == 20
    assert payment["date"] == "23/04/2025"


@patch("src.sheets_client.gspread")
@patch("src.sheets_client.Credentials")
def test_get_paid_months_returns_only_months_with_amount(mock_creds, mock_gspread):
    spreadsheet, _, _, _ = make_mock_spreadsheet(
        members_rows=MEMBERS_DATA,
        payments_rows=PAYMENTS_DATA,
    )
    mock_gspread.authorize.return_value.open_by_key.return_value = spreadsheet

    client = SheetsClient(sheet_id="fake-id", credentials_path="fake.json")
    months = client.get_paid_months("محمود")

    assert months == ["04/2025"]


@patch("src.sheets_client.gspread")
@patch("src.sheets_client.Credentials")
def test_get_next_distribution_returns_first_row_with_empty_member(mock_creds, mock_gspread):
    spreadsheet, _, _, _ = make_mock_spreadsheet(
        members_rows=MEMBERS_DATA,
        dist_rows=DIST_DATA,
    )
    mock_gspread.authorize.return_value.open_by_key.return_value = spreadsheet

    client = SheetsClient(sheet_id="fake-id", credentials_path="fake.json")
    result = client.get_next_distribution()

    assert result["month"] == "11/2026"
    assert result["row"] == 5  # row 5 in sheet (1-indexed, header=1)


@patch("src.sheets_client.gspread")
@patch("src.sheets_client.Credentials")
def test_get_balance_returns_total_paid(mock_creds, mock_gspread):
    spreadsheet, _, _, _ = make_mock_spreadsheet(members_rows=MEMBERS_DATA)
    mock_gspread.authorize.return_value.open_by_key.return_value = spreadsheet

    client = SheetsClient(sheet_id="fake-id", credentials_path="fake.json")
    balance = client.get_balance("خالد")

    assert balance == 560
