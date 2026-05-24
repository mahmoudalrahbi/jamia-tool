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

    # Row 4 in the sheet (index 3 in data = sheet row 4)
    # Columns: D=المبلغ المدفوع(idx 3), E=طريقة الدفع(idx 4), F=تاريخ الدفع(idx 5)
    payments_sheet.update_cell.assert_any_call(4, 4, 20)        # amount → col D
    payments_sheet.update_cell.assert_any_call(4, 5, "تحويل")   # type  → col E
    payments_sheet.update_cell.assert_any_call(4, 6, "21/05/2025")  # date → col F


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

    # DIST_HEADER = ["الشهر"(0), "المستفيد"(1), "تم الاستلام؟"(2), "المبلغ المستلم"(3), "طريقة التوزيع"(4), ...]
    dist_sheet.update_cell.assert_any_call(5, 2, "خالد")   # المستفيد  → col B
    dist_sheet.update_cell.assert_any_call(5, 4, 440)      # المبلغ    → col D
    dist_sheet.update_cell.assert_any_call(5, 5, "حجز")   # الطريقة  → col E


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
