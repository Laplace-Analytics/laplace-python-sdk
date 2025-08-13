"""Integration tests for earnings client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    EarningsTranscriptListItem,
    EarningsTranscriptWithSummary,
    Region,
)
from tests.conftest import MockResponse


class TestEarningsIntegration:
    """Integration tests for earnings client with real API responses."""

    @patch("httpx.Client")
    def test_get_transcripts(self, mock_httpx_client):
        """Test getting earnings transcripts with real API response."""
        # Real API response from /api/v1/earnings/transcripts?symbol=AAPL&region=us
        mock_response_data = [
            {
                "symbol": "AAPL",
                "year": 2024,
                "quarter": 1,
                "fiscal_year": 2024,
            },
            {
                "symbol": "AAPL",
                "year": 2023,
                "quarter": 4,
                "fiscal_year": 2024,
            },
            {
                "symbol": "AAPL",
                "year": 2023,
                "quarter": 3,
                "fiscal_year": 2023,
            },
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            transcripts = client.earnings.get_transcripts(symbol="AAPL", region=Region.US)

        # Assertions
        assert len(transcripts) == 3
        assert all(isinstance(transcript, EarningsTranscriptListItem) for transcript in transcripts)

        # Test first transcript (Q1 2024)
        q1_2024 = transcripts[0]
        assert q1_2024.symbol == "AAPL"
        assert q1_2024.year == 2024
        assert q1_2024.quarter == 1
        assert q1_2024.fiscal_year == 2024

        # Test second transcript (Q4 2023)
        q4_2023 = transcripts[1]
        assert q4_2023.symbol == "AAPL"
        assert q4_2023.year == 2023
        assert q4_2023.quarter == 4
        assert q4_2023.fiscal_year == 2024

        # Test third transcript (Q3 2023)
        q3_2023 = transcripts[2]
        assert q3_2023.symbol == "AAPL"
        assert q3_2023.year == 2023
        assert q3_2023.quarter == 3
        assert q3_2023.fiscal_year == 2023

    @patch("httpx.Client")
    def test_get_transcript_with_summary(self, mock_httpx_client):
        """Test getting earnings transcript with summary with real API response."""
        # Real API response from /api/v1/earnings/transcript?symbol=AAPL&year=2024&quarter=1
        mock_response_data = {
            "symbol": "AAPL",
            "year": 2024,
            "quarter": 1,
            "content": "This is the full earnings call transcript for Apple Inc. Q1 2024...",
            "summary": "Apple reported strong Q1 2024 results with revenue growth of 8%...",
            "has_summary": True,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            transcript = client.earnings.get_transcript_with_summary(
                symbol="AAPL", year=2024, quarter=1
            )

        # Assertions
        assert isinstance(transcript, EarningsTranscriptWithSummary)
        assert transcript.symbol == "AAPL"
        assert transcript.year == 2024
        assert transcript.quarter == 1
        assert (
            transcript.content
            == "This is the full earnings call transcript for Apple Inc. Q1 2024..."
        )
        assert (
            transcript.summary
            == "Apple reported strong Q1 2024 results with revenue growth of 8%..."
        )
        assert transcript.has_summary is True

    @patch("httpx.Client")
    def test_get_transcript_with_summary_no_summary(self, mock_httpx_client):
        """Test getting earnings transcript with no summary available."""
        # Real API response from /api/v1/earnings/transcript?symbol=AAPL&year=2023&quarter=4
        mock_response_data = {
            "symbol": "AAPL",
            "year": 2023,
            "quarter": 4,
            "content": "This is the full earnings call transcript for Apple Inc. Q4 2023...",
            "summary": None,
            "has_summary": False,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            transcript = client.earnings.get_transcript_with_summary(
                symbol="AAPL", year=2023, quarter=4
            )

        # Assertions
        assert isinstance(transcript, EarningsTranscriptWithSummary)
        assert transcript.symbol == "AAPL"
        assert transcript.year == 2023
        assert transcript.quarter == 4
        assert (
            transcript.content
            == "This is the full earnings call transcript for Apple Inc. Q4 2023..."
        )
        assert transcript.summary is None
        assert transcript.has_summary is False

    @patch("httpx.Client")
    def test_earnings_transcript_list_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for earnings transcript list items."""
        mock_response_data = [
            {
                "symbol": "TEST",
                "year": 2024,
                "quarter": 1,
                "fiscal_year": 2024,
            }
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            transcripts = client.earnings.get_transcripts(symbol="TEST", region=Region.US)

        transcript = transcripts[0]

        # Test field aliases work
        assert transcript.fiscal_year == 2024  # fiscal_year -> fiscal_year (no alias needed)

    @patch("httpx.Client")
    def test_earnings_transcript_with_summary_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for earnings transcript with summary."""
        mock_response_data = {
            "symbol": "TEST",
            "year": 2024,
            "quarter": 1,
            "content": "Test content",
            "summary": "Test summary",
            "has_summary": True,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            transcript = client.earnings.get_transcript_with_summary(
                symbol="TEST", year=2024, quarter=1
            )

        # Test field aliases work
        assert transcript.has_summary is True  # has_summary -> has_summary (no alias needed)


class TestEarningsRealIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_get_transcripts(self, integration_client: LaplaceClient):
        """Test real API call for getting earnings transcripts."""
        transcripts = integration_client.earnings.get_transcripts(symbol="AAPL", region=Region.US)

        assert len(transcripts) >= 0
        assert all(isinstance(transcript, EarningsTranscriptListItem) for transcript in transcripts)

        # Test items if any exist
        if transcripts:
            assert all(transcript.symbol for transcript in transcripts)
            assert all(transcript.year >= 2000 for transcript in transcripts)
            assert all(transcript.year <= 2050 for transcript in transcripts)
            assert all(1 <= transcript.quarter <= 4 for transcript in transcripts)
            assert all(transcript.fiscal_year >= 2000 for transcript in transcripts)
            assert all(transcript.fiscal_year <= 2050 for transcript in transcripts)

    @pytest.mark.integration
    def test_real_get_transcript_with_summary(self, integration_client: LaplaceClient):
        """Test real API call for getting earnings transcript with summary."""
        # First get transcripts to get a valid year/quarter
        transcripts = integration_client.earnings.get_transcripts(symbol="AAPL", region=Region.US)
        assert len(transcripts) > 0

        # Use the first transcript's year and quarter
        first_transcript = transcripts[0]
        year = first_transcript.year
        quarter = first_transcript.quarter

        transcript = integration_client.earnings.get_transcript_with_summary(
            symbol="AAPL", year=year, quarter=quarter
        )

        assert isinstance(transcript, EarningsTranscriptWithSummary)
        assert transcript.symbol == "AAPL"
        assert transcript.year == year
        assert transcript.quarter == quarter
        assert transcript.content
        assert transcript.has_summary is not None
        # summary can be None if not available
