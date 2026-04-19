"""
Cryptographic Algorithm Detector
Identifies cryptographic algorithms in source code and configuration files
References: RSA, ECC, AES, SHA, DES, 3DES, DSA, DH, etc.
"""

import re
from typing import List, Dict, Any, Optional


class CryptoDetector:
    """Detects cryptographic algorithm usage in files"""
    
    # Cryptographic algorithm patterns and their quantum vulnerability
    CRYPTO_PATTERNS = {
        # AI & Machine Learning Architectures (PS-2: AI-IoT Security)
        'AI_SECURITY': {
            'patterns': [
                r'\bLSTM\b',
                r'\bRNN\b',
                r'\bCNN\b',
                r'\bGRU\b',
                r'\bDense\b',
                r'\bConv2D\b',
                r'Keras',
                r'TensorFlow',
                r'PyTorch',
                r'scikit-learn',
                r'model\.predict',
                r'activation=',
                r'optimizer='
            ],
            'quantum_vulnerable': False,
            'attack': 'None (Integrity Shielding Required)',
            'category': 'ai_pqc_integration'
        },

        # Post-Quantum Cryptography (Quantum-Resistant)
        'ML-KEM': {
            'patterns': [r'ML-KEM', r'Kyber'],
            'quantum_vulnerable': False,
            'attack': 'None: Post-Quantum Secure',
            'category': 'pqc_kem'
        },
        'ML-DSA': {
            'patterns': [r'ML-DSA', r'Dilithium'],
            'quantum_vulnerable': False,
            'attack': 'None: Post-Quantum Secure',
            'category': 'pqc_signature'
        },
        'SLH-DSA': {
            'patterns': [r'SLH-DSA', r'SPHINCS\+'],
            'quantum_vulnerable': False,
            'attack': 'Quantum Resistant (Hash-based)',
            'category': 'pqc_signature'
        },
        
        # Public Key Cryptography (Quantum-vulnerable)
        'RSA': {
            'patterns': [
                r'\bRSA\b',
                r'RSAPublicKey',
                r'RSAPrivateKey',
                r'RSA_PKCS1',
                r'rsa_sign',
                r'rsa_encrypt',
                r'RSA/ECB',
                r'RSAES',
                r'RSASSA',
                r'RSAEngine'
            ],
            'quantum_vulnerable': True,
            'attack': 'Shor\'s Algorithm',
            'category': 'asymmetric'
        },
        'ECC': {
            'patterns': [
                r'\bECC\b',
                r'\bECDSA\b',
                r'\bECDH\b',
                r'EllipticCurve',
                r'secp256r1',
                r'secp384r1',
                r'secp521r1',
                r'prime256v1',
                r'P-256',
                r'P-384',
                r'P-521',
                r'ed25519',
                r'curve25519',
                r'ECPublicKey',
                r'ECPrivateKey'
            ],
            'quantum_vulnerable': True,
            'attack': 'Shor\'s Algorithm',
            'category': 'asymmetric'
        },
        'DSA': {
            'patterns': [
                r'(?<!ML-)\bDSA\b',
                r'DSAPublicKey',
                r'DSAPrivateKey',
                r'DSS\b',
                r'Digital Signature Algorithm'
            ],
            'quantum_vulnerable': True,
            'attack': 'Shor\'s Algorithm',
            'category': 'asymmetric'
        },
        'DH': {
            'patterns': [
                r'\bDiffie[-\s]?Hellman\b',
                r'\bDHE\b',
                r'\bECDHE\b',
                r'DHParameters',
                r'DH_compute_key'
            ],
            'quantum_vulnerable': True,
            'attack': 'Shor\'s Algorithm',
            'category': 'key_exchange'
        },
        
        # Symmetric Cryptography (Moderately vulnerable to Grover's)
        'AES': {
            'patterns': [
                r'\bAES\b',
                r'AES[-_]?128',
                r'AES[-_]?192',
                r'AES[-_]?256',
                r'AES/CBC',
                r'AES/GCM',
                r'AES/CTR',
                r'AES/ECB',
                r'Rijndael'
            ],
            'quantum_vulnerable': False,  # Managed by Grover's Resistance
            'attack': 'Grover\'s Algorithm (Quadratic speedup; safe with 256-bit keys)',
            'category': 'symmetric'
        },
        'DES': {
            'patterns': [
                r'\bDES\b',
                r'3DES',
                r'TripleDES',
                r'DES3',
                r'DES/CBC',
                r'DESede'
            ],
            'quantum_vulnerable': True,  # Already weak
            'attack': 'Grover\'s Algorithm (already broken)',
            'category': 'symmetric'
        },
        'ChaCha20': {
            'patterns': [
                r'ChaCha20',
                r'ChaCha20-Poly1305'
            ],
            'quantum_vulnerable': False,
            'attack': 'Grover\'s Algorithm (requires larger keys)',
            'category': 'symmetric'
        },
        
        # Hash Functions
        'SHA-1': {
            'patterns': [
                r'\bSHA1\b',
                r'\bSHA-1\b',
                r'sha1',
                r'SHA1Digest'
            ],
            'quantum_vulnerable': True,  # Already weak
            'attack': 'Grover\'s Algorithm (already broken)',
            'category': 'hash'
        },
        'SHA-2': {
            'patterns': [
                r'SHA[-_]?256',
                r'SHA[-_]?384',
                r'SHA[-_]?512',
                r'SHA2',
                r'SHA-2'
            ],
            'quantum_vulnerable': False,  # Needs larger output
            'attack': 'Grover\'s Algorithm (requires larger output)',
            'category': 'hash'
        },
        'SHA-3': {
            'patterns': [
                r'SHA3',
                r'SHA-3',
                r'Keccak'
            ],
            'quantum_vulnerable': False,
            'attack': 'Grover\'s Algorithm (quantum-resistant)',
            'category': 'hash'
        },
        'MD5': {
            'patterns': [
                r'\bMD5\b',
                r'md5'
            ],
            'quantum_vulnerable': True,  # Already broken
            'attack': 'Already broken (pre-quantum)',
            'category': 'hash'
        }
    }
    
    # Key size patterns
    KEY_SIZE_PATTERN = r'(?:key[_\s]?size|keysize|bits?)[:\s=]+(\d+)'
    
    def __init__(self):
        self.findings: List[Dict[str, Any]] = []
    
    def detect_crypto(self, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect cryptographic algorithms in a file
        """
        findings = []
        content = file_info.get('content')
        
        if not content:
            return findings
        
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8', errors='ignore')
            except Exception:
                return findings
        
        for algo_name, algo_info in self.CRYPTO_PATTERNS.items():
            for pattern in algo_info['patterns']:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end]
                    
                    key_size = self._extract_key_size(context)
                    line_number = content[:match.start()].count('\n') + 1
                    
                    finding = {
                        'algorithm': algo_name,
                        'file': file_info['path'],
                        'file_name': file_info['name'],
                        'file_type': file_info.get('file_type', 'source_code'),
                        'line': line_number,
                        'matched_text': match.group(),
                        'context': context.strip(),
                        'quantum_vulnerable': algo_info['quantum_vulnerable'],
                        'attack_vector': algo_info['attack'],
                        'category': algo_info['category'],
                        'key_size': key_size
                    }
                    
                    findings.append(finding)
        
        findings = self._deduplicate_findings(findings)
        return findings
    
    def _extract_key_size(self, context: str) -> Optional[int]:
        """Extract key size from context"""
        match = re.search(self.KEY_SIZE_PATTERN, context, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except Exception:
                pass
        
        common_sizes = [1024, 2048, 3072, 4096, 128, 192, 256, 384, 512]
        for size in common_sizes:
            if str(size) in context:
                return size
        
        return None
    
    def _deduplicate_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate findings from the same location"""
        seen = set()
        unique_findings = []
        
        for finding in findings:
            key = (
                finding['algorithm'],
                finding['file'],
                finding['line'] // 5
            )
            
            if key not in seen:
                seen.add(key)
                unique_findings.append(finding)
        
        return unique_findings
    
    def get_statistics(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics from findings with type safety"""
        total_vuln = 0
        by_algo: Dict[str, int] = {}
        by_cat: Dict[str, int] = {}
        by_type: Dict[str, int] = {}
        
        for f in findings:
            algo = str(f['algorithm'])
            category = str(f['category'])
            file_type = str(f.get('file_type', 'source_code'))
            
            if f['quantum_vulnerable']:
                total_vuln += 1
            
            by_algo[algo] = by_algo.get(algo, 0) + 1
            by_cat[category] = by_cat.get(category, 0) + 1
            by_type[file_type] = by_type.get(file_type, 0) + 1
        
        return {
            'total_findings': len(findings),
            'vulnerable_count': total_vuln,
            'by_algorithm': by_algo,
            'by_category': by_cat,
            'by_file_type': by_type
        }