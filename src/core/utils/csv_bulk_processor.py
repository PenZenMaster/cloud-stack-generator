"""
Filename: csv_bulk_processor.py
Path: E:\\projects\\cloud-stack-generator\\src\\core\\utils\\csv_bulk_processor.py
Description: CSV bulk processing utility for multiple city page generation
Supports batch processing of city data for scalable page generation

Version: 1.0.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

import csv
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from ..config.models import ClientConfig
from ..generators.city_page_generator import CityPageGenerator


@dataclass
class CityProcessingResult:
    """Result of processing a single city"""
    city_name: str
    success: bool
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    word_count: int = 0
    generation_time_ms: int = 0
    

@dataclass
class BulkProcessingResult:
    """Result of bulk processing operation"""
    total_cities: int
    successful: int
    failed: int
    output_directory: str
    processing_time_ms: int
    results: List[CityProcessingResult]
    

class CSVBulkProcessor:
    """CSV-driven bulk processor for city page generation"""
    
    def __init__(self, config: ClientConfig):
        """
        Initialize CSV bulk processor
        
        Args:
            config: Client configuration
        """
        self.config = config
        self.city_generator = CityPageGenerator(config)
    
    def process_cities_from_csv(self, csv_file_path: str, output_dir: str, 
                               **options) -> BulkProcessingResult:
        """
        Process cities from CSV file and generate pages
        
        Args:
            csv_file_path: Path to CSV file with city data
            output_dir: Output directory for generated pages
            **options: Additional processing options
            
        Returns:
            BulkProcessingResult with processing summary
        """
        start_time = datetime.now()
        results = []
        
        # Read cities from CSV
        try:
            cities_data = self._read_cities_csv(csv_file_path)
        except Exception as e:
            return BulkProcessingResult(
                total_cities=0,
                successful=0,
                failed=1,
                output_directory=output_dir,
                processing_time_ms=0,
                results=[CityProcessingResult(
                    city_name="CSV_READ_ERROR",
                    success=False,
                    error_message=f"Failed to read CSV: {str(e)}"
                )]
            )
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Process each city
        for city_data in cities_data:
            city_result = self._process_single_city(city_data, output_dir, **options)
            results.append(city_result)
        
        # Calculate summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        end_time = datetime.now()
        processing_time = int((end_time - start_time).total_seconds() * 1000)
        
        return BulkProcessingResult(
            total_cities=len(results),
            successful=successful,
            failed=failed,
            output_directory=output_dir,
            processing_time_ms=processing_time,
            results=results
        )
    
    def process_cities_from_list(self, cities_list: List[str], output_dir: str,
                                **options) -> BulkProcessingResult:
        """
        Process cities from a simple list
        
        Args:
            cities_list: List of city names
            output_dir: Output directory for generated pages
            **options: Additional processing options
            
        Returns:
            BulkProcessingResult with processing summary
        """
        start_time = datetime.now()
        results = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert list to city data format
        cities_data = []
        for city in cities_list:
            if city.strip():
                cities_data.append({
                    "city_name": city.strip(),
                    "focus_keyword": options.get("default_focus_keyword", 
                                                self.config.business.industry or "services")
                })
        
        # Process each city
        for city_data in cities_data:
            city_result = self._process_single_city(city_data, output_dir, **options)
            results.append(city_result)
        
        # Calculate summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        end_time = datetime.now()
        processing_time = int((end_time - start_time).total_seconds() * 1000)
        
        return BulkProcessingResult(
            total_cities=len(results),
            successful=successful,
            failed=failed,
            output_directory=output_dir,
            processing_time_ms=processing_time,
            results=results
        )
    
    def _read_cities_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """
        Read cities data from CSV file
        
        Expected CSV format:
        - city_name (required): Name of the city
        - focus_keyword (optional): Primary keyword for the page
        - custom_intro (optional): Custom introduction paragraph
        - custom_cta (optional): Custom call-to-action
        
        Args:
            csv_file_path: Path to CSV file
            
        Returns:
            List of city data dictionaries
        """
        cities_data = []
        
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # Try to detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, start=2):  # Start from 2 (header is row 1)
                # Skip empty rows
                if not any(value.strip() for value in row.values() if value):
                    continue
                
                # Validate required fields
                city_name = row.get("city_name", "").strip()
                if not city_name:
                    # Try alternative column names
                    city_name = (row.get("City", "") or 
                               row.get("Location", "") or 
                               row.get("location", "") or
                               row.get("city", "")).strip()
                
                if not city_name:
                    raise ValueError(f"Row {row_num}: city_name is required")
                
                # Extract data
                city_data = {
                    "city_name": city_name,
                    "focus_keyword": row.get("focus_keyword", "").strip(),
                    "custom_intro": row.get("custom_intro", "").strip(),
                    "custom_cta": row.get("custom_cta", "").strip(),
                    "custom_content": row.get("custom_content", "").strip(),
                    "row_number": row_num
                }
                
                # Set default focus keyword if not provided
                if not city_data["focus_keyword"]:
                    city_data["focus_keyword"] = self.config.business.industry or "services"
                
                cities_data.append(city_data)
        
        return cities_data
    
    def _process_single_city(self, city_data: Dict[str, Any], output_dir: str,
                           **options) -> CityProcessingResult:
        """
        Process a single city and generate its page
        
        Args:
            city_data: Dictionary with city information
            output_dir: Output directory
            **options: Additional options
            
        Returns:
            CityProcessingResult for this city
        """
        city_name = city_data["city_name"]
        start_time = datetime.now()
        
        try:
            # Prepare generation options
            generation_options = {
                "focus_keyword": city_data.get("focus_keyword"),
                **options
            }
            
            # Override default content if custom content is provided
            if city_data.get("custom_intro"):
                generation_options["custom_intro"] = city_data["custom_intro"]
            if city_data.get("custom_cta"):
                generation_options["custom_cta"] = city_data["custom_cta"]
            
            # Generate page
            file_path = self.city_generator.save_city_page(
                city_name, 
                output_dir, 
                **generation_options
            )
            
            # Calculate generation time
            end_time = datetime.now()
            generation_time = int((end_time - start_time).total_seconds() * 1000)
            
            # Estimate word count (simple approximation)
            word_count = self._estimate_word_count(file_path)
            
            return CityProcessingResult(
                city_name=city_name,
                success=True,
                file_path=file_path,
                word_count=word_count,
                generation_time_ms=generation_time
            )
            
        except Exception as e:
            end_time = datetime.now()
            generation_time = int((end_time - start_time).total_seconds() * 1000)
            
            return CityProcessingResult(
                city_name=city_name,
                success=False,
                error_message=str(e),
                generation_time_ms=generation_time
            )
    
    def _estimate_word_count(self, file_path: str) -> int:
        """
        Estimate word count of generated HTML file
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            Estimated word count
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple word count (can be enhanced to parse HTML properly)
            # Remove HTML tags for better word count
            import re
            text_content = re.sub(r'<[^>]+>', ' ', content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            return len(text_content.split())
        
        except Exception:
            return 0
    
    def generate_processing_report(self, result: BulkProcessingResult, 
                                 report_path: Optional[str] = None) -> str:
        """
        Generate a processing report
        
        Args:
            result: BulkProcessingResult to generate report for
            report_path: Optional path to save report (otherwise returns as string)
            
        Returns:
            Report content as string
        """
        report_lines = [
            "# City Page Generation Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- Total Cities: {result.total_cities}",
            f"- Successful: {result.successful}",
            f"- Failed: {result.failed}",
            f"- Success Rate: {(result.successful/result.total_cities*100):.1f}%" if result.total_cities > 0 else "- Success Rate: 0%",
            f"- Total Processing Time: {result.processing_time_ms/1000:.2f} seconds",
            f"- Average Time per City: {result.processing_time_ms/result.total_cities:.0f}ms" if result.total_cities > 0 else "- Average Time per City: 0ms",
            f"- Output Directory: {result.output_directory}",
            "",
            "## Detailed Results",
            ""
        ]
        
        # Add successful cities
        successful_cities = [r for r in result.results if r.success]
        if successful_cities:
            report_lines.extend([
                "### ✅ Successfully Generated Pages",
                ""
            ])
            
            for city_result in successful_cities:
                report_lines.append(
                    f"- **{city_result.city_name}**: "
                    f"{city_result.word_count} words, "
                    f"{city_result.generation_time_ms}ms, "
                    f"File: {os.path.basename(city_result.file_path) if city_result.file_path else 'N/A'}"
                )
            
            report_lines.append("")
        
        # Add failed cities
        failed_cities = [r for r in result.results if not r.success]
        if failed_cities:
            report_lines.extend([
                "### ❌ Failed to Generate Pages",
                ""
            ])
            
            for city_result in failed_cities:
                report_lines.append(
                    f"- **{city_result.city_name}**: {city_result.error_message}"
                )
            
            report_lines.append("")
        
        # Add statistics
        if successful_cities:
            total_words = sum(r.word_count for r in successful_cities)
            avg_words = total_words / len(successful_cities)
            avg_time = sum(r.generation_time_ms for r in successful_cities) / len(successful_cities)
            
            report_lines.extend([
                "## Statistics",
                f"- Total Words Generated: {total_words:,}",
                f"- Average Words per Page: {avg_words:.0f}",
                f"- Average Generation Time: {avg_time:.0f}ms",
                ""
            ])
        
        report_content = "\n".join(report_lines)
        
        # Save to file if path provided
        if report_path:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        return report_content
    
    @staticmethod
    def create_sample_csv(file_path: str, sample_cities: Optional[List[str]] = None):
        """
        Create a sample CSV file for bulk processing
        
        Args:
            file_path: Path where to create the sample CSV
            sample_cities: Optional list of sample cities
        """
        if sample_cities is None:
            sample_cities = [
                "Chicago, IL",
                "Detroit, MI", 
                "Milwaukee, WI",
                "Indianapolis, IN",
                "Cleveland, OH"
            ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['city_name', 'focus_keyword', 'custom_intro', 'custom_cta']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for city in sample_cities:
                writer.writerow({
                    'city_name': city,
                    'focus_keyword': '',  # Will use default from business config
                    'custom_intro': '',   # Will use generated intro
                    'custom_cta': ''      # Will use generated CTA
                })


# Convenience function for quick bulk processing
def process_cities_bulk(config: ClientConfig, cities: List[str], 
                       output_dir: str, **options) -> BulkProcessingResult:
    """
    Convenience function for bulk processing a list of cities
    
    Args:
        config: Client configuration
        cities: List of city names
        output_dir: Output directory
        **options: Additional options
        
    Returns:
        BulkProcessingResult
    """
    processor = CSVBulkProcessor(config)
    return processor.process_cities_from_list(cities, output_dir, **options)