from src.severity.classifier import SeverityClassifier, SeverityTier


def test_forklift_overload_is_critical(rules_path):
    classifier = SeverityClassifier(rules_path=rules_path)

    decision = classifier.classify(
        {"behavior_class": "Carrying_Overload_with_Forklift", "metadata": {}}
    )

    assert decision.severity == SeverityTier.CRITICAL


def test_walkway_violation_escalates_near_machinery(rules_path):
    classifier = SeverityClassifier(rules_path=rules_path)

    decision = classifier.classify(
        {
            "behavior_class": "Safe_Walkway_Violation",
            "metadata": {"person_proximity_to_machinery": 0.4}
        }
    )

    assert decision.severity == SeverityTier.HIGH
    assert decision.applied_rules == ["person_proximity_to_machinery < 1.0"]


def test_unknown_behavior_defaults_to_medium(rules_path):
    classifier = SeverityClassifier(rules_path=rules_path)

    decision = classifier.classify({"behavior_class": "Unknown"})

    assert decision.severity == SeverityTier.MEDIUM
