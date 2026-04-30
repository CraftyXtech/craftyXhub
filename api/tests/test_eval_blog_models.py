import importlib.util
import sys
from argparse import Namespace
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "eval_blog_models.py"
SPEC = importlib.util.spec_from_file_location("eval_blog_models", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_load_cases_can_filter_by_configured_word_count():
    cases = MODULE._load_cases(
        path=None,
        case_limit=None,
        case_word_count="short",
        case_names=None,
    )

    assert {case["name"] for case in cases} == {
        "health_how_to_short",
        "creator_tutorial_short",
        "seo_local_service_short",
        "listicle_short",
    }


def test_build_cases_can_use_per_case_word_count():
    args = Namespace(
        cases_json=None,
        case_limit=None,
        case_word_count="long",
        case_names=None,
        models="qwen-3.6-max-preview",
        runs_per_case=1,
        word_count="case",
        tone="professional",
        language="en-US",
        creativity=0.6,
        use_web_search=False,
        per_run_timeout_seconds=120.0,
    )

    cases = MODULE._build_cases(args)

    assert len(cases) == 1
    assert cases[0].inputs.case_name == "technical_tutorial_long"
    assert cases[0].inputs.word_count == "long"


def test_summarize_by_model_marks_smooth_model_when_gates_pass():
    case = {
        "inputs": {"model": "qwen-3.6-max-preview", "word_count": "short"},
        "output": {
            "ok": True,
            "generation_time_s": 20.0,
            "body_word_count": 420,
            "source_count": 2,
        },
        "scores": {
            "overall_quality_score": {"value": 0.95},
            "seo_score": {"value": 1.0},
            "style_score": {"value": 1.0},
            "grounding_score": {"value": 1.0},
            "editorial_score": {"value": 22},
            "latency_score": {"value": 0.8},
        },
        "assertions": {
            "generated": {"value": True},
            "structure_valid": {"value": True},
            "deterministic_quality_passed": {"value": True},
            "editorial_quality_passed": {"value": True},
        },
    }

    summary = MODULE._summarize_by_model([case])[0]

    assert summary["production_smooth"] is True
    assert summary["short_length_pass_rate"] == 1.0
    assert summary["editorial_pass_rate"] == 1.0
    assert summary["avg_editorial_score"] == 22


def test_default_eval_models_are_blog_enabled_only():
    args = MODULE.build_parser().parse_args([])

    assert args.models == "glm-5.1,deepseek-v4-pro,qwen-3.6-max-preview"
    assert "gpt-5.4" not in args.models
