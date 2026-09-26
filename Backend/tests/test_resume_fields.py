import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import GeminiService


def test_resume_profile_includes_contact_fields():
    text = """
    Jane Smith
    jane.smith@example.com
    +1 (415) 555-0102
    San Francisco, CA
    Senior Python Engineer
    Python, SQL, AWS
    """

    result = GeminiService().extract_resume_profile(text)

    assert result.get("name") == "Jane Smith"
    assert result.get("email") == "jane.smith@example.com"
    assert result.get("phone") == "+1 (415) 555-0102"
    assert result.get("location") == "San Francisco, CA"
    assert isinstance(result.get("skills"), list)
    assert any(item.get("name") == "Python" for item in result.get("skills", []))
