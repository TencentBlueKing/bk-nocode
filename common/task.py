# -*- coding: utf-8 -*-
from kombu import serialization
from celery import Task
from celery import current_app
from celery.result import denied_join_result
from kombu.utils.uuid import uuid


class CustomTask(Task):
    def apply_async(
        self,
        args=None,
        kwargs=None,
        task_id=None,
        producer=None,
        link=None,
        link_error=None,
        shadow=None,
        **options
    ):
        task_always_eager = kwargs.pop("task_always_eager", False)
        if self.typing:
            try:
                check_arguments = self.__header__
            except AttributeError:  # pragma: no cover
                pass
            else:
                check_arguments(*(args or ()), **(kwargs or {}))

        preopts = self._get_exec_options()
        options = dict(preopts, **options) if options else preopts

        options.setdefault("ignore_result", self.ignore_result)
        if self.priority:
            options.setdefault("priority", self.priority)

        app = self._get_app()
        if task_always_eager:
            with app.producer_or_acquire(producer) as eager_producer:
                serializer = options.get("serializer")
                if serializer is None:
                    if eager_producer.serializer:
                        serializer = eager_producer.serializer
                    else:
                        serializer = app.conf.task_serializer
                body = args, kwargs
                content_type, content_encoding, data = serialization.dumps(
                    body,
                    serializer,
                )
                args, kwargs = serialization.loads(
                    data, content_type, content_encoding, accept=[content_type]
                )
            with denied_join_result():
                return self.apply(
                    args,
                    kwargs,
                    task_id=task_id or uuid(),
                    link=link,
                    link_error=link_error,
                    **options
                )
        else:
            return app.send_task(
                self.name,
                args,
                kwargs,
                task_id=task_id,
                producer=producer,
                link=link,
                link_error=link_error,
                result_cls=self.AsyncResult,
                shadow=shadow,
                task_type=self,
                **options
            )


def mytask(*args, **kwargs):
    """Deprecated decorator, please use :func:`celery.task`."""
    return current_app.task(*args, **dict({"base": CustomTask}, **kwargs))
