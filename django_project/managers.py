from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text

class CommentManager(models.Manager):

    def for_model(self, model):
        """
        QuerySet for all comments for a particular model (either an instance or
        a class).
        """
        ct = ContentType.objects.get_for_model(model)
        qs = self.get_query_set().filter(content_type=ct)
        if isinstance(model, models.Model):
            qs = qs.filter(object_pk=force_text(model._get_pk_val()))
        return qs



from django.db.models.fields.related import ManyToManyField
from django.contrib.contenttypes.fields import GenericForeignKey

class ObjectTaskMixin(models.Model):
    _object_tasks = GenericForeignKey('ObjectTask',
        'content_type',
        'object_pk'
    )

    class Meta:
        abstract = True

    @property
    def tasks(self):
      from django_project.models import Task
      return Task.objects.filter(objecttask_tasks__content_type=self._content_type(), objecttask_tasks__object_pk=self._object_pk())

    def _content_type(self):
      return ContentType.objects.get_for_model(self)

    def _object_pk(self):
      return force_text(self._get_pk_val())

    def _filter(self, model):
      return self._object_tasks
      #return model.objects.filter(content_type=self._content_type(), object_pk=self._object_pk())

    def add_task(self, task):
      from django_project.models import ObjectTask
      if self._filter(ObjectTask).filter(task=task).count() == 0:
        ot = ObjectTask(task=task, content_object=self)
        ot.save()

    def remove_task(self, task):
      from django_project.models import ObjectTask
      self._filter(ObjectTask).filter(task=task).delete()

    def tasks_for_author(self, user):
      return self.tasks.filter(author=user)
