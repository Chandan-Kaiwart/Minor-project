"""
Risk Scoring Module - Calculates overall quantum risk assessment
"""

from typing import List, Dict, Any


class RiskScorer:
    """Calculates comprehensive risk scores for cryptographic findings"""
    
    RISK_WEIGHTS = {
        'CRITICAL': 10.0,
        'HIGH': 7.0,
        'MEDIUM': 4.0,
        'LOW': 2.0,
        'MINIMAL': 1.0
    }
    
    def calculate_overall_risk(self, vulnerabilities: List[Dict], findings: List[Dict]) -> Dict[str, Any]:
        """
        Calculate overall risk assessment
        
        Args:
            vulnerabilities: List of vulnerability analysis results
            findings: List of crypto findings
            
        Returns:
            Comprehensive risk assessment dict
        """
        if not vulnerabilities:
            return {
                'overall_level': 'MINIMAL',
                'overall_score': 0.0,
                'critical_count': 0,
                'high_count': 0,
                'medium_count': 0,
                'low_count': 0,
                'total_vulnerabilities': 0,
                'readiness_percentage': 100.0,
                'recommendation': 'No quantum vulnerabilities detected'
            }
        
        # Count by level
        counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'MINIMAL': 0}
        scores = []
        
        for vuln in vulnerabilities:
            level = vuln.get('risk_level', 'MEDIUM')
            counts[level] = counts.get(level, 0) + 1
            scores.append(vuln.get('risk_score', 50.0))
        
        # Calculate overall score
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine overall level
        if counts['CRITICAL'] > 0:
            overall_level = 'CRITICAL'
        elif counts['HIGH'] > 0 or overall_score >= 65:
            overall_level = 'HIGH'
        elif counts['MEDIUM'] > 0 or overall_score >= 40:
            overall_level = 'MEDIUM'
        elif overall_score >= 20:
            overall_level = 'LOW'
        else:
            overall_level = 'MINIMAL'
        
        readiness = max(0.0, 100.0 - overall_score)
        
        # Generate priority actions
        priority_actions = self._get_priority_actions(vulnerabilities, counts)
        
        # Algorithm inventory
        algo_summary = {}
        for finding in findings:
            algo = finding.get('algorithm', 'Unknown')
            algo_summary[algo] = algo_summary.get(algo, 0) + 1
        
        return {
            'overall_level': overall_level,
            'overall_score': round(overall_score, 1),
            'critical_count': counts['CRITICAL'],
            'high_count': counts['HIGH'],
            'medium_count': counts['MEDIUM'],
            'low_count': counts['LOW'],
            'total_vulnerabilities': len(vulnerabilities),
            'readiness_percentage': round(readiness, 1),
            'priority_actions': priority_actions,
            'algorithm_inventory': algo_summary,
            'recommendation': self._get_recommendation(overall_level, counts)
        }
    
    def _get_priority_actions(self, vulnerabilities: List[Dict], counts: Dict) -> List[str]:
        """Generate prioritized action list"""
        actions = []
        
        if counts.get('CRITICAL', 0) > 0:
            actions.append(f"IMMEDIATE: Replace {counts['CRITICAL']} critical public-key implementations")
            actions.append("IMMEDIATE: Plan for 'harvest now, decrypt later' threat")
        
        if counts.get('HIGH', 0) > 0:
            actions.append(f"SHORT-TERM: Upgrade {counts['HIGH']} high-risk algorithms")
        
        if counts.get('MEDIUM', 0) > 0:
            actions.append(f"MEDIUM-TERM: Address {counts['MEDIUM']} medium-risk algorithms")
        
        actions.append("Evaluate NIST PQC standards: ML-KEM, ML-DSA, SLH-DSA")
        actions.append("Create crypto-agility policy for future migrations")
        
        return actions
    
    def _get_recommendation(self, level: str, counts: Dict) -> str:
        """Get overall recommendation message"""
        messages = {
            'CRITICAL': f"IMMEDIATE ACTION REQUIRED: {counts.get('CRITICAL', 0)} critical vulnerabilities. Migrate to NIST PQC now.",
            'HIGH': "HIGH PRIORITY: Begin PQC migration planning within 1-2 years.",
            'MEDIUM': "PLAN AHEAD: Start PQC assessment and migration roadmap.",
            'LOW': "MONITOR: Low risk. Plan long-term migration to PQC.",
            'MINIMAL': "SECURE: No significant quantum vulnerabilities detected."
        }
        return messages.get(level, "Review cryptographic implementations")