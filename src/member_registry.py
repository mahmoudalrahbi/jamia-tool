from src.sheets_client import SheetsClient


class MemberRegistry:
    def __init__(self, client: SheetsClient):
        self._client = client
        self._members: list[dict] = []
        self.refresh()

    def refresh(self) -> None:
        self._members = self._client.get_members()

    def all(self) -> list[dict]:
        return self._members

    def get(self, name: str) -> dict | None:
        return next((m for m in self._members if m["name"] == name), None)

    def get_unpaid_months(self, member_name: str) -> list[str]:
        return self._client.get_unpaid_months(member_name)

    def get_paid_months(self, member_name: str) -> list[str]:
        return self._client.get_paid_months(member_name)

    def get_balance(self, member_name: str) -> int:
        return self._client.get_balance(member_name)

    def get_payment(self, member_name: str, month: str) -> dict:
        return self._client.get_payment(member_name, month)

    def get_next_distribution(self) -> dict:
        return self._client.get_next_distribution()

    def get_distributed_months(self) -> list[dict]:
        return self._client.get_distributed_months()

    def write_payment(self, member: str, month: str, date: str,
                      amount: int, transfer_type: str = "تحويل") -> None:
        self._client.write_payment(member=member, month=month, date=date,
                                   amount=amount, transfer_type=transfer_type)

    def write_distribution(self, row: int, member: str, amount: int, method: str = "") -> None:
        self._client.write_distribution(row=row, member=member, amount=amount, method=method)
