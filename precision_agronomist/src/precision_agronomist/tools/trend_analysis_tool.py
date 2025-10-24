from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import json


class TrendAnalysisInput(BaseModel):
    """Input schema for trend analysis."""
    time_period_days: int = Field(default=30, description="Number of days to analyze (default: 30)")
    disease_focus: str = Field(default="all", description="Specific disease to focus on, or 'all' for overall trends")


class TrendAnalysisTool(BaseTool):
    name: str = "Disease Trend Analyzer"
    description: str = (
        "Analyzes historical plant disease detection data to identify patterns and trends "
        "over weeks or months. Provides insights on disease progression, seasonal patterns, "
        "and areas requiring attention. Useful for proactive farm management."
    )
    args_schema: Type[BaseModel] = TrendAnalysisInput
    
    def _run(
        self, 
        time_period_days: int = 30,
        disease_focus: str = "all"
    ) -> str:
        """
        Analyze disease trends over specified time period
        
        Args:
            time_period_days: Number of days to analyze
            disease_focus: Specific disease or 'all'
            
        Returns:
            Trend analysis report as JSON string
        """
        try:
            db_path = Path("precision_agronomist/disease_tracking.db")
            
            if not db_path.exists():
                return json.dumps({
                    "status": "no_data",
                    "message": "No historical data available yet. Run detection sessions to build trend history.",
                    "suggestion": "Continue monitoring to establish baseline data for trend analysis."
                })
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_period_days)
            
            # Get overall statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_detections,
                    COUNT(DISTINCT session_id) as total_sessions,
                    COUNT(DISTINCT image_path) as total_images,
                    COUNT(DISTINCT disease_class) as unique_diseases
                FROM detections
                WHERE timestamp >= ?
            """, (start_date.isoformat(),))
            
            overall_stats = cursor.fetchone()
            
            # Get disease frequency
            cursor.execute("""
                SELECT 
                    disease_class,
                    COUNT(*) as frequency,
                    AVG(confidence) as avg_confidence,
                    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_severity_count
                FROM detections
                WHERE timestamp >= ?
                GROUP BY disease_class
                ORDER BY frequency DESC
            """, (start_date.isoformat(),))
            
            disease_frequency = cursor.fetchall()
            
            # Get weekly trends
            cursor.execute("""
                SELECT 
                    date(timestamp) as detection_date,
                    COUNT(*) as daily_detections,
                    COUNT(DISTINCT disease_class) as diseases_per_day
                FROM detections
                WHERE timestamp >= ?
                GROUP BY date(timestamp)
                ORDER BY detection_date
            """, (start_date.isoformat(),))
            
            daily_trends = cursor.fetchall()
            
            # Get severity distribution
            cursor.execute("""
                SELECT 
                    severity,
                    COUNT(*) as count
                FROM detections
                WHERE timestamp >= ?
                GROUP BY severity
            """, (start_date.isoformat(),))
            
            severity_dist = cursor.fetchall()
            
            conn.close()
            
            # Analyze trends
            analysis = self._generate_trend_analysis(
                overall_stats,
                disease_frequency,
                daily_trends,
                severity_dist,
                time_period_days
            )
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Trend analysis failed: {str(e)}"
            })
    
    def _generate_trend_analysis(self, overall_stats, disease_freq, daily_trends, severity_dist, period):
        """Generate comprehensive trend analysis"""
        
        total_detections, total_sessions, total_images, unique_diseases = overall_stats
        
        # Calculate trends
        disease_list = [
            {
                "disease": row[0],
                "frequency": row[1],
                "avg_confidence": round(row[2], 3),
                "high_severity_count": row[3]
            }
            for row in disease_freq
        ]
        
        # Identify most concerning disease
        most_frequent = disease_list[0] if disease_list else None
        
        # Calculate detection rate trends
        if len(daily_trends) > 7:
            recent_week = daily_trends[-7:]
            previous_week = daily_trends[-14:-7] if len(daily_trends) >= 14 else daily_trends[:7]
            
            recent_avg = sum(row[1] for row in recent_week) / len(recent_week)
            previous_avg = sum(row[1] for row in previous_week) / len(previous_week) if previous_week else recent_avg
            
            trend_direction = "increasing" if recent_avg > previous_avg else "decreasing" if recent_avg < previous_avg else "stable"
            change_percent = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
        else:
            trend_direction = "insufficient_data"
            change_percent = 0
        
        # Generate insights
        insights = []
        
        if most_frequent and 'healthy' not in most_frequent['disease'].lower():
            insights.append(f"⚠️ {most_frequent['disease']} is the most frequently detected disease ({most_frequent['frequency']} times)")
        
        if trend_direction == "increasing":
            insights.append(f"📈 Disease detections are INCREASING by {abs(change_percent):.1f}% (requires attention)")
        elif trend_direction == "decreasing":
            insights.append(f"📉 Disease detections are DECREASING by {abs(change_percent):.1f}% (positive trend)")
        
        high_severity_total = sum(d['high_severity_count'] for d in disease_list)
        if high_severity_total > 0:
            insights.append(f"🚨 {high_severity_total} high-severity detections require immediate action")
        
        # Recommendations
        recommendations = []
        
        if trend_direction == "increasing":
            recommendations.append("Increase monitoring frequency")
            recommendations.append("Review and enhance preventive measures")
            recommendations.append("Consider targeted treatments for most common diseases")
        
        if high_severity_total > 0:
            recommendations.append("Prioritize treatment of high-severity cases")
            recommendations.append("Isolate affected areas to prevent spread")
        
        if total_sessions < 10:
            recommendations.append("Continue regular monitoring to establish reliable trends")
        
        return {
            "status": "success",
            "analysis_period": {
                "days": period,
                "total_sessions": total_sessions,
                "total_images_analyzed": total_images,
                "total_detections": total_detections
            },
            "disease_distribution": disease_list,
            "trend": {
                "direction": trend_direction,
                "change_percent": round(change_percent, 2),
                "description": f"Disease detection rate is {trend_direction}"
            },
            "severity_distribution": [
                {"severity": row[0], "count": row[1]}
                for row in severity_dist
            ],
            "insights": insights,
            "recommendations": recommendations,
            "most_concerning_disease": most_frequent['disease'] if most_frequent else "None",
            "data_quality": "good" if total_sessions >= 10 else "building_baseline"
        }

