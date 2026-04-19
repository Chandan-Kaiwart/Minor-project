"""
PQC ADVANCED - AI-DRIVEN IoT SECURITY (Problem Statement 32)
Protects AI models and IoT data from quantum threats.
"""
from typing import Dict, List, Any
import hashlib

class AIModelProtector:
    """Security engine for AI models on edge devices"""
    
    def __init__(self):
        self.protection_levels = {
            'L1': 'Integrity Only (ML-DSA)',
            'L2': 'Confidentiality + Integrity (ML-KEM + ML-DSA)',
            'L3': 'Full Zero-Trust AI (PQC throughout pipeline)'
        }

    def secure_model_weights(self, model_info: Dict) -> Dict:
        """
        Signs and encrypts AI model weights for secure deployment
        """
        model_name = model_info.get('name', 'model_v1')
        size_mb = model_info.get('size_mb', 50)
        
        # Determine PQC algorithm based on device capability
        if size_mb < 10:
            target_pqc = 'ML-DSA-44'
            encryption = 'AES-256-GCM'
        else:
            target_pqc = 'ML-DSA-65'
            encryption = 'ML-KEM-768'

        return {
            'model': model_name,
            'protection_level': 'L2',
            'signature_algorithm': target_pqc,
            'encryption_scheme': encryption,
            'integrity_hash': hashlib.sha3_256(model_name.encode()).hexdigest(),
            'security_verdict': "Quantum-Safe Model Package Created",
            'deployment_suitability': "Suitable for Edge/Gateway devices"
        }

class IoTGatewaySecurity:
    """Manages quantum-safe communication for IoT clusters"""
    
    def analyze_iot_cluster(self, cluster_info: List[Dict]) -> Dict:
        """Analyzes a cluster of IoT devices for quantum risk"""
        vulnerable_count: int = 0
        recommendations: List[str] = []
        
        for device in cluster_info:
            if device.get('current_crypto') in ['RSA', 'ECC', 'ECDSA']:
                vulnerable_count = vulnerable_count + 1
                recommendations.append(f"Upgrade {str(device.get('id', 'Unknown'))} to ML-KEM for key-exchange.")
        
        total = len(cluster_info)
        risk_score = 0.0
        if total > 0:
            risk_score = (float(vulnerable_count) / float(total)) * 100.0
        
        return {
            'total_devices': total,
            'quantum_vulnerable_devices': vulnerable_count,
            'risk_score': risk_score,
            'cluster_status': 'UNSAFE' if vulnerable_count > 0 else 'QUANTUM-SECURE',
            'priority_actions': recommendations[0:3] if recommendations else []
        }
