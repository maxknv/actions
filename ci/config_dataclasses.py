
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Union

from workflow_config import JOBS_CONFIG, WORKFLOW_CONFIG


@dataclass
class JobConfig:
    run_command: str

@dataclass
class JobWfConfig:
    runner_type: Union[str, List[str]]
    # parameters for matrix job
    parametrized: Optional[List[Any]] = (None,)


class Config:
    @staticmethod
    def get_job_config(job_name: str) -> JobConfig:
        assert job_name in JOBS_CONFIG, "Job name must be valid name from JOBS_CONFIG"
        return JobConfig(**JOBS_CONFIG[job_name])

    def get_workflow_config() -> Dict[str, Any]:
        res = {}
        for k, v in WORKFLOW_CONFIG.items():
            if k not in 'jobs_config':
                res[k] = v
            else:
                res['jobs_config'] = {}
                for job, config in v.items():
                    res['jobs_config'][job] = asdict(JobWfConfig(**config))
        return res

    @staticmethod
    def get_jobs() -> List[str]:
        return list(JOBS_CONFIG.keys())
