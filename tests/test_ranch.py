import pytest

from scrape_gpt.app import main, RanchProfile

@pytest.mark.asyncio
class TestRanch:
    async def test_default(self):
        prompt = "navigate https://shorthorn.digitalbeef.com/ do Ranch search with herd prefix 'prnl' member id '01-00927' name 'james' city 'stantons'"
        results = await main(prompt)
        expected = RanchProfile(
            member="01-00927",
            member_name="JAMES PARNELL",
            city="STANTON",
            state_or_province="AL",
            prefix="PRNL",
            dba="",
            type="AA",
        )
        assert results == [expected]

    async def test_location(self):
        prompt = "navigate https://shorthorn.digitalbeef.com/ do Ranch search with state of alabama"
        results = await main(prompt)
        assert len(results) == 16