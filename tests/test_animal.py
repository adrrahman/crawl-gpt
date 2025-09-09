import pytest

from scrape_gpt.app import main

@pytest.mark.asyncio
class TestAnimal:
    async def test_default(self):
        prompt = "navigate https://shorthorn.digitalbeef.com/ do Animal Search, search for bulls with search field 'A' on Tattoo"
        results = await main(prompt)
        assert len(results) == 4
        registrations = [result.registration for result in results]
        registrations.sort()
        assert registrations == ['CM23361', 'CM24994', 'CM25763', 'U4334492']

    async def test_start_with(self):
        prompt = "navigate https://shorthorn.digitalbeef.com/ do Animal Search, search for bulls with tattoo start with FSF23"
        results = await main(prompt)
        assert len(results) == 3
        assert results[0].registration == 'AR4298591'
        assert results[1].registration == 'AR4298592'
        assert results[2].registration == '4295218'
