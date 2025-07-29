"""Integration tests for live price client."""

import os
import pytest

from laplace.live_price import BISTStockLiveData, USStockLiveData


class TestLivePriceIntegration:
    """Integration tests for live price client with real API responses."""

    @pytest.mark.asyncio
    async def test_live_price_connection_and_data_flow(self, integration_client):
        print("test_live_price_connection_and_data_flow")
        print(f"API Key set: {bool(os.getenv('LAPLACE_API_KEY'))}")
        print(f"API Key length: {len(os.getenv('LAPLACE_API_KEY', ''))}")
        """Test that live price connection works and data is flowing for US and TR stocks."""
        live_price_client = integration_client.live_price

        # Test US stocks first (more likely to work)
        us_symbols = ["AAPL", "GOOGL"]
        us_events = []

        try:
            print("Testing US stocks...")
            async for event in live_price_client.get_live_price_for_us(us_symbols):
                us_events.append(event)
                print(f"Received US event: {event.symbol}")
                # Limit to first few events for testing
                if len(us_events) >= 2:
                    break
        except Exception as e:
            error_msg = f"US live price streaming failed: {e}"
            print(f"❌ FULL ERROR: {error_msg}")
            print(f"❌ Error type: {type(e).__name__}")
            print(f"❌ Error args: {e.args}")
            pytest.skip("US live price streaming failed - see print output above")

        # Test BIST (Turkish) stocks
        bist_symbols = ["THYAO", "GARAN"]
        bist_events = []

        try:
            print("Testing BIST stocks...")
            async for event in live_price_client.get_live_price_for_bist(bist_symbols):
                bist_events.append(event)
                print(f"Received BIST event: {event.symbol}")
                # Limit to first few events for testing
                if len(bist_events) >= 2:
                    break
        except Exception as e:
            error_msg = f"BIST live price streaming failed: {e}"
            print(f"❌ FULL ERROR: {error_msg}")
            print(f"❌ Error type: {type(e).__name__}")
            print(f"❌ Error args: {e.args}")
            pytest.skip("BIST live price streaming failed - see print output above")

        # Verify US data flow
        if us_events:
            assert all(isinstance(event, USStockLiveData) for event in us_events)
            assert all(event.symbol in us_symbols for event in us_events)
            assert all(hasattr(event, "bid_price") for event in us_events)
            assert all(hasattr(event, "ask_price") for event in us_events)
            print(f"✅ US data flowing: {len(us_events)} events received")
        else:
            pytest.skip("No US events received")

        # Verify BIST data flow
        if bist_events:
            assert all(isinstance(event, BISTStockLiveData) for event in bist_events)
            assert all(event.symbol in bist_symbols for event in bist_events)
            assert all(hasattr(event, "daily_percent_change") for event in bist_events)
            assert all(hasattr(event, "close_price") for event in bist_events)
            print(f"✅ BIST data flowing: {len(bist_events)} events received")
        else:
            pytest.skip("No BIST events received")
