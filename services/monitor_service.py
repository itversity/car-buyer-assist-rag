"""
Monitor service for fetching observability data from LangSmith.

This module handles fetching and parsing LangSmith trace data for
document processing and query operations, returning typed model objects.
"""

from typing import List, Optional
from datetime import datetime

from langsmith import Client

from config.settings import settings
from models.monitoring import (
    DocumentProcessingRun,
    BatchProcessingRun,
    QueryRun,
    MonitoringSummary
)
from utils.logger import get_logger

logger = get_logger(__name__)


class MonitorService:
    """Service for fetching monitoring data from LangSmith."""
    
    def __init__(self, project_name: Optional[str] = None):
        """
        Initialize monitor service.
        
        Args:
            project_name: LangSmith project name. If None, uses value from settings.
        """
        self.project_name = project_name or settings.langsmith_project
        self.client = Client(api_key=settings.langsmith_api_key)
        logger.info(f"Monitor service initialized for project: {self.project_name}")
    
    def get_document_processing_runs(self, limit: int = 10) -> List[DocumentProcessingRun]:
        """
        Fetch recent document processing runs from LangSmith.
        
        Args:
            limit: Maximum number of runs to fetch
            
        Returns:
            List of DocumentProcessingRun objects
        """
        logger.info(f"Fetching {limit} document processing runs")
        
        try:
            runs = list(self.client.list_runs(
                project_name=self.project_name,
                filter='eq(name, "process_document")',
                limit=limit,
                order_by="-start_time"
            ))
            
            logger.debug(f"Found {len(runs)} document processing runs")
            
            processed_runs = []
            for run in runs:
                try:
                    # Extract from nested output structure
                    if not run.outputs or 'output' not in run.outputs:
                        logger.warning(f"Run {run.id} missing outputs")
                        continue
                    
                    output_data = run.outputs['output']
                    filename = output_data.get('filename', 'Unknown')
                    chunks_created = output_data.get('chunks_created', 0)
                    model_name = output_data.get('model_name', 'N/A')
                    
                    # Calculate duration
                    duration = 0.0
                    if run.end_time and run.start_time:
                        duration = (run.end_time - run.start_time).total_seconds()
                    
                    # Create typed object
                    # Try to get URL from run object, fallback to constructed URL
                    trace_url = getattr(run, 'url', None) or f"https://smith.langchain.com/public/{run.id}/r"
                    
                    doc_run = DocumentProcessingRun(
                        run_id=str(run.id),
                        timestamp=run.start_time,
                        filename=filename,
                        model_name=model_name,
                        chunks_created=chunks_created,
                        duration_sec=round(duration, 2),
                        status=run.status,
                        langsmith_url=trace_url
                    )
                    processed_runs.append(doc_run)
                    
                except Exception as e:
                    logger.error(f"Error processing run {run.id}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(processed_runs)} document runs")
            return processed_runs
            
        except Exception as e:
            logger.error(f"Error fetching document processing runs: {e}")
            return []
    
    def get_batch_processing_runs(self, limit: int = 10) -> List[BatchProcessingRun]:
        """
        Fetch recent batch document processing runs from LangSmith.
        
        Args:
            limit: Maximum number of runs to fetch
            
        Returns:
            List of BatchProcessingRun objects
        """
        logger.info(f"Fetching {limit} batch processing runs")
        
        try:
            runs = list(self.client.list_runs(
                project_name=self.project_name,
                filter='eq(name, "process_multiple_documents")',
                limit=limit,
                order_by="-start_time"
            ))
            
            logger.debug(f"Found {len(runs)} batch processing runs")
            
            processed_runs = []
            for run in runs:
                try:
                    # Extract from nested output structure
                    if not run.outputs or 'output' not in run.outputs:
                        logger.warning(f"Run {run.id} missing outputs")
                        continue
                    
                    output_data = run.outputs['output']
                    
                    # Calculate metrics from results array
                    results = output_data.get('results', [])
                    total_docs = len(results)
                    successful = sum(1 for r in results if r.get('status') == 'success')
                    failed = sum(1 for r in results if r.get('status') != 'success')
                    total_chunks = sum(r.get('chunks_created', 0) for r in results if r.get('status') == 'success')
                    
                    # Calculate duration
                    duration = 0.0
                    if run.end_time and run.start_time:
                        duration = (run.end_time - run.start_time).total_seconds()
                    
                    # Create typed object
                    # Try to get URL from run object, fallback to constructed URL
                    trace_url = getattr(run, 'url', None) or f"https://smith.langchain.com/public/{run.id}/r"
                    
                    batch_run = BatchProcessingRun(
                        run_id=str(run.id),
                        timestamp=run.start_time,
                        total_documents=total_docs,
                        successful_documents=successful,
                        failed_documents=failed,
                        total_chunks=total_chunks,
                        duration_sec=round(duration, 2),
                        status=run.status,
                        langsmith_url=trace_url
                    )
                    processed_runs.append(batch_run)
                    
                except Exception as e:
                    logger.error(f"Error processing batch run {run.id}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(processed_runs)} batch runs")
            return processed_runs
            
        except Exception as e:
            logger.error(f"Error fetching batch processing runs: {e}")
            return []
    
    def get_query_runs(self, limit: int = 10) -> List[QueryRun]:
        """
        Fetch recent RAG query runs from LangSmith.
        
        Args:
            limit: Maximum number of runs to fetch
            
        Returns:
            List of QueryRun objects
        """
        logger.info(f"Fetching {limit} query runs")
        
        try:
            runs = list(self.client.list_runs(
                project_name=self.project_name,
                filter='eq(name, "rag_query")',
                limit=limit,
                order_by="-start_time"
            ))
            
            logger.debug(f"Found {len(runs)} query runs")
            
            processed_runs = []
            for run in runs:
                try:
                    # Extract question from inputs
                    question = 'Unknown'
                    if run.inputs:
                        question = run.inputs.get('question', 'Unknown')
                    
                    # Extract answer and metadata from outputs
                    answer = ''
                    sources = []
                    retrieved_chunks = 0
                    
                    if run.outputs and 'output' in run.outputs:
                        output_data = run.outputs['output']
                        answer = output_data.get('answer', '')
                        sources = output_data.get('sources', [])
                        retrieved_chunks = output_data.get('retrieved_chunks', 0)
                    
                    # Calculate duration
                    duration = 0.0
                    if run.end_time and run.start_time:
                        duration = (run.end_time - run.start_time).total_seconds()
                    
                    # Create typed object
                    # Try to get URL from run object, fallback to constructed URL
                    trace_url = getattr(run, 'url', None) or f"https://smith.langchain.com/public/{run.id}/r"
                    
                    query_run = QueryRun(
                        run_id=str(run.id),
                        timestamp=run.start_time,
                        question=question,
                        answer=answer,
                        sources=sources,
                        retrieved_chunks=retrieved_chunks,
                        duration_sec=round(duration, 2),
                        status=run.status,
                        langsmith_url=trace_url
                    )
                    processed_runs.append(query_run)
                    
                except Exception as e:
                    logger.error(f"Error processing query run {run.id}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(processed_runs)} query runs")
            return processed_runs
            
        except Exception as e:
            logger.error(f"Error fetching query runs: {e}")
            return []
    
    def get_summary_metrics(self) -> MonitoringSummary:
        """
        Calculate aggregate metrics across all operation types.
        
        Returns:
            MonitoringSummary object with aggregate statistics
        """
        logger.info("Calculating summary metrics")
        
        try:
            # Fetch recent runs from all operation types
            doc_runs = self.get_document_processing_runs(limit=50)
            batch_runs = self.get_batch_processing_runs(limit=50)
            query_runs = self.get_query_runs(limit=50)
            
            # Calculate totals
            total_operations = len(doc_runs) + len(batch_runs) + len(query_runs)
            total_documents = len(doc_runs) + sum(r.total_documents for r in batch_runs)
            total_queries = len(query_runs)
            
            # Calculate average duration
            all_durations = (
                [r.duration_sec for r in doc_runs] +
                [r.duration_sec for r in batch_runs] +
                [r.duration_sec for r in query_runs]
            )
            avg_duration = sum(all_durations) / len(all_durations) if all_durations else 0.0
            
            # Calculate success rate
            successful = sum(
                1 for r in doc_runs if r.status == "success"
            ) + sum(
                1 for r in batch_runs if r.status == "success"
            ) + sum(
                1 for r in query_runs if r.status == "success"
            )
            success_rate = successful / total_operations if total_operations > 0 else 1.0
            
            # Find most recent operation
            all_timestamps = (
                [r.timestamp for r in doc_runs] +
                [r.timestamp for r in batch_runs] +
                [r.timestamp for r in query_runs]
            )
            last_operation = max(all_timestamps) if all_timestamps else None
            
            summary = MonitoringSummary(
                total_operations=total_operations,
                total_documents_processed=total_documents,
                total_queries_executed=total_queries,
                avg_duration_sec=round(avg_duration, 2),
                success_rate=success_rate,
                last_operation_time=last_operation
            )
            
            logger.info(f"Summary: {total_operations} operations, {success_rate:.1%} success rate")
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating summary metrics: {e}")
            # Return empty summary
            return MonitoringSummary(
                total_operations=0,
                total_documents_processed=0,
                total_queries_executed=0,
                avg_duration_sec=0.0,
                success_rate=0.0
            )
