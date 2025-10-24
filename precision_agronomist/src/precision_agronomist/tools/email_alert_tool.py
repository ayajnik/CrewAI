from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os


class EmailAlertInput(BaseModel):
    """Input schema for EmailAlert."""
    disease_summary: str = Field(..., description="Summary of detected diseases")
    severity_level: str = Field(..., description="Severity level: low, moderate, high, critical")
    num_detections: int = Field(..., description="Total number of disease detections")
    affected_images: int = Field(..., description="Number of images with diseases")


class EmailAlertTool(BaseTool):
    name: str = "Email Alert System"
    description: str = (
        "Sends email alerts to farmers/agronomists when high-severity plant diseases "
        "are detected. Only sends alerts for 'high' or 'critical' severity levels. "
        "Includes disease summary, affected image count, and urgency level."
    )
    args_schema: Type[BaseModel] = EmailAlertInput

    def _run(
        self, 
        disease_summary: str, 
        severity_level: str,
        num_detections: int,
        affected_images: int
    ) -> str:
        """
        Send email alert for high-severity disease detections
        
        Args:
            disease_summary: Summary of detected diseases
            severity_level: Severity (low, moderate, high, critical)
            num_detections: Total detections
            affected_images: Number of affected images
            
        Returns:
            Status message
        """
        try:
            # Only send alerts for high severity
            if severity_level.lower() not in ['high', 'critical']:
                return f"ℹ️ Severity level '{severity_level}' - No alert sent (only high/critical trigger alerts)"
            
            # Get email configuration from environment variables
            # In production, set these in your environment or .env file
            sender_email = os.getenv('ALERT_SENDER_EMAIL', 'precision.agronomist@example.com')
            sender_password = os.getenv('ALERT_SENDER_PASSWORD', '')
            recipient_email = os.getenv('FARMER_EMAIL', 'farmer@example.com')
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            
            # For demo purposes, if no credentials, just log the alert
            if not sender_password:
                alert_message = self._format_alert_message(
                    disease_summary, severity_level, num_detections, affected_images
                )
                print("\n" + "="*60)
                print("📧 EMAIL ALERT (Demo Mode - No credentials configured)")
                print("="*60)
                print(alert_message)
                print("="*60 + "\n")
                
                return (
                    f"✅ Alert generated for {severity_level} severity!\n"
                    f"📧 To: {recipient_email}\n"
                    f"📝 Detections: {num_detections} diseases in {affected_images} images\n"
                    f"⚙️ Configure ALERT_SENDER_EMAIL and ALERT_SENDER_PASSWORD environment variables to send real emails"
                )
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🚨 URGENT: {severity_level.upper()} Severity Plant Disease Alert"
            message["From"] = sender_email
            message["To"] = recipient_email
            
            # Create email body
            email_body = self._format_email_html(
                disease_summary, severity_level, num_detections, affected_images
            )
            
            html_part = MIMEText(email_body, "html")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.as_string())
            
            return (
                f"✅ Email alert sent successfully!\n"
                f"📧 To: {recipient_email}\n"
                f"🚨 Severity: {severity_level.upper()}\n"
                f"📝 {num_detections} diseases detected in {affected_images} images"
            )
            
        except Exception as e:
            return f"⚠️ Failed to send email alert: {str(e)}\n(Alert logged locally for manual review)"
    
    def _format_alert_message(self, disease_summary, severity_level, num_detections, affected_images):
        """Format alert message for console/log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""
🚨 PLANT DISEASE ALERT - {severity_level.upper()} SEVERITY

Timestamp: {timestamp}
Affected Images: {affected_images}
Total Detections: {num_detections}

Disease Summary:
{disease_summary}

⚠️ IMMEDIATE ACTION REQUIRED
This alert requires urgent attention to prevent crop loss.

Recommended Actions:
1. Inspect affected areas immediately
2. Isolate infected plants if possible
3. Apply appropriate treatments
4. Monitor spread closely

View full report: plant_disease_report.md
View annotated images: artifacts/yolo_detection/predictions/crew_results/
"""
    
    def _format_email_html(self, disease_summary, severity_level, num_detections, affected_images):
        """Format HTML email body"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        severity_color = "red" if severity_level.lower() == "critical" else "orange"
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: {severity_color}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .alert-box {{ background-color: #fff3cd; border-left: 4px solid {severity_color}; padding: 15px; margin: 20px 0; }}
        .stats {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .actions {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        ul {{ padding-left: 20px; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 PLANT DISEASE ALERT</h1>
        <h2>{severity_level.upper()} SEVERITY</h2>
    </div>
    
    <div class="content">
        <div class="alert-box">
            <strong>⚠️ Immediate Action Required</strong><br>
            High-severity plant diseases have been detected in your crops.
        </div>
        
        <div class="stats">
            <h3>Detection Summary</h3>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <p><strong>Affected Images:</strong> {affected_images}</p>
            <p><strong>Total Detections:</strong> {num_detections}</p>
            <hr>
            <p><strong>Diseases Found:</strong></p>
            <p>{disease_summary}</p>
        </div>
        
        <div class="actions">
            <h3>🎯 Recommended Actions</h3>
            <ul>
                <li>Inspect affected areas immediately</li>
                <li>Isolate infected plants if possible</li>
                <li>Apply appropriate fungicides or treatments</li>
                <li>Monitor disease spread closely over next 48-72 hours</li>
                <li>Consider consulting with a plant pathologist</li>
            </ul>
        </div>
        
        <p><strong>📊 Full Report:</strong> Check plant_disease_report.md for detailed analysis</p>
        <p><strong>🖼️ Visual Evidence:</strong> Review annotated images in predictions folder</p>
    </div>
    
    <div class="footer">
        <p>Precision Agronomist AI System</p>
        <p>Automated Plant Disease Detection & Monitoring</p>
    </div>
</body>
</html>
"""

