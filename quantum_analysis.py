"""
Quantum Vulnerability Analyzer
Analyzes cryptographic findings for quantum computing vulnerabilities
References: Shor's Algorithm, Grover's Algorithm
"""

from typing import Dict, Any, Optional
import math


class QuantumVulnerabilityAnalyzer:
    """
    Analyzes quantum vulnerabilities in cryptographic systems
    
    References:
    - Shor's Algorithm: Breaks RSA, ECC, DH in polynomial time
    - Grover's Algorithm: Provides quadratic speedup for symmetric crypto
    """
    
    # Quantum algorithm impacts
    QUANTUM_THREATS = {
        'Shor\'s Algorithm': {
            'description': 'Polynomial-time algorithm for integer factorization and discrete logarithms',
            'impact': 'Breaks RSA, ECC, DSA, and Diffie-Hellman completely',
            'timeline': 'Threat becomes real when sufficiently large quantum computers exist (2030-2040)',
            'affected_algorithms': ['RSA', 'ECC', 'DSA', 'DH']
        },
        'Grover\'s Algorithm': {
            'description': 'Quadratic speedup for unstructured search problems',
            'impact': 'Reduces effective key size by half for symmetric encryption and hash functions',
            'timeline': 'Requires mitigation by doubling key sizes',
            'affected_algorithms': ['AES', 'ChaCha20', 'SHA-2', 'SHA-3']
        }
    }
    
    # Security levels required to resist quantum attacks
    QUANTUM_SECURITY_LEVELS = {
        'asymmetric': {
            'RSA': {
                1024: 0,    # Completely broken
                2048: 0,    # Completely broken
                3072: 0,    # Completely broken
                4096: 0,    # Completely broken
                7680: 0,    # All RSA broken by Shor's
                15360: 0
            },
            'ECC': {
                160: 0,     # Completely broken
                192: 0,     # Completely broken
                224: 0,     # Completely broken
                256: 0,     # Completely broken
                384: 0,     # All ECC broken by Shor's
                521: 0
            }
        },
        'symmetric': {
            'AES': {
                128: 64,    # Equivalent to 64-bit classical security (Grover's)
                192: 96,    # Equivalent to 96-bit classical security
                256: 128    # Equivalent to 128-bit classical security (recommended)
            }
        },
        'hash': {
            'SHA-2': {
                256: 128,   # Output size halved by Grover's
                384: 192,
                512: 256
            }
        }
    }
    
    def __init__(self):
        pass
    
    def analyze_vulnerability(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze quantum vulnerability for a cryptographic finding
        
        Args:
            finding: Cryptographic finding from CryptoDetector
        
        Returns:
            Vulnerability analysis with risk assessment
        """
        algorithm = finding['algorithm']
        category = finding['category']
        key_size = finding.get('key_size')
        
        vulnerability = {
            'algorithm': algorithm,
            'category': category,
            'file': finding['file'],
            'file_name': finding['file_name'],
            'line': finding['line'],
            'context': finding.get('context', '')[:200],  # Truncate for report
            'quantum_vulnerable': finding.get('quantum_vulnerable', True),
            'key_size': key_size
        }
        
        # Determine primary quantum threat
        if algorithm in ['RSA', 'ECC', 'DSA', 'DH']:
            vulnerability['quantum_threat'] = 'Shor\'s Algorithm'
            vulnerability['threat_description'] = self.QUANTUM_THREATS['Shor\'s Algorithm']['description']
            vulnerability['impact'] = 'CRITICAL - Complete break of public key cryptography'
            vulnerability['effective_security'] = 0  # Completely broken
            vulnerability['risk_level'] = 'CRITICAL'
            
        elif algorithm in ['AES', 'ChaCha20']:
            vulnerability['quantum_threat'] = 'Grover\'s Algorithm'
            vulnerability['threat_description'] = self.QUANTUM_THREATS['Grover\'s Algorithm']['description']
            
            if key_size:
                effective_security = self._calculate_grover_security(key_size)
                vulnerability['effective_security'] = effective_security
                vulnerability['impact'] = f'Effective security reduced to {effective_security} bits'
                
                if effective_security < 112:
                    vulnerability['risk_level'] = 'HIGH'
                elif effective_security < 128:
                    vulnerability['risk_level'] = 'MEDIUM'
                else:
                    vulnerability['risk_level'] = 'LOW'
            else:
                vulnerability['effective_security'] = None
                vulnerability['impact'] = 'Key size halved by Grover\'s Algorithm'
                vulnerability['risk_level'] = 'MEDIUM'
        
        elif algorithm in ['SHA-1', 'MD5', 'DES']:
            vulnerability['quantum_threat'] = 'Already broken (pre-quantum)'
            vulnerability['impact'] = 'CRITICAL - Algorithm is cryptographically broken'
            vulnerability['risk_level'] = 'CRITICAL'
            vulnerability['effective_security'] = 0
        
        elif algorithm in ['SHA-2', 'SHA-3']:
            vulnerability['quantum_threat'] = 'Grover\'s Algorithm'
            vulnerability['impact'] = 'Output size should be doubled for quantum resistance'
            vulnerability['risk_level'] = 'MEDIUM'
        
        # Add contextual risk factors
        vulnerability['risk_factors'] = self._assess_risk_factors(finding)
        
        # Calculate composite risk score
        vulnerability['risk_score'] = self._calculate_risk_score(vulnerability)
        
        # Add mitigation urgency timeline
        vulnerability['mitigation_urgency'] = self._determine_urgency(vulnerability)
        
        return vulnerability
    
    def _calculate_grover_security(self, key_size: int) -> int:
        """
        Calculate effective security against Grover's Algorithm
        
        Grover's Algorithm provides quadratic speedup, so effective
        security is approximately key_size / 2
        """
        return key_size // 2
    
    def _assess_risk_factors(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Assess contextual risk factors"""
        risk_factors = {
            'data_sensitivity': 'UNKNOWN',
            'exposure': 'UNKNOWN',
            'longevity': 'UNKNOWN'
        }
        
        # Analyze context for risk indicators
        context_lower = finding.get('context', '').lower()
        
        # Data sensitivity indicators
        sensitivity_keywords = [
            'password', 'private', 'secret', 'confidential', 'key',
            'credential', 'token', 'auth', 'certificate', 'payment',
            'financial', 'medical', 'personal', 'sensitive'
        ]
        
        if any(keyword in context_lower for keyword in sensitivity_keywords):
            risk_factors['data_sensitivity'] = 'HIGH'
        else:
            risk_factors['data_sensitivity'] = 'MEDIUM'
        
        # Exposure analysis
        exposure_keywords = ['public', 'api', 'external', 'internet', 'web']
        if any(keyword in context_lower for keyword in exposure_keywords):
            risk_factors['exposure'] = 'HIGH'
        else:
            risk_factors['exposure'] = 'MEDIUM'
        
        # Data longevity (harvest now, decrypt later concern)
        longevity_keywords = ['archive', 'long-term', 'permanent', 'backup', 'storage']
        if any(keyword in context_lower for keyword in longevity_keywords):
            risk_factors['longevity'] = 'HIGH'
        else:
            risk_factors['longevity'] = 'MEDIUM'
        
        return risk_factors
    
    def _calculate_risk_score(self, vulnerability: Dict[str, Any]) -> float:
        """
        Calculate composite risk score (0-100)
        
        Factors:
        - Quantum vulnerability severity
        - Effective security level
        - Contextual risk factors
        """
        score = 0.0
        
        # Base score from vulnerability level
        risk_level = vulnerability.get('risk_level', 'MEDIUM')
        base_scores = {
            'CRITICAL': 85,
            'HIGH': 65,
            'MEDIUM': 40,
            'LOW': 20,
            'MINIMAL': 10
        }
        score = base_scores.get(risk_level, 50)
        
        # Adjust for effective security
        effective_security = vulnerability.get('effective_security')
        if effective_security is not None:
            if effective_security == 0:
                score = max(score, 90)
            elif effective_security < 80:
                score += 10
            elif effective_security < 112:
                score += 5
        
        # Adjust for risk factors
        risk_factors = vulnerability.get('risk_factors', {})
        
        if risk_factors.get('data_sensitivity') == 'HIGH':
            score += 10
        
        if risk_factors.get('exposure') == 'HIGH':
            score += 5
        
        if risk_factors.get('longevity') == 'HIGH':
            score += 10  # "Harvest now, decrypt later" concern
        
        return min(100.0, score)
    
    def _determine_urgency(self, vulnerability: Dict[str, Any]) -> str:
        """
        Determine migration urgency
        
        Categories:
        - IMMEDIATE: Critical vulnerabilities needing immediate attention
        - SHORT_TERM: 1-2 years
        - MEDIUM_TERM: 2-5 years
        - LONG_TERM: 5+ years
        """
        risk_score = vulnerability.get('risk_score', 50.0)
        risk_level = vulnerability.get('risk_level', 'MEDIUM')
        
        # Critical vulnerabilities or high risk scores
        if risk_level == 'CRITICAL' or risk_score >= 80:
            return 'IMMEDIATE (0-1 years)'
        
        # High risk - especially for long-lived data
        if risk_level == 'HIGH' or risk_score >= 60:
            if vulnerability.get('risk_factors', {}).get('longevity') == 'HIGH':
                return 'IMMEDIATE (harvest now, decrypt later threat)'
            return 'SHORT_TERM (1-3 years)'
        
        # Medium risk
        if risk_level == 'MEDIUM' or risk_score >= 40:
            return 'MEDIUM_TERM (3-5 years)'
        
        # Low risk
        return 'LONG_TERM (5+ years)'
    
    def get_quantum_threat_summary(self) -> Dict[str, Any]:
        """Get summary of quantum threats"""
        return {
            'shors_algorithm': self.QUANTUM_THREATS['Shor\'s Algorithm'],
            'grovers_algorithm': self.QUANTUM_THREATS['Grover\'s Algorithm'],
            'timeline': {
                'early_quantum': '2025-2030: Small quantum computers',
                'cryptographically_relevant': '2030-2035: Threat to 1024-bit RSA',
                'large_scale': '2035-2040: Threat to 2048-bit RSA and 256-bit ECC',
                'mature': '2040+: All classical public-key cryptography at risk'
            }
        }