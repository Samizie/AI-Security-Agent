import streamlit as st
import json
from typing import Dict, Any
from datetime import datetime
import pandas as pd
import time


from core import SecurityOrchestrator



# Streamlit UI
def main():
    st.set_page_config(
        page_title="CodiSkout",
        page_icon="🤖",
        layout="wide"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .agent-card {
        background-color: #000000;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #000000;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    .risk-critical { border-left-color: #dc3545; }
    .risk-high { border-left-color: #fd7e14; }
    .risk-medium { border-left-color: #ffc107; }
    .risk-low { border-left-color: #28a745; }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🤖 CodiSkout")
    st.markdown("**Intelligent AI agents working together to secure your codebase**")
    
    # Agent Status Dashboard
    st.markdown("### 🎯 Agent Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="agent-card">
            <h4>Repo Cloner</h4>
            <p>Clones repositories and analyzes structure</p>
            <span style="color: green;">●</span> Ready
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="agent-card">
            <h4>Security Analyst</h4>
            <p>Scans for vulnerabilities and security issues</p>
            <span style="color: green;">●</span> Ready
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="agent-card">
            <h4>Code Reviewer</h4>
            <p>Reviews code quality and best practices</p>
            <span style="color: green;">●</span> Ready
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="agent-card">
            <h4>Report Generator</h4>
            <p>Collates and formats comprehensive reports</p>
            <span style="color: green;">●</span> Ready
        </div>
        """, unsafe_allow_html=True)
    
    # Configuration
    st.markdown("### ⚙️ Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        api_key = st.text_input("Groq API Key", type="password", help="Enter your Groq API key")
        repo_url = st.text_input("GitHub Repository URL", 
                                placeholder="https://github.com/username/repository",
                                help="Enter the GitHub repository URL to analyze")
    
    with col2:
        st.markdown("#### Analysis Options")
        deep_analysis = st.checkbox("Deep Analysis", value=True, help="Perform comprehensive analysis")
        include_deps = st.checkbox("Include Dependencies", value=True, help="Analyze dependency vulnerabilities")
        
    if not api_key:
        st.warning("⚠️ Please enter your Groq API key to continue.")
        st.info("You can get a free API key from [Groq Console](https://console.groq.com/)")
        st.stop()
    
    # Analysis Button
    if st.button("🚀 Start Multi-Agent Analysis", type="primary", use_container_width=True):
        if not repo_url:
            st.error("❌ Please enter a GitHub repository URL")
            return
        
        # Initialize orchestrator
        orchestrator = SecurityOrchestrator(api_key)
        
        # Progress tracking
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🔄 Analysis Progress")
            
            # Create progress bars for each agent
            cloner_progress = st.progress(0)
            cloner_status = st.empty()
            
            security_progress = st.progress(0)
            security_status = st.empty()
            
            review_progress = st.progress(0)
            review_status = st.empty()
            
            report_progress = st.progress(0)
            report_status = st.empty()
            
            # Start analysis
            cloner_status.text("🔄 Repo Cloner: Initializing...")
            cloner_progress.progress(10)
            
            
            try:
                # Run orchestrated analysis
                #cloner_status.text("🔄 Repo Cloner: Cloning repository...")
                cloner_progress.progress(50)
                with st.spinner("🔄 Repo Cloner: Cloning repository..."):
                    time.sleep(1.0)
                
                security_status.text("🔒 Security Analyst: Standby...")
                review_status.text("📝 Code Reviewer: Standby...")
                report_status.text("📊 Reporter: Standby...")
                
                # Execute analysis
                result = orchestrator.orchestrate_analysis(repo_url)
                
                if result['success']:
                    # Update progress
                    cloner_status.text("✅ Repo Cloner: Repository cloned")
                    cloner_progress.progress(100)
                    
                    #security_status.text("🔒 Security Analyst: Running security analysis...")
                    security_progress.progress(50)
                    with st.spinner("🔒 Security Analyst: Running security analysis..."):
                        time.sleep(3.0)
                    
                    security_status.text("✅ Security Analyst: Security analysis completed")
                    security_progress.progress(100)
                    
                    #review_status.text("📝 Code Reviewer: Reviewing code quality...")
                    review_progress.progress(50)
                    with st.spinner("📝 Code Reviewer: Reviewing code quality..."):
                        time.sleep(2.0)
                    
                    review_status.text("✅ Code Reviewer: Code review completed")
                    review_progress.progress(100)
                    
                    #report_status.text("📊 Reporter: Generating comprehensive report...")
                    report_progress.progress(50)
                    with st.spinner("📊 Reporter: Generating comprehensive report..."):
                        time.sleep(1.0)
                    
                    report_status.text("✅ Reporter: Report generated successfully")
                    report_progress.progress(100)
                    
                    # Display results
                    st.success("Analysis completed successfully")
                    display_analysis_results(result['results'])
                    
                else:
                    st.error(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ An error occurred during analysis: {str(e)}")

def display_analysis_results(results: Dict[str, Any]):
    """Display the analysis results in a structured format"""
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Get the final report
    report_data = results['report']['report'] if results['report']['success'] else None
    print(report_data)
    
    if not report_data:
        st.error("❌ Unable to generate comprehensive report")
        return
    
    # Executive Summary
    st.markdown("### 📋 Executive Summary")
    
    summary = report_data['executive_summary']
    repo_overview = report_data['repository_overview']
    languages_detected = summary.get('languages_detected') or repo_overview.get('structure', {}).get('languages', [])
    
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_level = summary['overall_risk_level']
        risk_color = {
            'CRITICAL': 'red',
            'HIGH': 'orange',
            'MEDIUM': 'yellow',
            'LOW': 'green'
        }.get(risk_level, 'gray')
        
        st.markdown(f"""
        <div class="metric-card risk-{risk_level.lower()}">
            <h4>Risk Level</h4>
            <h2 style="color: {risk_color};">{risk_level}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        quality_score = summary['code_quality_score']
        quality_color = 'green' if quality_score >= 7 else 'orange' if quality_score >= 5 else 'red'
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>Code Quality</h4>
            <h2 style="color: {quality_color};">{quality_score}/10</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Files Analyzed</h4>
            <h2>{summary['total_files_analyzed']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Languages</h4>
            <h2>{len(languages_detected)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Critical Findings
    if summary['critical_findings']:
        st.markdown("### 🚨 Critical Findings")
        for finding in summary['critical_findings']:
            st.error(f"⚠️ {finding}")
    
    # Security Analysis Results
    st.markdown("### 🔒 Security Analysis")
    
    security_analysis = report_data['security_analysis']
    
    if security_analysis['status']:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🛡️ Security Vulnerabilities")
            if security_analysis['vulnerabilities']:
                for vuln in security_analysis['vulnerabilities']:
                    st.warning(f"🔍 {vuln}")
            else:
                st.success("✅ No major vulnerabilities detected")
        
        with col2:
            st.markdown("#### 💡 Security Recommendations")
            if security_analysis['recommendations']:
                for rec in security_analysis['recommendations']:
                    st.info(f"💡 {rec}")
            else:
                st.success("✅ No specific security recommendations")
    else:
        st.error("❌ Security analysis failed")
    
    # Code Review Results
    st.markdown("### 📝 Code Review")
    
    code_review = report_data['code_review']
    
    if code_review['status']:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 Best Practices Violations")
            if code_review['best_practices_violations']:
                for violation in code_review['best_practices_violations']:
                    st.warning(f"📋 {violation}")
            else:
                st.success("✅ No major best practice violations found")
        
        with col2:
            st.markdown("#### 🏗️ Architecture Recommendations")
            if code_review['architecture_recommendations']:
                for rec in code_review['architecture_recommendations']:
                    st.info(f"🏗️ {rec}")
            else:
                st.success("✅ Architecture looks good")
    else:
        st.error("❌ Code review failed")
    
    # Repository Overview
    st.markdown("### 📁 Repository Overview")
    
    repo_overview = report_data['repository_overview']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌐 Programming Languages")
        languages = repo_overview.get('structure', {}).get('languages', [])
        if languages:
            for lang in languages:
                st.code(lang)
        else:
            st.info("No programming languages detected")
    
    with col2:
        st.markdown("#### 🔗 API Endpoints")
        if repo_overview['endpoints']:
            endpoint_df = pd.DataFrame(repo_overview['endpoints'])
            st.dataframe(endpoint_df, use_container_width=True)
        else:
            st.info("No API endpoints found")
    
    # Actionable Recommendations
    st.markdown("### 🎯 Actionable Recommendations")
    
    recommendations = report_data['actionable_recommendations']
    
    if recommendations:
        for rec in recommendations:
            priority_color = {
                'HIGH': 'red',
                'MEDIUM': 'orange',
                'LOW': 'green'
            }.get(rec['priority'], 'blue')
            
            st.markdown(f"""
            <div style="border-left: 4px solid {priority_color}; padding-left: 15px; margin: 10px 0;">
                <strong>{rec['category']} - {rec['priority']} Priority</strong><br>
                {rec['action']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No specific recommendations at this time")
    
    # Priority Matrix
    st.markdown("### ⏰ Priority Matrix")
    
    priority_matrix = report_data['priority_matrix']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🔥 Immediate Action")
        for item in priority_matrix['immediate_action']:
            st.error(f"🔥 {item}")
    
    with col2:
        st.markdown("#### ⚡ Short Term")
        for item in priority_matrix['short_term']:
            st.warning(f"⚡ {item}")
    
    with col3:
        st.markdown("#### 📅 Long Term")
        for item in priority_matrix['long_term']:
            st.info(f"📅 {item}")
    
    # Download Report
    st.markdown("### 📥 Download Report")
    
    report_json = json.dumps(report_data, indent=2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📄 Download JSON Report",
            data=report_json,
            file_name=f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Generate summary text
        summary_text = generate_summary_text(report_data)
        st.download_button(
            label="📝 Download Summary Report",
            data=summary_text,
            file_name=f"security_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

def generate_summary_text(report_data: Dict[str, Any]) -> str:
    """Generate a text summary of the report"""

    all_langs = set(report_data.get('executive_summary', {}).get('languages_detected', [])) | \
            set(report_data.get('repository_overview', {}).get('languages', []))
    
    summary = f"""
MULTI-AGENT SECURITY ANALYSIS REPORT
=====================================

Repository: {report_data['metadata']['repository']}
Generated: {report_data['metadata']['generated_at']}

EXECUTIVE SUMMARY
-----------------
Risk Level: {report_data['executive_summary']['overall_risk_level']}
Code Quality Score: {report_data['executive_summary']['code_quality_score']}/10
Files Analyzed: {report_data['executive_summary']['total_files_analyzed']}
Languages: {', '.join(sorted(all_langs))}

CRITICAL FINDINGS
-----------------
"""
    
    for finding in report_data['executive_summary']['critical_findings']:
        summary += f"• {finding}\n"
    
    summary += f"""
SECURITY ANALYSIS
-----------------
Status: {'✅ Completed' if report_data['security_analysis']['status'] else '❌ Failed'}
Risk Level: {report_data['security_analysis']['risk_level']}
Confidence: {report_data['security_analysis']['confidence_score']:.1%}

Vulnerabilities Found:
"""
    
    for vuln in report_data['security_analysis']['vulnerabilities']:
        summary += f"• {vuln}\n"
    
    summary += f"""
CODE REVIEW
-----------
Status: {'✅ Completed' if report_data['code_review']['status'] else '❌ Failed'}
Maintainability Score: {report_data['code_review']['maintainability_score']}/10

Best Practices Violations:
"""
    
    for violation in report_data['code_review']['best_practices_violations']:
        summary += f"• {violation}\n"
    
    summary += f"""
PRIORITY ACTIONS
----------------
Immediate Action Required:
"""
    
    for item in report_data['priority_matrix']['immediate_action']:
        summary += f"• {item}\n"
    
    summary += f"""
Short Term Actions:
"""
    
    for item in report_data['priority_matrix']['short_term']:
        summary += f"• {item}\n"
    
    return summary

if __name__ == "__main__":
    main()