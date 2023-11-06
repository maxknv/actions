import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, Optional
from config_dataclasses import Config, JobConfig
from workflow_config import WORKFLOW_CONFIG



def get_check_name(check_name: str, batch: int, num_batches: int) -> str:
    res = check_name
    if num_batches > 1:
        res = f"{check_name} [{batch+1}/{num_batches}]"
    return res


def normalize_check_name(check_name: str) -> str:
    res = check_name.lower()
    for r in ((" ", "_"), ("(", "_"), (")", "_"), (",", "_"), ("/", "_")):
        res = res.replace(*r)
    return res


def is_build_job(job: str) -> bool:
    if "package_" in job or "binary_" in job or job == "fuzzers":
        return True
    return False


def is_test_job(job: str) -> bool:
    return not is_build_job(job) and not "Style" in job and not "Docs check" in job


def is_docs_job(job: str) -> bool:
    return "Docs check" in job


def parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    # FIXME: consider switching to sub_parser for configure, pre, run, post actions
    parser.add_argument(
        "--configure",
        action="store_true",
        help="Action that configures ci run. Calculates digests, checks job to be executed, generates json output",
    )
    parser.add_argument(
        "--update-gh-statuses",
        action="store_true",
        help="Action that recreate success GH statuses for jobs that finished successfully in past and will be skipped this time",
    )
    parser.add_argument(
        "--pre",
        action="store_true",
        help="Action that executes prerequesetes for the job provided in --job-name",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Action that executes run action for specified --job-name. run_command must be configured for a given job name.",
    )
    parser.add_argument(
        "--post",
        action="store_true",
        help="Action that executes post actions for the job provided in --job-name",
    )
    parser.add_argument(
        "--mark-success",
        action="store_true",
        help="Action that marks job provided in --job-name (with batch provided in --batch) as successfull",
    )
    parser.add_argument(
        "--job-name",
        default="",
        type=str,
        help="Job name as in config",
    )
    parser.add_argument(
        "--parametrized",
        default="",
        type=str,
        help="Parameter' set for job run (for --run action)",
    )
    parser.add_argument(
        "--run-config",
        default="",
        type=str,
        help="Input json file or json string with ci run config",
    )
    parser.add_argument(
        "--outfile",
        default="",
        type=str,
        required=False,
        help="otput file to write json result to, if not set - stdout",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=False,
        help="makes json output pretty formated",
    )
    parser.add_argument(
        "--skip-docker",
        action="store_true",
        default=False,
        help="skip fetching docker data from dockerhub, used in --configure action (for debugging)",
    )
    parser.add_argument(
        "--docker-digest-or-latest",
        action="store_true",
        default=False,
        help="temporary hack to fallback to latest if image with digest as a tag is not on docker hub",
    )
    parser.add_argument(
        "--skip-jobs",
        action="store_true",
        default=False,
        help="skip fetching data about job runs, used in --configure action (for debugging)",
    )
    parser.add_argument(
        "--rebuild-all-docker",
        action="store_true",
        default=False,
        help="will create run config for rebuilding all dockers, used in --configure action (for nightly docker job)",
    )
    parser.add_argument(
        "--rebuild-all-binaries",
        action="store_true",
        default=False,
        help="will create run config without skipping build jobs in any case, used in --configure action (for release branches)",
    )
    return parser.parse_args()

def _action_configure() -> Dict[str, Any]:
    res = Config.get_workflow_config()
    res['jobs_to_do'] = Config.get_jobs()
    return res

def _handle_parametrized(param: str) -> Dict[str, str]:
    if param:
        return {"PARAM": param}
    return {}


def main() -> int:
    exit_code = 0
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    args = parse_args(parser)

    # if args.mark_success or args.pre or args.post or args.run:
    #     assert args.run_config, "Run config must be provided via --run-config"
    #     assert args.job_name, "Job name must be provided via --job-name"

    run_config: Optional[Dict[str, Any]] = None
    if args.run_config:
        run_config = (
            json.loads(args.run_config)
            if not os.path.isfile(args.run_config)
            else json.load(open(args.run_config))
        )
        assert run_config and isinstance(run_config, dict), "Invalid --run-config json"

    result: Dict[str, Any] = {}

    if args.configure:
        result = _action_configure()
    elif args.update_gh_statuses:
        assert run_config, "Run config must be provided via --run-config"
        #_update_gh_statuses(run_config=run_config, s3=s3)
    elif args.pre:
        pass
    elif args.run:
        job_config = Config.get_job_config(args.job_name) # type: JobConfig
        run_command = job_config.run_command
        envs = _handle_parametrized(args.parametrized)
        print(f"Going to run command [{run_command}]")
        process = subprocess.run(
            run_command,
            env=envs,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
            check=False,
            shell=True,
        )
        if process.returncode == 0:
            print(f"Run action succeded for: [{args.job_name}]")
        else:
            print(
                f"Run action failed for: [{args.job_name}] with exit code [{process.returncode}]"
            )
            exit_code = process.returncode

    elif args.post:
        pass

    elif args.mark_success:
        pass

    # print results
    if args.outfile:
        with open(args.outfile, "w") as f:
            if isinstance(result, str):
                print(result, file=f)
            elif isinstance(result, dict):
                print(json.dumps(result, indent=2 if args.pretty else None), file=f)
            else:
                raise AssertionError(f"Unexpected type for 'res': {type(result)}")
    else:
        if isinstance(result, str):
            print(result)
        elif isinstance(result, dict):
            print(json.dumps(result, indent=2 if args.pretty else None))
        else:
            raise AssertionError(f"Unexpected type for 'res': {type(result)}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
