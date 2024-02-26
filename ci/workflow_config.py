
# Parameters that are required for Action yml file
WORKFLOW_CONFIG = {
    # STAGE_<LEVEL>_<NUM> : job_name
    'stages_config': {
        'STAGE_0_0': 'TestMe1',
        'STAGE_0_1': 'TestMe2',
        'STAGE_0_2': 'TestMe3',
        # 'STAGE_0_3': 'TestMe4',
    },
    # jon_name : job_config
    'jobs_config': {
        "TestMe1": {
            'runner_type': 'ubuntu-latest',
            'parametrized': ["Max", "Anna"]
        },
        "TestMe2": {
            'runner_type': 'ubuntu-latest',
        },
        "TestMe3": {
            'runner_type': 'ubuntu-latest',
        },
        "TestMe4": {
            'runner_type': 'ubuntu-latest',
        },
    }
}

# Parameters which are not required in workflow file
JOBS_CONFIG = {
    # jon_name : job_config
    "TestMe1": {
        'run_command': 'echo Hello, $PARAM'
    },
    "TestMe2": {
        'run_command': 'echo Hello everyone!'
    },
    "TestMe3": {
        'run_command': 'echo Hello everyone, exit $(($(date +%s) % 2))!; exit "$(($(date +%s) % 2))"'
    },
    "TestMe4": {
        'run_command': 'echo Hello everyone, exit 0!; exit 0'
    }
}
