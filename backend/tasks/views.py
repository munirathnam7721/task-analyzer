# backend/tasks/views.py
from datetime import date
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import TaskSerializer
from task_analyzer.scoring import calculate_priority


class BaseTaskView(APIView):
    def _process_tasks(self, task_list):
        processed_tasks = []

        for task_data in task_list:
            t = dict(task_data)
            t['id'] = str(t.get('id') or str(uuid.uuid4()))

            due_raw = t.get('due_date')
            if due_raw:
                if isinstance(due_raw, date):
                    t['due_date'] = due_raw
                else:
                    try:
                        t['due_date'] = date.fromisoformat(str(due_raw))
                    except Exception as e:
                        raise ValueError(
                            f"Invalid date for task '{t.get('title','<no title>')}': {due_raw}. Use YYYY-MM-DD."
                        ) from e
            else:
                t['due_date'] = None

            deps = t.get('dependencies', '')
            if deps is None:
                t['dependencies'] = []
            elif isinstance(deps, list):
                t['dependencies'] = deps
            elif isinstance(deps, str):
                t['dependencies'] = [d.strip() for d in deps.split(',') if d.strip()]
            else:
                try:
                    t['dependencies'] = list(deps)
                except Exception:
                    t['dependencies'] = []

            try:
                t['importance'] = int(t.get('importance', 5) or 5)
            except Exception:
                t['importance'] = 5

            try:
                t['estimated_hours'] = float(t.get('estimated_hours', 1) or 1)
            except Exception:
                t['estimated_hours'] = 1.0

            processed_tasks.append(t)

        for task in processed_tasks:
            score, explanation = calculate_priority(task, processed_tasks)
            task['priority_score'] = score
            task['explanation'] = explanation

        for t in processed_tasks:
            d = t.get('due_date')
            if hasattr(d, 'isoformat'):
                t['due_date'] = d.isoformat()
            else:
                t['due_date'] = None if d is None else str(d)

        return processed_tasks


class TaskAnalyzeView(BaseTaskView):
    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a JSON array (list) of tasks."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            scored_tasks = self._process_tasks(request.data)
        except ValueError as ve:
            return Response(
                {"error": "Invalid input data", "detail": str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Failed to process tasks", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        scored_tasks.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        return Response(scored_tasks, status=status.HTTP_200_OK)


class TaskSuggestView(BaseTaskView):
    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a JSON array (list) of tasks."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            scored_tasks = self._process_tasks(request.data)
        except ValueError as ve:
            return Response(
                {"error": "Invalid input data", "detail": str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Failed to process tasks", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        scored_tasks.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        top_3 = scored_tasks[:3]

        response_data = []
        for task in top_3:
            response_data.append({
                'id': task.get('id'),
                'title': task.get('title'),
                'priority_score': round(task.get('priority_score', 0), 2),
                'explanation': task.get('explanation', '')
            })

        return Response(response_data, status=status.HTTP_200_OK)
