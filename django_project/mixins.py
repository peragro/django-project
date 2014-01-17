from django.db import models

from django.db import transaction
import reversion

from follow.models import Follow

from django_project.signals import workflow_task_transition, workflow_task_resolved, workflow_task_new


class ProjectMixin(object):
    def save(self, *args, **kwargs):
        ret = super(ProjectMixin, self).save(*args, **kwargs)
        #Author of the project is always following!
        Follow.objects.get_or_create(self.author, self)
        return ret


class TaskMixin(object):
    def versions(self):
        #version_list = reversion.get_for_object(self)
        version_list = reversion.get_unique_for_object(self)
        return version_list
        
    def nr_of_versions(self):
        version_list = reversion.get_unique_for_object(self)
        return len(version_list)
    
    def save_revision(self, user, comment, *args, **kwargs):
        with transaction.atomic(), reversion.create_revision():
            self.save()
            reversion.set_user(user)
            reversion.set_comment(comment)
    
        
    def save(self, *args, **kwargs):
        from django_project.models import Task, Transition
        
        exists = self.id is not None
        if exists:
            old_task = Task.objects.get(pk=self.id)
            old_state = old_task.status

        ret = super(TaskMixin, self).save(*args, **kwargs)

        if exists:
            new_state = self.status
            #print('TaskMixin::save 1', old_state, new_state)
            transition = Transition.objects.get(source=old_state, destination=new_state)
            print('TaskMixin::save 2', transition)
            
            if new_state.is_resolved:
                workflow_task_resolved.send(sender=Task, instance=self, transition=transition, old_state=old_state, new_state=new_state)
            else:
                workflow_task_transition.send(sender=Task, instance=self, transition=transition, old_state=old_state, new_state=new_state)
        else:
            workflow_task_new.send(sender=Task, instance=self)
            
        return ret
