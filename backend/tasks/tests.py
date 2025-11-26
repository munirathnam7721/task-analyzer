from datetime import date, timedelta
from django.test import TestCase
from task_analyzer.scoring import calculate_priority, WEIGHTS
import uuid

def create_test_task(title, days_to_due, effort, importance, dependencies=[]):
    if days_to_due is None:
        due_date = date.today() + timedelta(days=999)
    else:
        due_date = date.today() + timedelta(days=days_to_due)
        
    return {
        'id': str(uuid.uuid4()),
        'title': title,
        'due_date': due_date,
        'estimated_hours': effort,
        'importance': importance,
        'dependencies': dependencies
    }

class PriorityAlgorithmTests(TestCase):
    def setUp(self):
        self.task_a = create_test_task("Task A (Blocker)", days_to_due=10, effort=5, importance=8, dependencies=[])
        self.task_b = create_test_task("Task B (Normal)", days_to_due=5, effort=2, importance=5, dependencies=[])
        self.task_c = create_test_task("Task C (Dependent)", days_to_due=20, effort=3, importance=4, dependencies=[self.task_a['id']])
        self.all_tasks = [self.task_a, self.task_b, self.task_c]

    def test_smart_balance_priority(self):
        urgent_task = create_test_task("Fix Critical Bug", days_to_due=1, effort=1, importance=3, dependencies=[])
        important_task = create_test_task("Plan Q4 Strategy", days_to_due=30, effort=15, importance=10, dependencies=[])
        score_urgent, _ = calculate_priority(urgent_task, [urgent_task, important_task])
        score_important, _ = calculate_priority(important_task, [urgent_task, important_task])
        self.assertGreater(score_urgent, score_important)
        self.assertGreater(score_urgent, 0.5)

    def test_past_due_date_handling(self):
        past_due_1 = create_test_task("Small Overdue Task", days_to_due=-1, effort=2, importance=5, dependencies=[])
        past_due_5 = create_test_task("Big Overdue Task", days_to_due=-5, effort=8, importance=7, dependencies=[])
        score_1, explanation_1 = calculate_priority(past_due_1, [past_due_1, past_due_5])
        score_5, explanation_5 = calculate_priority(past_due_5, [past_due_1, past_due_5])
        self.assertGreater(score_5, score_1)
        self.assertIn("Critically Past Due (5 days)", explanation_5)
        self.assertIn("Critically Past Due (1 days)", explanation_1)

    def test_dependency_boosting(self):
        score_a, _ = calculate_priority(self.task_a, self.all_tasks) 
        score_b, _ = calculate_priority(self.task_b, self.all_tasks)
        self.assertGreater(score_a, score_b)

    def test_dependency_cycle_detection(self):
        task_x = create_test_task("Task X", days_to_due=5, effort=3, importance=7, dependencies=['Y_ID'])
        task_y = create_test_task("Task Y", days_to_due=5, effort=3, importance=7, dependencies=['X_ID'])
        task_x['dependencies'] = [task_y['id']]
        task_y['dependencies'] = [task_x['id']]
        task_x['id'] = 'X_ID'
        task_y['id'] = 'Y_ID'
        all_cycle_tasks = [task_x, task_y]
        score_x, explanation_x = calculate_priority(task_x, all_cycle_tasks)
        self.assertIn("Dependency factor ignored", explanation_x)
