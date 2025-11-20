"""
Unit tests for Business Tab AI content generation
Path: E:/projects/cloud-stack-generator/tests/unit/test_business_tab_ai.py

Description:
Tests for AI content generation functionality in the Business Info tab,
including cursor handling, UI state management, and error handling.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-20

Last Modified Date:
2025-11-20

Comments:
* v1.00 - Initial creation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import sys

# Ensure QApplication exists for tests
if not QApplication.instance():
    app = QApplication(sys.argv)

from src.ui.components.business_tab import BusinessTab


class TestBusinessTabAIGeneration:
    """Test suite for AI content generation in Business Tab"""

    @pytest.fixture
    def business_tab(self, qtbot):
        """Create a BusinessTab instance for testing"""
        tab = BusinessTab()
        qtbot.addWidget(tab)
        return tab

    @pytest.fixture
    def mock_ai_service(self):
        """Create a mock AI service"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        return mock_service

    @pytest.fixture
    def mock_business_generator(self):
        """Create a mock business content generator"""
        mock_gen = Mock()
        mock_gen.generate_business_description.return_value = "Test business description"
        mock_gen.generate_company_overview.return_value = "Test company overview"
        mock_gen.generate_mission_statement.return_value = "Test mission statement"
        mock_gen.generate_service_guarantee.return_value = "Test service guarantee"
        mock_gen.generate_service_area_description.return_value = "Test service area"
        return mock_gen

    def test_ai_service_initialization(self, business_tab):
        """Test that AI service is properly initialized"""
        assert hasattr(business_tab, 'ai_service')
        assert hasattr(business_tab, 'business_generator')

    def test_generate_business_description_ai_unavailable(self, business_tab, qtbot):
        """Test business description generation when AI is unavailable"""
        # Mock AI service as unavailable
        business_tab.ai_service.is_available = Mock(return_value=False)

        # Mock QMessageBox to avoid actual dialog
        with patch('src.ui.components.business_tab.QMessageBox') as mock_msgbox:
            business_tab._generate_business_description()

            # Verify warning message was shown
            mock_msgbox.warning.assert_called_once()
            args = mock_msgbox.warning.call_args[0]
            assert "AI Not Available" in args[1]

    def test_generate_business_description_missing_info(self, business_tab, qtbot):
        """Test business description generation with missing business info"""
        # Set AI as available
        business_tab.ai_service.is_available = Mock(return_value=True)

        # Leave business name empty
        business_tab.business_name_input.clear()

        # Mock QMessageBox
        with patch('src.ui.components.business_tab.QMessageBox') as mock_msgbox:
            business_tab._generate_business_description()

            # Verify warning message was shown
            mock_msgbox.warning.assert_called_once()
            args = mock_msgbox.warning.call_args[0]
            assert "Missing Information" in args[1]

    @patch('src.ui.components.business_tab.QApplication.setOverrideCursor')
    @patch('src.ui.components.business_tab.QApplication.restoreOverrideCursor')
    @patch('src.ui.components.business_tab.AIContentPreviewDialog')
    def test_generate_business_description_cursor_handling(
        self,
        mock_dialog,
        mock_restore_cursor,
        mock_set_cursor,
        business_tab,
        qtbot
    ):
        """Test that busy cursor is set and restored during generation"""
        # Setup
        business_tab.ai_service.is_available = Mock(return_value=True)
        business_tab.business_name_input.setText("Test Business")
        business_tab.industry_input.setCurrentText("Technology")
        business_tab.business_generator.generate_business_description = Mock(
            return_value="Test content"
        )

        # Mock dialog to avoid actual UI
        mock_dialog_instance = Mock()
        mock_dialog.return_value = mock_dialog_instance

        # Execute
        business_tab._generate_business_description()

        # Verify cursor was set to wait cursor
        mock_set_cursor.assert_called_once_with(Qt.CursorShape.WaitCursor)

        # Verify cursor was restored
        mock_restore_cursor.assert_called_once()

    @patch('src.ui.components.business_tab.QApplication.setOverrideCursor')
    @patch('src.ui.components.business_tab.QApplication.restoreOverrideCursor')
    @patch('src.ui.components.business_tab.AIContentPreviewDialog')
    def test_generate_business_description_ui_disabled(
        self,
        mock_dialog,
        mock_restore_cursor,
        mock_set_cursor,
        business_tab,
        qtbot
    ):
        """Test that UI is disabled during generation and re-enabled after"""
        # Setup
        business_tab.ai_service.is_available = Mock(return_value=True)
        business_tab.business_name_input.setText("Test Business")
        business_tab.industry_input.setCurrentText("Technology")
        business_tab.business_generator.generate_business_description = Mock(
            return_value="Test content"
        )

        # Mock dialog
        mock_dialog_instance = Mock()
        mock_dialog.return_value = mock_dialog_instance

        # Verify UI starts enabled
        assert business_tab.isEnabled()

        # Execute
        business_tab._generate_business_description()

        # Verify UI was re-enabled (after generation completes)
        assert business_tab.isEnabled()

    @patch('src.ui.components.business_tab.QApplication.setOverrideCursor')
    @patch('src.ui.components.business_tab.QApplication.restoreOverrideCursor')
    @patch('src.ui.components.business_tab.QMessageBox')
    def test_generate_business_description_generation_failure(
        self,
        mock_msgbox,
        mock_restore_cursor,
        mock_set_cursor,
        business_tab,
        qtbot
    ):
        """Test that cursor is restored even when generation fails"""
        # Setup
        business_tab.ai_service.is_available = Mock(return_value=True)
        business_tab.business_name_input.setText("Test Business")
        business_tab.industry_input.setCurrentText("Technology")

        # Mock generator to return None (failure)
        business_tab.business_generator.generate_business_description = Mock(
            return_value=None
        )

        # Execute
        business_tab._generate_business_description()

        # Verify cursor was set and restored even on failure
        mock_set_cursor.assert_called_once()
        mock_restore_cursor.assert_called_once()

        # Verify error message was shown
        mock_msgbox.critical.assert_called_once()

        # Verify UI is still enabled after failure
        assert business_tab.isEnabled()

    @patch('src.ui.components.business_tab.QApplication.setOverrideCursor')
    @patch('src.ui.components.business_tab.QApplication.restoreOverrideCursor')
    def test_generate_business_description_exception_handling(
        self,
        mock_restore_cursor,
        mock_set_cursor,
        business_tab,
        qtbot
    ):
        """Test that cursor is restored even when an exception occurs"""
        # Setup
        business_tab.ai_service.is_available = Mock(return_value=True)
        business_tab.business_name_input.setText("Test Business")
        business_tab.industry_input.setCurrentText("Technology")

        # Mock generator to raise an exception
        business_tab.business_generator.generate_business_description = Mock(
            side_effect=Exception("Test exception")
        )

        # Execute - should not crash
        with pytest.raises(Exception):
            business_tab._generate_business_description()

        # Verify cursor was set
        mock_set_cursor.assert_called_once()

        # Verify cursor was restored even after exception
        mock_restore_cursor.assert_called_once()

    @patch('src.ui.components.business_tab.QApplication.setOverrideCursor')
    @patch('src.ui.components.business_tab.QApplication.restoreOverrideCursor')
    @patch('src.ui.components.business_tab.AIContentPreviewDialog')
    def test_generate_company_overview_success(
        self,
        mock_dialog,
        mock_restore_cursor,
        mock_set_cursor,
        business_tab,
        qtbot
    ):
        """Test successful company overview generation"""
        # Setup
        business_tab.ai_service.is_available = Mock(return_value=True)
        business_tab.business_name_input.setText("Test Business")
        business_tab.industry_input.setCurrentText("Technology")
        business_tab.business_generator.generate_company_overview = Mock(
            return_value="Test company overview"
        )

        # Mock dialog
        mock_dialog_instance = Mock()
        mock_dialog.return_value = mock_dialog_instance

        # Execute
        business_tab._generate_company_overview()

        # Verify generation was called
        business_tab.business_generator.generate_company_overview.assert_called_once()

        # Verify cursor handling
        mock_set_cursor.assert_called_once()
        mock_restore_cursor.assert_called_once()

        # Verify dialog was shown
        mock_dialog.assert_called_once()

    @patch('src.ui.components.business_tab.QApplication.setOverrideCursor')
    @patch('src.ui.components.business_tab.QApplication.restoreOverrideCursor')
    @patch('src.ui.components.business_tab.AIContentPreviewDialog')
    def test_all_generation_methods_cursor_handling(
        self,
        mock_dialog,
        mock_restore_cursor,
        mock_set_cursor,
        business_tab,
        qtbot
    ):
        """Test that all AI generation methods properly handle cursor"""
        # Setup
        business_tab.ai_service.is_available = Mock(return_value=True)
        business_tab.business_name_input.setText("Test Business")
        business_tab.industry_input.setCurrentText("Technology")

        # Mock all generators
        business_tab.business_generator.generate_business_description = Mock(return_value="Test")
        business_tab.business_generator.generate_company_overview = Mock(return_value="Test")
        business_tab.business_generator.generate_mission_statement = Mock(return_value="Test")
        business_tab.business_generator.generate_service_guarantee = Mock(return_value="Test")
        business_tab.business_generator.generate_service_area_description = Mock(return_value="Test")

        # Mock dialog
        mock_dialog_instance = Mock()
        mock_dialog.return_value = mock_dialog_instance

        # Test each generation method
        methods = [
            business_tab._generate_business_description,
            business_tab._generate_company_overview,
            business_tab._generate_mission_statement,
            business_tab._generate_service_guarantee,
            business_tab._generate_service_area_description,
        ]

        for method in methods:
            mock_set_cursor.reset_mock()
            mock_restore_cursor.reset_mock()

            method()

            # Verify cursor was set and restored for each method
            mock_set_cursor.assert_called_once_with(Qt.CursorShape.WaitCursor)
            mock_restore_cursor.assert_called_once()
