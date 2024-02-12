#!/usr/bin/env python
import os

import requests
import json
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # repo = "https://github.com/justinc1/gha-experiment"
    # repo_api = " https://api.github.com/repos/justinc1/gha-experiment"
    # run_id = "7871225452"
    repo_api = f"{os.environ['GITHUB_API_URL']}/repos/{os.environ['GITHUB_REPOSITORY']}"
    run_id = os.environ["GITHUB_RUN_ID"]

    resp = requests.get(f"{repo_api}/actions/runs/{run_id}")
    run_data = resp.json()
    # print(f"run_data={json.dumps(run_data, indent=4)}")
    run_attempt = run_data['run_attempt']
    logger.info(f"Latest/current run_attempt={run_attempt}")
    if run_attempt == 1:
        retry_job_names = ""
        logger.info(f"retry_job_names={retry_job_names}")
        print(f"retry_job_names={retry_job_names}")
        return

    previous_run_attempt = run_attempt - 1
    previous_attempt_url = run_data['previous_attempt_url']
    # print(f"previous_attempt_url={run_data['previous_attempt_url']}")
    # previous_attempt_data = requests.get(previous_attempt_url).json()
    previous_attempt_jobs_url = f"{previous_attempt_url}/jobs"
    logger.info(f"previous_attempt_jobs_url={previous_attempt_jobs_url}")

    _jobs_data = requests.get(previous_attempt_jobs_url).json()
    previous_jobs = _jobs_data["jobs"]
    logger.info(f"previous_jobs count={len(previous_jobs)}")
    for job in previous_jobs:
        logger.info(f"job id={job['id']} status={job['status']} conclusion={job['conclusion']} name={job['name']}")

    # Decide which jobs should NOT be re-run.
    # https://docs.github.com/en/actions/learn-github-actions/contexts#steps-context
    # conclusion == success, failure, cancelled, or skipped.
    retry_needed_jobs = [
        job
        for job in previous_jobs
        if job["conclusion"] in ["failure", "cancelled"]
    ]
    retry_job_names = " ".join([
        job["name"]
        for job in retry_needed_jobs
    ])
    logger.info(f"retry_job_names={retry_job_names}")
    print(f"retry_job_names={retry_job_names}")


if __name__ == "__main__":
    main()
