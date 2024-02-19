is_production_flags = [
    '--set autoscaling.enabled=true',
    '--set autoscaling.minReplicas=4',
    '--set-string resources.requests.cpu=3000m',
    '--set-string resources.requests.memory=4Gi'
]
