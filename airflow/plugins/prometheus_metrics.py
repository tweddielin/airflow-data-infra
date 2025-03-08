"""
Prometheus Metrics Plugin for Airflow.

This plugin exposes Airflow metrics to Prometheus.
"""

import time
from flask import Response, Blueprint
from airflow.plugins_manager import AirflowPlugin
from airflow.settings import Session
from airflow.models import DagModel, DagRun, TaskInstance
from airflow.utils.state import State
from prometheus_client import generate_latest, REGISTRY, Gauge, Counter

# DAG Metrics
dag_info = Gauge('airflow_dag_info', 'Airflow DAG information', ['dag_id', 'owner', 'schedule_interval'])
dag_status = Gauge('airflow_dag_status', 'Airflow DAG status', ['dag_id', 'status'])
dag_run_status = Gauge('airflow_dag_run_status', 'Airflow DAG run status', ['dag_id', 'run_id', 'status'])
dag_run_duration = Gauge('airflow_dag_run_duration', 'Airflow DAG run duration', ['dag_id', 'run_id'])

# Task Metrics
task_status = Gauge('airflow_task_status', 'Airflow task status', ['dag_id', 'task_id', 'status'])
task_duration = Gauge('airflow_task_duration', 'Airflow task duration', ['dag_id', 'task_id'])

# Scheduler Metrics
scheduler_heartbeat = Gauge('airflow_scheduler_heartbeat', 'Airflow scheduler heartbeat')
scheduler_tasks_running = Gauge('airflow_scheduler_tasks_running', 'Airflow scheduler tasks running')

# Executor Metrics
executor_open_slots = Gauge('airflow_executor_open_slots', 'Airflow executor open slots')
executor_queued_tasks = Gauge('airflow_executor_queued_tasks', 'Airflow executor queued tasks')
executor_running_tasks = Gauge('airflow_executor_running_tasks', 'Airflow executor running tasks')


def get_dag_status_metrics():
    """Get DAG status metrics."""
    session = Session()
    try:
        dag_status.clear()
        dag_info.clear()
        
        # Get DAG information
        dag_models = session.query(DagModel).all()
        for dag in dag_models:
            dag_info.labels(
                dag_id=dag.dag_id,
                owner=dag.owners,
                schedule_interval=dag.schedule_interval
            ).set(1)
            
            # Set DAG status
            dag_status.labels(dag_id=dag.dag_id, status='active').set(1 if dag.is_active else 0)
            dag_status.labels(dag_id=dag.dag_id, status='paused').set(1 if dag.is_paused else 0)
    finally:
        session.close()


def get_dag_run_metrics():
    """Get DAG run metrics."""
    session = Session()
    try:
        dag_run_status.clear()
        dag_run_duration.clear()
        
        # Get DAG run information
        dag_runs = session.query(DagRun).all()
        for dag_run in dag_runs:
            # Set DAG run status
            for state in State.dag_states:
                dag_run_status.labels(
                    dag_id=dag_run.dag_id,
                    run_id=dag_run.run_id,
                    status=state
                ).set(1 if dag_run.state == state else 0)
            
            # Set DAG run duration if the run has ended
            if dag_run.end_date and dag_run.start_date:
                duration = (dag_run.end_date - dag_run.start_date).total_seconds()
                dag_run_duration.labels(
                    dag_id=dag_run.dag_id,
                    run_id=dag_run.run_id
                ).set(duration)
    finally:
        session.close()


def get_task_metrics():
    """Get task metrics."""
    session = Session()
    try:
        task_status.clear()
        task_duration.clear()
        
        # Get task information
        task_instances = session.query(TaskInstance).all()
        for ti in task_instances:
            # Set task status
            for state in State.task_states:
                task_status.labels(
                    dag_id=ti.dag_id,
                    task_id=ti.task_id,
                    status=state
                ).set(1 if ti.state == state else 0)
            
            # Set task duration if the task has ended
            if ti.end_date and ti.start_date:
                duration = (ti.end_date - ti.start_date).total_seconds()
                task_duration.labels(
                    dag_id=ti.dag_id,
                    task_id=ti.task_id
                ).set(duration)
    finally:
        session.close()


def get_scheduler_metrics():
    """Get scheduler metrics."""
    # These metrics would typically come from the scheduler
    # For now, we'll just set some placeholder values
    scheduler_heartbeat.set(time.time())
    scheduler_tasks_running.set(0)


def get_executor_metrics():
    """Get executor metrics."""
    # These metrics would typically come from the executor
    # For now, we'll just set some placeholder values
    executor_open_slots.set(32)
    executor_queued_tasks.set(0)
    executor_running_tasks.set(0)


def get_metrics():
    """Get all metrics."""
    get_dag_status_metrics()
    get_dag_run_metrics()
    get_task_metrics()
    get_scheduler_metrics()
    get_executor_metrics()
    return generate_latest(REGISTRY)


# Create a Flask Blueprint for the metrics endpoint
metrics_blueprint = Blueprint(
    'metrics', __name__,
    url_prefix='/metrics'
)

@metrics_blueprint.route('/')
def serve_metrics():
    """Serve metrics endpoint."""
    return Response(get_metrics(), mimetype='text/plain')


class PrometheusMetricsPlugin(AirflowPlugin):
    """Airflow Plugin for Prometheus Metrics."""
    
    name = "prometheus_metrics"
    
    # Register the Flask Blueprint
    flask_blueprints = [metrics_blueprint]
    
    hooks = []
    executors = []
    macros = []
    admin_views = []
    menu_links = []
    appbuilder_views = []
    appbuilder_menu_items = [] 