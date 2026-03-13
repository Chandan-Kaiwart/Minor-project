"""
PQC ADVANCED V3.0 - UNIFIED ANALYZER
Integrates IoT-AI, Research, and Cloud Optimization modules.
"""
from typing import Dict, List, Any
import os
import sys

# Ensure current directory is in sys.path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ensure current directory is in sys.path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core modules
from crypto_detector import CryptoDetector
from quantum_analysis import QuantumVulnerabilityAnalyzer
from risk_scoring import RiskScorer
from pqc_recommendation import PQCRecommender

# Import new advanced modules
from pqc_iot_ai import AIModelProtector, IoTGatewaySecurity
from pqc_research import PQCResearchLab
from pqc_cloud_ai import CloudPQCOrchestrator, AIComplianceMonitor
from pqc_system_scanner import SystemPQCScanner

class AdvancedPQCManager:
    """Unified manager for PQC V3.0"""
    
    def __init__(self):
        # Tools from V2
        self.detector = CryptoDetector()
        self.vuln_analyzer = QuantumVulnerabilityAnalyzer()
        self.risk_scorer = RiskScorer()
        self.recommender = PQCRecommender()
        
        # Advanced V3 Modules
        self.model_protector = AIModelProtector()
        self.iot_security = IoTGatewaySecurity()
        self.research_lab = PQCResearchLab()
        self.cloud_orchestrator = CloudPQCOrchestrator()
        self.compliance_monitor = AIComplianceMonitor()
        
        # System Scanner
        self.system_scanner = SystemPQCScanner(self.detector, self.vuln_analyzer)

    def _is_code_like(self, content: str) -> bool:
        """Objectives check: Ensure the input is actually code (Objective 1)"""
        if not content or len(content.strip()) < 10: return False
        
        # Common code-specific markers (keywords and symbols)
        CODE_MARKERS = [
            '{', '}', '(', ')', ';', 'def ', 'function', 'import ', 
            'class ', 'var ', 'val ', 'public ', 'private ', 'return ',
            '#include', 'using ', 'package ', 'from ', 'struct ', 
            'func ', 'println', 'printf', 'const '
        ]
        
        # Check if at least 2 markers exist or if it has multiple lines with indentation
        found_markers = sum(1 for m in CODE_MARKERS if m in content)
        has_lines = len(content.splitlines()) > 5
        
        return found_markers >= 2 or (has_lines and '    ' in content)

    def full_advanced_audit(self, context: str) -> Dict:
        """Performs a comprehensive V3 audit with code validation"""
        if not self._is_code_like(context):
            return {
                'status': 'error',
                'message': "Invalid Input: This content is not a codebase. There is no point in analyzing non-code artifacts for PQC readiness. Please provide valid source code (Python, Java, C++, etc.) for audit."
            }

        findings = self.detector.detect_crypto({'path': 'input_code', 'name': 'input_code', 'content': context})
        
        # Decision: Cryptographic usage detected?
        if findings:
            vulns = []
            for f in findings:
                # Step: Check quantum vulnerability
                v = self.vuln_analyzer.analyze_vulnerability(f)
                if v: vulns.append(v)
            
            # Step: Calculate quantum risk score & Determine readiness level
            risk = self.risk_scorer.calculate_overall_risk(vulns, findings)
            return self._wrap_report(vulns, risk, 1)
        else:
            # "No" Path: Analyze context and provide guidance
            guidance = self._generate_future_proofing_guidance(context)
            return self._wrap_guidance_report(guidance)

    def _is_supported_extension(self, filename: str) -> bool:
        """Objectives check: Only read code-related files (Objective 1)"""
        # Define allowed extensions for industrial PQC audit
        CODE_EXTENSIONS = {'.py', '.js', '.c', '.cpp', '.java', '.go', '.ts', '.sh', '.rs', '.swift', '.kt', '.cs'}
        ext = os.path.splitext(filename)[1].lower()
        return ext in CODE_EXTENSIONS

    def scan_system_path(self, path: str) -> Dict:
        """Scans a file, folder, or zip following the readiness flowchart with validation"""
        if not os.path.exists(path):
            return {'status': 'error', 'message': f'Path not found: {path}'}

        results = []
        files_count = 0
        
        if os.path.isfile(path):
            if path.endswith('.zip'):
                report = self.system_scanner.scan_zip(path)
                results = report.get('vulnerabilities', [])
                files_count = report.get('files_scanned', 1)
            else:
                if not self._is_supported_extension(path):
                    return {
                        'status': 'error', 
                        'message': f"Invalid File Type: '{os.path.basename(path)}'. The PQCRA only scans source code and configuration files."
                    }
                results = self.system_scanner.scan_file(path)
                files_count = 1
        else:
            # For folders, we rely on the internal scanner to filter but we increment based on valid files
            report = self.system_scanner.scan_folder(path)
            results = report.get('vulnerabilities', [])
            files_count = report.get('files_scanned', 1)

        if files_count == 0:
            return {
                'status': 'error',
                'message': "No valid source code files found in the specified path. Please provide a directory containing supported languages (Python, Java, C++, Js, etc.)"
            }

        # Decision: Cryptographic usage detected?
        if results:
            risk = self.risk_scorer.calculate_overall_risk(results, results) 
            return self._wrap_report(results, risk, files_count)
        else:
            # "No" Path: System-wide guidance
            return self._wrap_guidance_report({
                'context': f"System Scan: {files_count} files analyzed. No legacy crypto detected.",
                'recommendation': "Implementation of Post-Quantum-Aware Architecture recommended for new modules.",
                'next_steps': ["Deploy AES-256 for data-at-rest", "Plan for ML-KEM integration in API layers"]
            }, files_count)

    def _generate_future_proofing_guidance(self, context: str) -> Dict:
        """Provides guidance when no crypto is detected (Flowchart 'No' path)"""
        return {
            'context': "Clean codebase (no vulnerable crypto found).",
            'security_requirements': ["Confidentiality", "Integrity", "Future-Proofing"],
            'recommendation': "Design your application with 'Crypto-Agility'. Use parameters that support PQC standards.",
            'pqc_aware_guidance': "Adopt AES-256 and SHA-384 immediately to resist Grover's algorithm speedup."
        }

    def _wrap_guidance_report(self, guidance: Dict, files: int = 1) -> Dict:
        """Wraps guidance for codebases without existing crypto"""
        return {
            'status': 'success',
            'version': '3.1 - INDUSTRIAL (GUIDANCE MODE)',
            'base_report': {
                'risk_level': 'LOW',
                'risk_score': 0,
                'vulnerabilities_found': 0,
                'files_processed': files,
                'readiness_percentage': 100.0
            },
            'guidance_mode': True,
            'structured_assessment': {
                'cybersecurity_impact': {
                    'confidentiality_impact': "SECURE",
                    'integrity_impact': "SECURE",
                    'financial_risk': "LOW",
                    'quantum_readiness': "100/100"
                },
                'mitigation_roadmap': [{
                    'challenge': "No PQC strategy in place for future expansion",
                    'strategy': "Forward-Defense planning",
                    'solution': guidance.get('pqc_aware_guidance', "Implement AES-256/Kyber-Hybrid")
                }],
                'recommendation': guidance['recommendation']
            },
            'vulnerable_implementations': [],
            'summary': guidance['context']
        }

    def _wrap_report(self, vulns: List, risk: Dict, files: int) -> Dict:
        """Wraps all scan data into the industrial V3.1 format"""
        # Generate structured assessment sections based on user objectives
        impact_assessment = self._generate_impact_assessment(vulns, risk)
        mitigation_strategies = self._generate_mitigation_strategies(vulns)
        
        research = self.research_lab.evaluate_existing_schemes()
        ai_iot = self.model_protector.secure_model_weights({'name': 'ScanTarget', 'size_mb': files * 2})
        cloud = self.cloud_orchestrator.optimize_vault_security('AWS', 'Critical')
        
        return {
            'status': 'success',
            'version': '3.1 - INDUSTRIAL',
            'base_report': {
                'risk_level': risk['overall_level'],
                'risk_score': risk['overall_score'],
                'vulnerabilities_found': len(vulns),
                'files_processed': files,
                'readiness_percentage': risk['readiness_percentage']
            },
            'structured_assessment': {
                'cybersecurity_impact': impact_assessment,
                'mitigation_roadmap': mitigation_strategies,
                'priority_actions': risk.get('priority_actions', []),
                'recommendation': risk.get('recommendation', '')
            },
            'advanced_modules': {
                'research_benchmarks': research,
                'ai_iot_protection': ai_iot,
                'cloud_optimization': cloud
            },
            'vulnerable_implementations': self._enrich_vulns(vulns[:15]), 
            'summary': f"V3.1 Industrial Audit complete. {len(vulns)} issues identified across {files} file(s)."
        }

    def _enrich_vulns(self, vulns: List) -> List:
        """Enriches vulnerabilities with Objective-specific insights"""
        enriched = []
        for v in vulns:
            # Objective 2 & 3: Identification & Assessment
            algo = v['algorithm']
            threat = v.get('quantum_threat', 'Shor\'s Algorithm')
            
            # Objective 5: PQC Alternatives
            pqc_alt = "ML-KEM (Kyber)" if algo in ['RSA', 'ECC', 'DH'] else "AES-256 (Grover-Resistant)"
            if "SHA" in algo: pqc_alt = "SHA-512 / SHA3-512"

            v['objective_metadata'] = {
                'what_is_it': f"Detected {algo} ({v.get('key_size', 'standard')} bit) in {v['file_name']}",
                'how_vulnerable': f"Vulnerable to {threat}. Quantum computers can solve the underlying math in polynomial time.",
                'prevention': f"Migrate to {pqc_alt}. This provides lattice-level resistance against quantum search and factoring."
            }
            enriched.append(v)
        return enriched

    def _generate_impact_assessment(self, vulns: List, risk: Dict) -> Dict:
        """Generates a structured impact assessment based on identified vulnerabilities"""
        critical_vulns = [v for v in vulns if v.get('risk_level') == 'CRITICAL']
        
        return {
            'confidentiality_impact': "HIGH - Data can be harvested now and decrypted later by quantum computers" if critical_vulns else "MODERATE",
            'integrity_impact': "HIGH - Quantum computers can forge signatures (Shor's Algorithm)" if "Shor" in str(vulns) else "LOW",
            'availability_impact': "LOW - Quantum threats primarily target confidentiality and authentication",
            'financial_risk': "SIGNIFICANT" if risk['overall_level'] in ['CRITICAL', 'HIGH'] else "CONTROLLED",
            'quantum_readiness': f"{risk['readiness_percentage']}/100"
        }

    def _generate_mitigation_strategies(self, vulns: List) -> List[Dict]:
        """Provides specific mitigation strategies for identified issues"""
        strategies = []
        algorithms = set(v['algorithm'] for v in vulns)
        
        if any(a in ['RSA', 'ECC', 'DH'] for a in algorithms):
            strategies.append({
                'challenge': "Asymmetric cryptography broken by Shor's Algorithm",
                'strategy': "Migrate to NIST-standardized Lattice-based Cryptography",
                'solution': "Implement ML-KEM (Kyber) for encapsulation and ML-DSA (Dilithium) for signatures"
            })
            
        if any(a in ['AES'] for a in algorithms):
            strategies.append({
                'challenge': "Symmetric key length vulnerability (Grover's Algorithm)",
                'strategy': "Upgrade to AES-256 for 128-bit quantum security",
                'solution': "Double existing key sizes to maintain current security levels"
            })
            
        if not strategies:
            strategies.append({
                'challenge': "Maintaining long-term security in a post-quantum world",
                'strategy': "Implement Crypto-Agility Framework",
                'solution': "Ensure applications can swap cryptographic primitives without code changes"
            })
            
        return strategies

if __name__ == "__main__":
    manager = AdvancedPQCManager()
    sample_code = "from cryptography.hazmat.primitives.asymmetric import rsa\nkey = rsa.generate_private_key(65537, 2048)"
    report = manager.full_advanced_audit(sample_code)
    print("\n" + "="*50)
    print("      PQC ADVANCED V3.0 ANALYZER")
    print("="*50)
    print(f"Status: {report['status']}")
    print(f"Version: {report['version']}")
    print(f"Base Risk: {report['base_report']['risk_level']}")
    print("-" * 50)
    print("AI-IoT OPTIMIZATION:")
    print(f"  > Target PQC: {report['advanced_modules']['ai_iot_protection']['signature_algorithm']}")
    print("RESEARCH RANKING:")
    print(f"  > Top Scheme: {report['advanced_modules']['research_benchmarks']['rankings'][0]['name']}")
    print("CLOUD STRATEGY:")
    print(f"  > AWS Policy: {report['advanced_modules']['cloud_optimization']['ai_optimized_algo']}")
    print("="*50 + "\n")
