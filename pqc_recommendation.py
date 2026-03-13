"""
Post-Quantum Cryptography Recommendation Engine
Recommends NIST-approved PQC algorithms for migration

NIST PQC Standards (2024):
- ML-KEM (Module-Lattice-Based Key Encapsulation Mechanism) - formerly CRYSTALS-KYBER
- ML-DSA (Module-Lattice-Based Digital Signature Algorithm) - formerly CRYSTALS-DILITHIUM
- SLH-DSA (Stateless Hash-Based Digital Signature Algorithm) - formerly SPHINCS+
- Classic McEliece (Code-Based KEM) - Additional standard
"""

from typing import Dict, Any, List


class PQCRecommender:
    """Recommends post-quantum cryptography alternatives"""
    
    # NIST Post-Quantum Cryptography Standards
    NIST_PQC_STANDARDS = {
        'ML-KEM': {
            'full_name': 'Module-Lattice-Based Key Encapsulation Mechanism',
            'former_name': 'CRYSTALS-KYBER',
            'type': 'Key Encapsulation',
            'basis': 'Lattice-based (Module-LWE)',
            'variants': {
                'ML-KEM-512': {
                    'security_level': 'NIST Level 1 (equivalent to AES-128)',
                    'public_key_size': '800 bytes',
                    'ciphertext_size': '768 bytes',
                    'use_case': 'Standard applications'
                },
                'ML-KEM-768': {
                    'security_level': 'NIST Level 3 (equivalent to AES-192)',
                    'public_key_size': '1184 bytes',
                    'ciphertext_size': '1088 bytes',
                    'use_case': 'Recommended for most applications'
                },
                'ML-KEM-1024': {
                    'security_level': 'NIST Level 5 (equivalent to AES-256)',
                    'public_key_size': '1568 bytes',
                    'ciphertext_size': '1568 bytes',
                    'use_case': 'High-security applications'
                }
            },
            'advantages': [
                'Fast performance',
                'Small key sizes (relatively)',
                'Well-studied security',
                'Efficient implementation'
            ],
            'considerations': [
                'Relatively new (monitor for cryptanalysis)',
                'Larger keys than classical crypto'
            ],
            'replaces': ['RSA (encryption)', 'DH', 'ECDH'],
            'status': 'NIST FIPS 203 (2024)'
        },
        
        'ML-DSA': {
            'full_name': 'Module-Lattice-Based Digital Signature Algorithm',
            'former_name': 'CRYSTALS-DILITHIUM',
            'type': 'Digital Signature',
            'basis': 'Lattice-based (Module-LWE)',
            'variants': {
                'ML-DSA-44': {
                    'security_level': 'NIST Level 2',
                    'public_key_size': '1312 bytes',
                    'signature_size': '2420 bytes',
                    'use_case': 'Standard applications'
                },
                'ML-DSA-65': {
                    'security_level': 'NIST Level 3',
                    'public_key_size': '1952 bytes',
                    'signature_size': '3293 bytes',
                    'use_case': 'Recommended for most applications'
                },
                'ML-DSA-87': {
                    'security_level': 'NIST Level 5',
                    'public_key_size': '2592 bytes',
                    'signature_size': '4595 bytes',
                    'use_case': 'High-security applications'
                }
            },
            'advantages': [
                'Fast signature generation and verification',
                'Good balance of security and performance',
                'Relatively compact signatures'
            ],
            'considerations': [
                'Larger signatures than classical ECDSA',
                'Requires careful implementation'
            ],
            'replaces': ['RSA (signatures)', 'DSA', 'ECDSA'],
            'status': 'NIST FIPS 204 (2024)'
        },
        
        'SLH-DSA': {
            'full_name': 'Stateless Hash-Based Digital Signature Algorithm',
            'former_name': 'SPHINCS+',
            'type': 'Digital Signature',
            'basis': 'Hash-based',
            'variants': {
                'SLH-DSA-128s': {
                    'security_level': 'NIST Level 1 (small signature)',
                    'public_key_size': '32 bytes',
                    'signature_size': '7856 bytes',
                    'use_case': 'When smaller signatures acceptable'
                },
                'SLH-DSA-128f': {
                    'security_level': 'NIST Level 1 (fast)',
                    'public_key_size': '32 bytes',
                    'signature_size': '17088 bytes',
                    'use_case': 'When performance is priority'
                },
                'SLH-DSA-256s': {
                    'security_level': 'NIST Level 5 (small signature)',
                    'public_key_size': '64 bytes',
                    'signature_size': '29792 bytes',
                    'use_case': 'High security, smaller signatures'
                }
            },
            'advantages': [
                'Conservative security assumptions (hash functions)',
                'No known quantum attacks',
                'Small public keys',
                'Stateless (no state management required)'
            ],
            'considerations': [
                'Very large signature sizes',
                'Slower signing compared to ML-DSA',
                'Better suited as backup/hybrid option'
            ],
            'replaces': ['RSA (signatures)', 'DSA', 'ECDSA'],
            'status': 'NIST FIPS 205 (2024)'
        },
        
        'Classic McEliece': {
            'full_name': 'Classic McEliece',
            'former_name': None,
            'type': 'Key Encapsulation',
            'basis': 'Code-based (Goppa codes)',
            'variants': {
                'mceliece348864': {
                    'security_level': 'NIST Level 1',
                    'public_key_size': '261,120 bytes',
                    'ciphertext_size': '128 bytes',
                    'use_case': 'Conservative security choice'
                },
                'mceliece6688128': {
                    'security_level': 'NIST Level 5',
                    'public_key_size': '1,357,824 bytes',
                    'ciphertext_size': '240 bytes',
                    'use_case': 'Highest security level'
                }
            },
            'advantages': [
                'Oldest and most conservative PQC',
                'Well-studied since 1970s',
                'Fast encapsulation/decapsulation',
                'Small ciphertexts'
            ],
            'considerations': [
                'Extremely large public keys (MB scale)',
                'Not suitable for most constrained environments',
                'Best for specific high-security scenarios'
            ],
            'replaces': ['RSA (encryption)', 'DH', 'ECDH'],
            'status': 'NIST Additional Standard (2024)'
        }
    }
    
    # Hybrid approaches
    HYBRID_APPROACHES = {
        'description': 'Combine classical and post-quantum algorithms',
        'benefits': [
            'Security if either algorithm is broken',
            'Smoother migration path',
            'Backwards compatibility'
        ],
        'examples': [
            'X25519 + ML-KEM-768 for key exchange',
            'ECDSA-P256 + ML-DSA-65 for signatures',
            'RSA-2048 + ML-KEM-768 for hybrid encryption'
        ]
    }
    
    def __init__(self):
        pass
    
    def generate_recommendations(
        self,
        vulnerabilities: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate PQC migration recommendations
        
        Args:
            vulnerabilities: List of analyzed vulnerabilities
            risk_assessment: Overall risk assessment
        
        Returns:
            List of specific recommendations
        """
        recommendations = []
        
        # Sort vulnerabilities by risk score
        sorted_vulns = sorted(
            vulnerabilities,
            key=lambda x: x.get('risk_score', 0),
            reverse=True
        )
        
        # Generate recommendations for each vulnerability
        for vuln in sorted_vulns:
            rec = self._create_recommendation(vuln)
            if rec:
                recommendations.append(rec)
        
        # Add strategic recommendations
        strategic_recs = self._generate_strategic_recommendations(risk_assessment)
        recommendations.extend(strategic_recs)
        
        return recommendations
    
    def _create_recommendation(self, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """Create specific recommendation for a vulnerability"""
        algorithm = vulnerability['algorithm']
        category = vulnerability.get('category', 'unknown')
        risk_level = vulnerability.get('risk_level', 'MEDIUM')
        
        recommendation = {
            'current_algorithm': algorithm,
            'file': vulnerability.get('file', 'N/A'),
            'line': vulnerability.get('line', 0),
            'risk_level': risk_level,
            'priority': self._determine_priority(risk_level)
        }
        
        # Recommend appropriate PQC algorithm
        if algorithm in ['RSA', 'DH']:
            # Key exchange / encryption
            recommendation['recommended_pqc'] = 'ML-KEM-768'
            recommendation['alternative_pqc'] = 'Classic McEliece (for high security)'
            recommendation['rationale'] = (
                f"Replace {algorithm} key exchange/encryption with ML-KEM-768 "
                "(lattice-based KEM, NIST FIPS 203). Provides equivalent to AES-192 security "
                "against quantum attacks with good performance."
            )
            recommendation['pqc_details'] = self.NIST_PQC_STANDARDS['ML-KEM']
            
        elif algorithm in ['ECC', 'ECDH']:
            # ECC key exchange
            recommendation['recommended_pqc'] = 'ML-KEM-768'
            recommendation['alternative_pqc'] = 'Hybrid: X25519 + ML-KEM-768'
            recommendation['rationale'] = (
                f"Replace {algorithm} with ML-KEM-768 or hybrid approach combining "
                "X25519 with ML-KEM-768 for smooth migration and defense-in-depth."
            )
            recommendation['pqc_details'] = self.NIST_PQC_STANDARDS['ML-KEM']
            
        elif algorithm in ['DSA', 'ECDSA']:
            # Digital signatures
            recommendation['recommended_pqc'] = 'ML-DSA-65'
            recommendation['alternative_pqc'] = 'SLH-DSA-128s (conservative) or Hybrid approach'
            recommendation['rationale'] = (
                f"Replace {algorithm} signatures with ML-DSA-65 (lattice-based signatures, "
                "NIST FIPS 204). For maximum conservatism, consider SLH-DSA (hash-based, "
                "NIST FIPS 205) or hybrid approach."
            )
            recommendation['pqc_details'] = self.NIST_PQC_STANDARDS['ML-DSA']
            
        elif algorithm == 'RSA' and category == 'asymmetric':
            # RSA signatures
            recommendation['recommended_pqc'] = 'ML-DSA-65'
            recommendation['alternative_pqc'] = 'SLH-DSA or Hybrid: RSA + ML-DSA'
            recommendation['rationale'] = (
                "Replace RSA signatures with ML-DSA-65 for good performance and security. "
                "Consider hybrid approach (RSA + ML-DSA) during transition."
            )
            recommendation['pqc_details'] = self.NIST_PQC_STANDARDS['ML-DSA']
            
        elif algorithm == 'AES':
            # Symmetric encryption
            key_size = vulnerability.get('key_size')
            if key_size and key_size < 256:
                recommendation['recommended_pqc'] = 'AES-256'
                recommendation['rationale'] = (
                    f"Upgrade from AES-{key_size} to AES-256 to maintain 128-bit security "
                    "against quantum attacks (Grover's algorithm halves effective security). "
                    "AES remains quantum-resistant with appropriate key sizes."
                )
            else:
                recommendation['recommended_pqc'] = 'AES-256 (current)'
                recommendation['rationale'] = (
                    "AES-256 provides adequate quantum resistance (128-bit effective security). "
                    "No immediate action required, but monitor for updates."
                )
            
        elif algorithm in ['SHA-1', 'MD5']:
            # Weak hashes
            recommendation['recommended_pqc'] = 'SHA-256 or SHA-3-256'
            recommendation['rationale'] = (
                f"{algorithm} is cryptographically broken and must be replaced immediately. "
                "Use SHA-256 (minimum) or SHA-3 for quantum resistance."
            )
            
        elif algorithm == 'SHA-2':
            # SHA-2 family
            recommendation['recommended_pqc'] = 'SHA-384 or SHA-512'
            recommendation['rationale'] = (
                "SHA-256 provides only 128-bit security against Grover's algorithm. "
                "Consider upgrading to SHA-384 or SHA-512 for higher security margins."
            )
            
        elif algorithm == 'DES':
            recommendation['recommended_pqc'] = 'AES-256'
            recommendation['rationale'] = (
                "DES is completely broken. Replace immediately with AES-256."
            )
        
        else:
            # Generic recommendation
            recommendation['recommended_pqc'] = 'Consult PQC standards'
            recommendation['rationale'] = (
                f"Review NIST PQC standards for appropriate replacement of {algorithm}."
            )
        
        # Add migration steps
        recommendation['migration_steps'] = self._generate_migration_steps(
            algorithm,
            recommendation.get('recommended_pqc', 'NIST PQC')
        )
        
        return recommendation
    
    def _determine_priority(self, risk_level: str) -> str:
        """Determine migration priority"""
        priority_map = {
            'CRITICAL': 'P0 - IMMEDIATE',
            'HIGH': 'P1 - SHORT TERM (1-2 years)',
            'MEDIUM': 'P2 - MEDIUM TERM (2-5 years)',
            'LOW': 'P3 - LONG TERM (5+ years)',
            'MINIMAL': 'P4 - MONITOR'
        }
        return priority_map.get(risk_level, 'P2')
    
    def _generate_migration_steps(
        self,
        current_algo: str,
        target_pqc: str
    ) -> str:
        """Generate high-level migration steps"""
        if 'ML-KEM' in target_pqc:
            return (
                "1) Evaluate ML-KEM library implementations (e.g., liboqs, BouncyCastle); "
                "2) Implement in test environment; "
                "3) Benchmark performance; "
                "4) Consider hybrid approach for transition; "
                "5) Deploy with monitoring"
            )
        elif 'ML-DSA' in target_pqc:
            return (
                "1) Evaluate ML-DSA implementations; "
                "2) Update signature generation/verification code; "
                "3) Test certificate infrastructure compatibility; "
                "4) Consider hybrid signatures during transition; "
                "5) Roll out gradually"
            )
        elif 'SLH-DSA' in target_pqc:
            return (
                "1) Evaluate hash-based signature libraries; "
                "2) Assess signature size impact on systems; "
                "3) Implement with performance testing; "
                "4) Deploy for high-security scenarios"
            )
        elif 'AES-256' in target_pqc:
            return (
                "1) Update key generation to 256-bit; "
                "2) Verify implementation supports AES-256; "
                "3) Migrate keys and re-encrypt data; "
                "4) Update documentation"
            )
        else:
            return (
                "1) Research NIST-approved PQC standards; "
                "2) Select appropriate algorithm; "
                "3) Pilot implementation; "
                "4) Gradual rollout"
            )
    
    def _generate_strategic_recommendations(
        self,
        risk_assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate strategic, system-wide recommendations"""
        strategic = []
        
        overall_level = risk_assessment.get('overall_level', 'MEDIUM')
        
        if overall_level in ['CRITICAL', 'HIGH']:
            strategic.append({
                'type': 'STRATEGIC',
                'priority': 'P0 - IMMEDIATE',
                'title': 'Establish PQC Migration Task Force',
                'rationale': (
                    "High quantum risk detected. Form cross-functional team to oversee "
                    "organization-wide PQC migration."
                ),
                'recommended_pqc': 'N/A',
                'migration_steps': (
                    "1) Designate PQC migration lead; "
                    "2) Create migration roadmap; "
                    "3) Allocate budget and resources; "
                    "4) Establish testing infrastructure; "
                    "5) Define success metrics"
                )
            })
            
            strategic.append({
                'type': 'STRATEGIC',
                'priority': 'P0 - IMMEDIATE',
                'title': 'Implement Crypto-Agility',
                'rationale': (
                    "Enable rapid algorithm replacement capability for future cryptographic "
                    "transitions."
                ),
                'recommended_pqc': 'Architecture pattern',
                'migration_steps': (
                    "1) Abstract cryptographic operations behind interfaces; "
                    "2) Externalize algorithm selection to configuration; "
                    "3) Implement algorithm negotiation protocols; "
                    "4) Design for hybrid crypto support"
                )
            })
        
        strategic.append({
            'type': 'STRATEGIC',
            'priority': 'P1 - SHORT TERM',
            'title': 'Hybrid Cryptography Adoption',
            'rationale': (
                "Implement hybrid classical-PQC approaches for smooth migration and "
                "defense-in-depth."
            ),
            'recommended_pqc': 'Hybrid approach (see details)',
            'migration_steps': (
                "1) Prioritize systems for hybrid deployment; "
                "2) Implement dual-algorithm support; "
                "3) Test hybrid protocols; "
                "4) Monitor for interoperability issues"
            ),
            'hybrid_details': self.HYBRID_APPROACHES
        })
        
        strategic.append({
            'type': 'STRATEGIC',
            'priority': 'P2 - MEDIUM TERM',
            'title': 'Certificate Infrastructure Update',
            'rationale': (
                "Update PKI to support PQC certificates and hybrid certificate chains."
            ),
            'recommended_pqc': 'ML-DSA-65 + ML-KEM-768',
            'migration_steps': (
                "1) Assess CA compatibility with PQC; "
                "2) Plan certificate format updates; "
                "3) Test certificate chain validation; "
                "4) Coordinate with external CAs"
            )
        })
        
        return strategic
    
    def get_pqc_standards_summary(self) -> Dict[str, Any]:
        """Get summary of NIST PQC standards"""
        return {
            'nist_standards': self.NIST_PQC_STANDARDS,
            'hybrid_approaches': self.HYBRID_APPROACHES,
            'timeline': {
                'nist_standardization': 'FIPS 203, 204, 205 published (2024)',
                'initial_adoption': '2024-2026',
                'widespread_deployment': '2026-2030',
                'mandatory_transition': '2030-2035 (estimated)'
            }
        }