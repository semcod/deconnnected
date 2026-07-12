from deconnected.agent.models import ValidationStep
from deconnected.refactor.verify import VerificationRunner

def test_verification_runs_and_stops_on_required_failure(tmp_path):
    checks = [
        ValidationStep(command=["python", "-c", "print('ok')"], description="ok"),
        ValidationStep(command=["python", "-c", "raise SystemExit(2)"], description="bad"),
        ValidationStep(command=["python", "-c", "print('never')"], description="never"),
    ]
    result = VerificationRunner().run(tmp_path, checks)
    assert len(result) == 2
    assert result[0].passed
    assert not result[1].passed
