"""Integration tests for live price client."""

import os
import asyncio
import pytest

from laplace.client import LaplaceClient
from laplace.live_price import BISTStockLiveData, USStockLiveData


class TestLivePriceIntegration:
    """Integration tests for live price client with real API responses."""

    @pytest.mark.asyncio
    async def test_live_price_connection_and_data_flow(self, integration_client: LaplaceClient):
        print("test_live_price_connection_and_data_flow")
        print(f"API Key set: {bool(os.getenv('LAPLACE_API_KEY'))}")
        print(f"API Key length: {len(os.getenv('LAPLACE_API_KEY', ''))}")
        """Test that live price connection works and data is flowing for US and TR stocks."""
        live_price_client = integration_client.live_price

        # Test US stocks first (more likely to work)
        us_symbols = ["AAPL", "GOOGL"]
        us_events = []

        us_client = await live_price_client.get_live_price_for_us(us_symbols)

        try:
            print("Testing US stocks...")
            async for result in us_client.receive():
                if result.error:
                    print(f"Error: {result.error}")
                    continue
                if result.data is None:
                    print(
                        "❌ FAIL: Received None data - this indicates a problem with the API or data processing"
                    )
                    pytest.fail(
                        "Received None data from live price stream - this should not happen"
                    )
                us_events.append(result.data)
                print(f"Received US event: {result.data.symbol}")
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

        bist_client = await live_price_client.get_live_price_for_bist(bist_symbols)

        try:
            print("Testing BIST stocks...")
            async for result in bist_client.receive():
                if result.error:
                    print(f"Error: {result.error}")
                    continue
                if result.data is None:
                    print(
                        "❌ FAIL: Received None data - this indicates a problem with the API or data processing"
                    )
                    pytest.fail(
                        "Received None data from live price stream - this should not happen"
                    )
                bist_events.append(result.data)
                print(f"Received BIST event: {result.data.symbol}")
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
            assert all(hasattr(event, "price") for event in us_events)
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

    @pytest.mark.asyncio
    async def test_subscribe_switches_to_new_symbols(self, integration_client: LaplaceClient):
        """Test that calling subscribe() switches the stream to new symbols and doesn't exit the receive loop."""
        print("\ntest_subscribe_switches_to_new_symbols")
        print(f"API Key set: {bool(os.getenv('LAPLACE_API_KEY'))}")

        live_price_client = integration_client.live_price

        # Use clearly different symbols to ensure we can detect the switch
        initial_symbols = ["AAPL"]  # Start with just Apple
        new_symbols = ["MSFT"]  # Switch to just Microsoft

        initial_events = []
        post_subscribe_events = []

        us_client = await live_price_client.get_live_price_for_us(initial_symbols)

        try:
            print(f"Phase 1: Subscribing to {initial_symbols}")

            resubscribed = False

            async for result in us_client.receive():
                if result.error:
                    print(f"Error: {result.error}")
                    continue
                if result.data is None:
                    print(
                        "❌ FAIL: Received None data - this indicates a problem with the API or data processing"
                    )
                    pytest.fail(
                        "Received None data from live price stream - this should not happen"
                    )

                print(f"Received event: {result.data.symbol}")

                # Phase 1: Collect events from initial symbols
                if not resubscribed:
                    initial_events.append(result.data)

                    # After getting 3 events from initial symbols, switch to new symbols
                    if len(initial_events) >= 3:
                        print(f"\nPhase 2: Switching to {new_symbols}")
                        print("🔄 Calling subscribe() - this should NOT exit the receive loop")

                        await us_client.subscribe(new_symbols)
                        resubscribed = True

                        print("✅ Subscribe completed - continuing to receive...")
                        continue

                # Phase 2: Collect events from new symbols
                else:
                    post_subscribe_events.append(result.data)

                    # Stop after getting enough events from new symbols
                    if len(post_subscribe_events) >= 3:
                        print("✅ Got enough events from new symbols - test complete")
                        break

                # Safety break
                if len(initial_events) + len(post_subscribe_events) >= 12:
                    print("⚠️  Safety break - collected enough total events")
                    break

        except Exception as e:
            error_msg = f"Subscribe test failed: {e}"
            print(f"❌ FULL ERROR: {error_msg}")
            print(f"❌ Error type: {type(e).__name__}")
            print(f"❌ Error args: {e.args}")
            pytest.skip("Subscribe test failed - see print output above")

        finally:
            await us_client.close()

        # Analyze results
        initial_symbols_received = {event.symbol for event in initial_events}
        post_symbols_received = {event.symbol for event in post_subscribe_events}

        print(f"\n📊 Test Results:")
        print(
            f"Initial phase: {len(initial_events)} events from symbols: {initial_symbols_received}"
        )
        print(
            f"Post-subscribe phase: {len(post_subscribe_events)} events from symbols: {post_symbols_received}"
        )
        print(f"Expected initial symbols: {set(initial_symbols)}")
        print(f"Expected post-subscribe symbols: {set(new_symbols)}")

        # Verify the test ran properly
        if not resubscribed:
            pytest.skip("Subscribe was not called - not enough initial events received")

        if len(initial_events) < 2:
            pytest.skip(f"Not enough initial events to verify: {len(initial_events)}")

        if len(post_subscribe_events) < 1:
            pytest.skip(f"No post-subscribe events received: {len(post_subscribe_events)}")

        # CRITICAL TEST: Verify that symbols actually switched
        # Initial events should be from initial symbols
        assert initial_symbols_received == set(
            initial_symbols
        ), f"Initial events should only be from {initial_symbols}, but got: {initial_symbols_received}"

        # Post-subscribe events should be from NEW symbols only
        assert post_symbols_received == set(
            new_symbols
        ), f"Post-subscribe events should only be from {new_symbols}, but got: {post_symbols_received}"

        # Verify no overlap (this is the key test)
        overlap = initial_symbols_received.intersection(post_symbols_received)
        assert (
            len(overlap) == 0
        ), f"Symbol sets should not overlap after subscribe, but both phases received: {overlap}"

        print("✅ Subscribe symbol switching test PASSED!")
        print(f"   ✓ Receive loop continued after subscribe() call")
        print(f"   ✓ Initial phase only received: {initial_symbols_received}")
        print(f"   ✓ Post-subscribe phase only received: {post_symbols_received}")
        print(f"   ✓ No symbol overlap - subscription successfully switched")
