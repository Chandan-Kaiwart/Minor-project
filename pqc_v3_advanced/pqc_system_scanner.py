"""
PQC V3.1 - SYSTEM SCANNER
Handles multi-file, folder, and zip scanning for PQC vulnerabilities.
"""
import os
import zipfile
import shutil
from typing import List, Dict, Any

class SystemPQCScanner:
    def __init__(self, detector, vuln_analyzer):
        self.detector = detector
        self.vuln_analyzer = vuln_analyzer

    def scan_file(self, file_path: str) -> List[Dict]:
        """Scans a single file for PQC vulnerabilities"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            findings = self.detector.detect_crypto({
                'path': file_path,
                'name': os.path.basename(file_path),
                'content': content
            })
            
            vulns = []
            for f in findings:
                v = self.vuln_analyzer.analyze_vulnerability(f)
                if v: vulns.append(v)
            return vulns
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
            return []

    def scan_folder(self, folder_path: str) -> Dict:
        """Recursively scans a folder for files"""
        total_vulns = []
        files_scanned = 0
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(('.py', '.js', '.c', '.cpp', '.java', '.go', '.ts', '.sh')):
                    file_path = os.path.join(root, file)
                    vulns = self.scan_file(file_path)
                    total_vulns.extend(vulns)
                    files_scanned = files_scanned + 1
        
        return {
            'files_scanned': files_scanned,
            'vulnerabilities': total_vulns,
            'findings': total_vulns # Map to same for consistency
        }

    def scan_zip(self, zip_path: str, temp_extract_dir: str = "temp_pqc_scan") -> Dict:
        """Extracts and scans a zip file"""
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)
        os.makedirs(temp_extract_dir)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_dir)
            
            report = self.scan_folder(temp_extract_dir)
            return report
        finally:
            shutil.rmtree(temp_extract_dir)

if __name__ == "__main__":
    # Test stub
    pass
