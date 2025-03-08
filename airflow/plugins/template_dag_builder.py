"""
Template DAG Builder for Airflow.

This module provides a template-based approach to creating DAGs in Airflow.
It allows for easy creation of DAGs with common patterns and configurations.
"""

from typing import Dict, List, Optional, Union, Callable, Any
from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import BaseOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup


class TemplateDAGBuilder:
    """
    A builder class for creating templated DAGs in Airflow.
    
    This class provides a fluent interface for building DAGs with common patterns
    and configurations. It simplifies the process of creating DAGs by providing
    a template-based approach.
    """
    
    def __init__(
        self,
        dag_id: str,
        description: str = "",
        schedule_interval: Optional[Union[str, timedelta]] = None,
        start_date: Optional[datetime] = None,
        catchup: bool = False,
        tags: Optional[List[str]] = None,
        default_args: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new TemplateDAGBuilder.
        
        Args:
            dag_id: The ID of the DAG.
            description: A description of the DAG.
            schedule_interval: The schedule interval of the DAG.
            start_date: The start date of the DAG.
            catchup: Whether to catch up on missed DAG runs.
            tags: Tags for the DAG.
            default_args: Default arguments for the DAG.
        """
        self.dag_id = dag_id
        self.description = description
        self.schedule_interval = schedule_interval
        self.start_date = start_date or datetime(2023, 1, 1)
        self.catchup = catchup
        self.tags = tags or []
        
        self.default_args = {
            'owner': 'airflow',
            'depends_on_past': False,
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 1,
            'retry_delay': timedelta(minutes=5),
        }
        
        if default_args:
            self.default_args.update(default_args)
        
        self.dag = DAG(
            dag_id=self.dag_id,
            description=self.description,
            schedule_interval=self.schedule_interval,
            start_date=self.start_date,
            catchup=self.catchup,
            tags=self.tags,
            default_args=self.default_args,
        )
        
        self.tasks = {}
        self.task_groups = {}
    
    def add_task(
        self,
        task_id: str,
        operator: BaseOperator,
        upstream_tasks: Optional[List[str]] = None,
        downstream_tasks: Optional[List[str]] = None,
        group: Optional[str] = None,
    ) -> 'TemplateDAGBuilder':
        """
        Add a task to the DAG.
        
        Args:
            task_id: The ID of the task.
            operator: The operator to use for the task.
            upstream_tasks: The IDs of upstream tasks.
            downstream_tasks: The IDs of downstream tasks.
            group: The ID of the task group to add the task to.
            
        Returns:
            The TemplateDAGBuilder instance for method chaining.
        """
        if group and group not in self.task_groups:
            self.add_task_group(group)
        
        if group:
            with self.task_groups[group]:
                self.tasks[task_id] = operator
        else:
            self.tasks[task_id] = operator
        
        if upstream_tasks:
            for upstream_task_id in upstream_tasks:
                if upstream_task_id in self.tasks:
                    self.tasks[upstream_task_id] >> self.tasks[task_id]
        
        if downstream_tasks:
            for downstream_task_id in downstream_tasks:
                if downstream_task_id in self.tasks:
                    self.tasks[task_id] >> self.tasks[downstream_task_id]
        
        return self
    
    def add_python_task(
        self,
        task_id: str,
        python_callable: Callable,
        op_kwargs: Optional[Dict[str, Any]] = None,
        upstream_tasks: Optional[List[str]] = None,
        downstream_tasks: Optional[List[str]] = None,
        group: Optional[str] = None,
    ) -> 'TemplateDAGBuilder':
        """
        Add a Python task to the DAG.
        
        Args:
            task_id: The ID of the task.
            python_callable: The Python function to call.
            op_kwargs: Keyword arguments to pass to the Python function.
            upstream_tasks: The IDs of upstream tasks.
            downstream_tasks: The IDs of downstream tasks.
            group: The ID of the task group to add the task to.
            
        Returns:
            The TemplateDAGBuilder instance for method chaining.
        """
        operator = PythonOperator(
            task_id=task_id,
            python_callable=python_callable,
            op_kwargs=op_kwargs or {},
            dag=self.dag,
        )
        
        return self.add_task(
            task_id=task_id,
            operator=operator,
            upstream_tasks=upstream_tasks,
            downstream_tasks=downstream_tasks,
            group=group,
        )
    
    def add_dummy_task(
        self,
        task_id: str,
        upstream_tasks: Optional[List[str]] = None,
        downstream_tasks: Optional[List[str]] = None,
        group: Optional[str] = None,
    ) -> 'TemplateDAGBuilder':
        """
        Add a dummy task to the DAG.
        
        Args:
            task_id: The ID of the task.
            upstream_tasks: The IDs of upstream tasks.
            downstream_tasks: The IDs of downstream tasks.
            group: The ID of the task group to add the task to.
            
        Returns:
            The TemplateDAGBuilder instance for method chaining.
        """
        operator = DummyOperator(
            task_id=task_id,
            dag=self.dag,
        )
        
        return self.add_task(
            task_id=task_id,
            operator=operator,
            upstream_tasks=upstream_tasks,
            downstream_tasks=downstream_tasks,
            group=group,
        )
    
    def add_task_group(
        self,
        group_id: str,
        tooltip: Optional[str] = None,
    ) -> 'TemplateDAGBuilder':
        """
        Add a task group to the DAG.
        
        Args:
            group_id: The ID of the task group.
            tooltip: A tooltip for the task group.
            
        Returns:
            The TemplateDAGBuilder instance for method chaining.
        """
        self.task_groups[group_id] = TaskGroup(
            group_id=group_id,
            dag=self.dag,
            tooltip=tooltip,
        )
        
        return self
    
    def build(self) -> DAG:
        """
        Build and return the DAG.
        
        Returns:
            The built DAG.
        """
        return self.dag
    
    def create_extract_load_transform_pattern(
        self,
        extract_callable: Callable,
        transform_callable: Callable,
        load_callable: Callable,
        extract_kwargs: Optional[Dict[str, Any]] = None,
        transform_kwargs: Optional[Dict[str, Any]] = None,
        load_kwargs: Optional[Dict[str, Any]] = None,
    ) -> 'TemplateDAGBuilder':
        """
        Create an Extract-Load-Transform (ELT) pattern in the DAG.
        
        Args:
            extract_callable: The Python function for extraction.
            transform_callable: The Python function for transformation.
            load_callable: The Python function for loading.
            extract_kwargs: Keyword arguments for the extract function.
            transform_kwargs: Keyword arguments for the transform function.
            load_kwargs: Keyword arguments for the load function.
            
        Returns:
            The TemplateDAGBuilder instance for method chaining.
        """
        # Add start and end dummy tasks
        self.add_dummy_task(task_id="start")
        self.add_dummy_task(task_id="end")
        
        # Add extract task group
        self.add_task_group(group_id="extract", tooltip="Extract data from source")
        
        # Add transform task group
        self.add_task_group(group_id="transform", tooltip="Transform data")
        
        # Add load task group
        self.add_task_group(group_id="load", tooltip="Load data to destination")
        
        # Add extract task
        self.add_python_task(
            task_id="extract_data",
            python_callable=extract_callable,
            op_kwargs=extract_kwargs or {},
            upstream_tasks=["start"],
            group="extract",
        )
        
        # Add transform task
        self.add_python_task(
            task_id="transform_data",
            python_callable=transform_callable,
            op_kwargs=transform_kwargs or {},
            upstream_tasks=["extract_data"],
            group="transform",
        )
        
        # Add load task
        self.add_python_task(
            task_id="load_data",
            python_callable=load_callable,
            op_kwargs=load_kwargs or {},
            upstream_tasks=["transform_data"],
            downstream_tasks=["end"],
            group="load",
        )
        
        return self
    
    def create_parallel_processing_pattern(
        self,
        process_callables: List[Callable],
        process_task_ids: Optional[List[str]] = None,
        process_kwargs: Optional[List[Dict[str, Any]]] = None,
    ) -> 'TemplateDAGBuilder':
        """
        Create a parallel processing pattern in the DAG.
        
        Args:
            process_callables: The Python functions for processing.
            process_task_ids: The IDs of the processing tasks.
            process_kwargs: Keyword arguments for the processing functions.
            
        Returns:
            The TemplateDAGBuilder instance for method chaining.
        """
        # Add start and end dummy tasks
        self.add_dummy_task(task_id="start")
        self.add_dummy_task(task_id="end")
        
        # Add process task group
        self.add_task_group(group_id="process", tooltip="Process data in parallel")
        
        # Add process tasks
        for i, process_callable in enumerate(process_callables):
            task_id = process_task_ids[i] if process_task_ids and i < len(process_task_ids) else f"process_{i+1}"
            kwargs = process_kwargs[i] if process_kwargs and i < len(process_kwargs) else {}
            
            self.add_python_task(
                task_id=task_id,
                python_callable=process_callable,
                op_kwargs=kwargs,
                upstream_tasks=["start"],
                downstream_tasks=["end"],
                group="process",
            )
        
        return self 