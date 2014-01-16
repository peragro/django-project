import django.dispatch

workflow_task_new = django.dispatch.Signal(providing_args=["instance"])

workflow_task_transition = django.dispatch.Signal(providing_args=["instance", "transition", "old_state", "new_state"])

workflow_task_resolved = django.dispatch.Signal(providing_args=["instance", "transition", "old_state", "new_state"])
