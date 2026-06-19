"""Tests for severity classification module."""

import pytest
from src.severity.classifier import SeverityClassifier, SeverityTier

def test_forklift_overload_is_critical_with_condition(rules_path):
    classifier = SeverityClassifier(rules_path=rules_path)

    # With block_count > 3, it should escalate to CRITICAL
    decision = classifier.classify(
        {"behavior_class": "Carrying_Overload_with_Forklift", "metadata": {"block_count": 4}}
    )

    assert decision.severity == SeverityTier.CRITICAL
    assert "Extreme overload" in decision.rationale

def test_forklift_overload_base_is_high(rules_path):
    classifier = SeverityClassifier(rules_path=rules_path)

    # Without extra blocks, it should be HIGH
    decision = classifier.classify(
        {"behavior_class": "Carrying_Overload_with_Forklift", "metadata": {}}
    )

    assert decision.severity == SeverityTier.HIGH

def test_walkway_violation_escalates_with_personnel(rules_path):
    classifier = SeverityClassifier(rules_path=rules_path)

    decision = classifier.classify(
        {
            "behavior_class": "Safe_Walkway_Violation",
            "metadata": {"personnel_count": 3}
        }
    )

    assert decision.severity == SeverityTier.CRITICAL

def test_unknown_behavior_defaults_to_medium(rules_path):
    classifier = SeverityClassifier(rules_path=rules_path)

    decision = classifier.classify(
        {"behavior_class": "Unknown_Alien_Activity", "metadata": {}}
    )

    assert decision.severity == SeverityTier.MEDIUM
