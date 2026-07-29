#!/usr/bin/env python3
"""
Static check: validate that task.toml [metadata] labels belong to the
closed-set vocabulary defined in references/diversity-taxonomy.toml.

Usage:
    python references/check-diversity-labels.py task/task.toml

Exit codes:
    0  — all labels valid
    1  — one or more labels are not in the closed set (FAIL)
"""

import sys
import re

# ---------------------------------------------------------------------------
# Closed sets — copied verbatim from diversity-taxonomy.toml
# ---------------------------------------------------------------------------

TASK_OBJECTIVE = {
    "implement", "fix", "configure", "analyze", "transform", "validate",
    "optimize", "migrate", "refactor", "test", "debug", "build_or_package",
    "deploy_or_operate", "recover_or_repair_artifact", "generate",
    "compare_or_select", "secure_or_harden", "automate_workflow",
}

ARTIFACT_TYPE = {
    "codebase", "single_script_or_program", "test_suite_or_benchmark",
    "build_system_or_package_metadata", "configuration_file", "shell_environment",
    "service_or_daemon", "container_or_virtual_environment",
    "database_or_structured_store", "dataset_or_tabular_file", "text_or_log_file",
    "document_or_report", "archive_or_compressed_artifact",
    "binary_executable_or_library", "media_artifact", "model_or_checkpoint",
    "hardware_or_firmware_artifact", "network_endpoint_or_protocol_artifact",
    "repository_history_or_version_control_state", "security_artifact",
    "mathematical_or_scientific_model", "generated_output_artifact",
}

CATEGORIES = {
    "software_engineering",
    "debugging_and_repair",
    "build_dependency_and_release_management",
    "systems_infrastructure_and_operations",
    "data_processing_and_etl",
    "data_querying_and_databases",
    "data_science_and_reporting",
    "machine_learning_and_ai",
    "model_training_and_ml_infrastructure",
    "security",
    "scientific_computing_and_domain_science",
    "mathematics_and_formal_reasoning",
    "hardware_embedded_and_low_level_systems",
    "file_and_media_operations",
    "games_puzzles_and_interactive_simulation",
    "regulated_knowledge_work_and_business_operations",
}


# ---------------------------------------------------------------------------
# Minimal TOML array parser (no external deps)
# ---------------------------------------------------------------------------

def parse_toml_array(line):
    """Extract list of quoted string values from a TOML inline array."""
    return re.findall(r'"([^"]+)"', line)


def parse_toml_string(line):
    """Extract a single quoted string value from a TOML key = '...' line."""
    m = re.search(r'=\s*"([^"]+)"', line)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Main check
# ---------------------------------------------------------------------------

def check(path):
    failed = False

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_metadata = False
    for raw in lines:
        line = raw.strip()

        if line == "[metadata]":
            in_metadata = True
            continue
        if line.startswith("[") and line != "[metadata]":
            in_metadata = False

        if not in_metadata:
            continue

        # category
        if line.startswith("category"):
            val = parse_toml_string(line)
            if val and val.lower().replace(" ", "_") not in CATEGORIES:
                print(f"FAIL  category '{val}' is not a recognised category.")
                print(f"      Valid categories: {sorted(CATEGORIES)}")
                failed = True
            elif val:
                print(f"PASS  category = \"{val}\"")

        # subcategory — open set, just warn
        if line.startswith("subcategory"):
            val = parse_toml_string(line)
            if val:
                print(f"INFO  subcategory = \"{val}\" (open set — not validated)")

        # task_objective — closed set
        if line.startswith("task_objective"):
            vals = parse_toml_array(line)
            for v in vals:
                if v not in TASK_OBJECTIVE:
                    print(f"FAIL  task_objective '{v}' is not in the closed set.")
                    print(f"      Valid values: {sorted(TASK_OBJECTIVE)}")
                    failed = True
                else:
                    print(f"PASS  task_objective = \"{v}\"")

        # artifact_type — closed set
        if line.startswith("artifact_type"):
            vals = parse_toml_array(line)
            for v in vals:
                if v not in ARTIFACT_TYPE:
                    print(f"FAIL  artifact_type '{v}' is not in the closed set.")
                    print(f"      Valid values: {sorted(ARTIFACT_TYPE)}")
                    failed = True
                else:
                    print(f"PASS  artifact_type = \"{v}\"")

    return failed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <task.toml>")
        sys.exit(1)

    any_failed = False
    for toml_path in sys.argv[1:]:
        print(f"\n--- Checking {toml_path} ---")
        if check(toml_path):
            any_failed = True

    print()
    if any_failed:
        print("RESULT: FAIL — one or more labels are not in the closed set.")
        sys.exit(1)
    else:
        print("RESULT: PASS — all labels are valid.")
        sys.exit(0)
