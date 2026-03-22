from stackradar.analytics.tech_counter import count_technologies_in_jobs
from stackradar.storage.models import JobRecord


def test_counts_once_per_job() -> None:
    jobs = [
        JobRecord(
            id="1",
            title="Software Engineer",
            description="We use Python and python daily.",
            url="",
            fetched_at="",
        )
    ]
    techs = ["Python", "Java"]
    c = count_technologies_in_jobs(jobs, techs)
    assert c["Python"] == 1
    assert c["Java"] == 0


def test_golang_synonym() -> None:
    jobs = [
        JobRecord(
            id="2",
            title="Software Engineer Golang",
            description="",
            url="",
            fetched_at="",
        )
    ]
    c = count_technologies_in_jobs(jobs, ["Go (Golang)"])
    assert c["Go (Golang)"] == 1
