from datetime import date
from math import log1p


WEIGHTS = {
    'urgency': 0.60,      
    'importance': 0.25,   
    'effort': 0.10,       
    'dependency': 0.05,   
}
MAX_EFFORT_HOURS = 15 


def detect_circular_dependencies(task_id, task_map, visiting=None, visited=None):
    """
    Detects if a dependency loop exists starting from task_id using DFS.
    Returns: True if a cycle is detected, False otherwise.
    """
    if visiting is None: visiting = set()
    if visited is None: visited = set()
    
    
    
    if task_id in visiting: return True
    if task_id in visited: return False

    visiting.add(task_id)
    task = task_map.get(task_id)

    if not task:
        visiting.remove(task_id)
        visited.add(task_id)
        return False
    
    dependencies = task.get('dependencies')
    
    if dependencies and isinstance(dependencies, list):
        for dep_id in dependencies:
            if dep_id in task_map: 
                if detect_circular_dependencies(dep_id, task_map, visiting, visited):
                    return True

    visiting.remove(task_id)
    visited.add(task_id)
    return False


def calculate_priority(task, all_tasks_data):
    """Calculates the priority score for a single task and provides an explanation."""
    
    due_date = task.get('due_date')
    importance = task.get('importance', 5)
    estimated_hours = task.get('estimated_hours', 1)

    today = date.today()
    days_until_due = (due_date - today).days if due_date else 9999

    if days_until_due <= 0:
        days_overdue = abs(days_until_due)
        F_urgency = 1.0 + log1p(days_overdue)
        urgency_explanation = f"Critically Past Due ({days_overdue} days). "
    else:
        F_urgency = 1.0 / (days_until_due * 0.5 + 1)
        F_urgency = min(1.0, F_urgency)
        urgency_explanation = f"Due in {days_until_due} days. "

    F_importance = importance / 10.0
    importance_explanation = f"Importance: {importance}/10. "

    effort_normalized = min(estimated_hours, MAX_EFFORT_HOURS) / MAX_EFFORT_HOURS
    F_effort = 1.0 - effort_normalized
    effort_explanation = f"Effort: {estimated_hours} hours. "

    task_map = {t['id']: t for t in all_tasks_data if 'id' in t}
    task_id = task.get('id') 
    
    blocker_count = 0
    dependency_explanation = "No dependencies. "
    
    if task_id and detect_circular_dependencies(task_id, task_map):
        F_dependency = 0.0
        dependency_explanation = "**CIRCULAR DEPENDENCY DETECTED. Dependency factor ignored.** " 
    else:
        for other_task in all_tasks_data:
            dependencies_list = other_task.get('dependencies', [])
            
            if isinstance(dependencies_list, list) and task_id in dependencies_list:
                blocker_count += 1
        
        max_blockers = len(all_tasks_data) - 1
        F_dependency = blocker_count / max_blockers if max_blockers > 0 else 0
        dependency_explanation = f"Blocks {blocker_count} other tasks. "

    priority_score = (
        WEIGHTS['urgency'] * F_urgency +
        WEIGHTS['importance'] * F_importance +
        WEIGHTS['effort'] * F_effort +
        WEIGHTS['dependency'] * F_dependency
    )
    
    explanation = f"{urgency_explanation}{importance_explanation}{effort_explanation}{dependency_explanation}"
    
    return priority_score, explanation.strip()