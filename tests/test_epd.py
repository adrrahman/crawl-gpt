import pytest

from scrape_gpt.app import main

@pytest.mark.asyncio
class TestEpd:
    async def test_default(self):
        prompt = "navigate https://shorthorn.digitalbeef.com/ do EPD search with CE direct min,max 0,0 birth weight min 5 max 6 weaning weight min 60 max 79 sort by milk"
        results = await main(prompt)
        assert len(results) == 2
        assert results[0].registration == '4230422'
        assert results[1].registration == 'AR4259808'

    async def test_multiple_fields(self):
        prompt = "navigate https://shorthorn.digitalbeef.com/ do EPD search, fill max value of ce direct until yearling weight with 3"
        results = await main(prompt)
        assert len(results) == 1
        assert results[0].registration == '3803875'
        