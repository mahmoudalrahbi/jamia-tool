import pytest
from datetime import date
from unittest.mock import AsyncMock
from src.flows.components import ManualDateModal


@pytest.mark.asyncio
async def test_manual_date_modal_defaults_to_today():
    modal = ManualDateModal(on_date=AsyncMock())
    assert modal.date_input.default == date.today().strftime("%d/%m/%Y")
