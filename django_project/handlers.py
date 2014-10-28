from notifications import notify
from follow.models import Follow

from django_project import signals

#Monkey patching the Follow clean function
from django.core.exceptions import ValidationError
def clean(instance):
    '''
    Only allow a single target to be selected on follow!
    '''
    fields = [field.name for field in instance._meta.fields if not field.name in ['id', 'user', 'datetime']]
    values = filter(lambda a: a != None, [getattr(instance, field_name) for field_name in fields])
    if len(values) != 1:
        raise ValidationError('You should only set a single target!')
Follow.clean = clean
def __unicode__(instance):
    return str(instance.user)+' is following '+str(instance.target._meta.model_name)+' '+str(instance.target)
Follow.__unicode__ = __unicode__


def follow_handler(follower, followee, **kwargs):
    """
    """
    notify.send(follower,
                recipient=follower,
                actor=follower,
                verb='started following',
                action_object=followee,
                description='',
                target=getattr(followee, 'project', None))

def unfollow_handler(follower, followee, **kwargs):
    """
    """
    notify.send(follower,
                recipient=follower,
                actor=follower,
                verb='stopped following',
                action_object=followee,
                description='',
                target=getattr(followee, 'project', None))

# connect the signal
signals.follow.connect(follow_handler, dispatch_uid='django_project.handlers.follow')
signals.unfollow.connect(unfollow_handler, dispatch_uid='django_project.handlers.unfollow')


def workflow_task_handler_creator(verb):
    """
    """
    print('REG workflow_task_handler_creator::handler', verb)
    def handler(instance, *args, **kwargs):
        print('workflow_task_handler_creator::handler', verb)
        follow_obj = instance.project if verb=='created' else instance
        for follow in Follow.objects.get_follows(follow_obj):
            notify.send(instance.author,
                        recipient=follow.user,
                        actor=instance.author,
                        verb=verb,
                        action_object=instance,
                        description='',
                        target=instance.project)
    if not hasattr(workflow_task_handler_creator, 'instances'):
        workflow_task_handler_creator.instances = []
    workflow_task_handler_creator.instances.append(handler)
    return handler

def handler(instance, transition, old_state, new_state, **kwargs):
    print('workflow_task_handler_creator::handler22')

# connect the signal
signals.workflow_task_new.connect(workflow_task_handler_creator('created'), dispatch_uid='django_project.handlers.workflow_task_new')
signals.workflow_task_transition.connect(workflow_task_handler_creator('updated'), dispatch_uid='django_project.handlers.workflow_task_transition')
signals.workflow_task_resolved.connect(workflow_task_handler_creator('resolved'), dispatch_uid='django_project.handlers.workflow_task_resolved')


def commented_handler(instance, comment, **kwargs):
    for follow in Follow.objects.get_follows(instance):
        notify.send(instance.author,
                    recipient=follow.user,
                    actor=instance.author,
                    verb='commented',
                    action_object=comment,
                    description=comment.comment[:50]+'...',
                    target=instance)

    from django.contrib.contenttypes.models import ContentType
    from django.contrib.admin.models import LogEntry, ADDITION
    from django.utils.encoding import force_unicode
    LogEntry.objects.log_action(
        user_id         = instance.author.pk,
        content_type_id = ContentType.objects.get_for_model(comment).pk,
        object_id       = comment.pk,
        object_repr     = force_unicode(comment),
        action_flag     = ADDITION
    )

# connect the signal
signals.commented.connect(commented_handler, dispatch_uid='django_project.handlers.commented_handler')
