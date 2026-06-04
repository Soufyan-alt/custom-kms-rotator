# 🛡️ SECURITY.md - Cryptographic Threat Modeling & KMS Remediation Log

This security document outlines the technical risks associated with encryption key stagnation, the automated mechanisms used to track key degradation, and the programmatic self-remediation architecture deployed to handle key lifecycle automation without causing database service disruption.

---

## 🛑 1. The Cryptographic Risk: Key Stagnation & Exposure (ما هي الثغرة أو المشكلة الأمنية؟)

### The Architectural Problem
When applications encrypt sensitive corporate payloads (such as credit cards, PII, or access credentials) using a static encryption key, they create a high-value attack surface. If an adversary compromises the infrastructure or extracts a database backup, having a single static key means all historical, current, and future data is permanently compromised. 

### The Regulatory & Practical Impact
Leaving encryption keys unchanged for extended periods violates major compliance frameworks like PCI-DSS, HIPAA, and SOC2. Furthermore, if a key is compromised, there is typically no safe or automated way to migrate terabytes of existing database ciphertexts to a new key without taking the entire application platform offline.

---

## 🔍 2. Automated Detection: Key Lifecycle Auditing (كيف تم اكتشافها آلياً؟)

To guarantee that encryption keys do not exceed their maximum safe operational lifespan, the architecture utilizes automated temporal tracking and cryptographic event monitoring:

1. **Time-Based Lifecycle Triggers**: An automated orchestrator checks the metadata of active keys. If a key version's age reaches the defined 30-day boundary, a lifecycle policy violation event is triggered programmatically.
2. **Cryptographic Metadata Auditing**: The system queries HashiCorp Vault’s backend API to monitor key usage limits and version parameters. If a legacy version (`v1`) is found handling new encryption write requests, an alert is dispatched indicating a compliance skew.
3. **Audit Trail Logging**: Every operational encryption and decryption request produces detailed audit logs, allowing security teams to continuously track which data fields are still bound to older, high-risk key versions.

---

## 🛠️ 3. Root Remediation: Zero-Downtime Rotation & Rewrapping (كيف تم إصلاحها؟)

The risk of key compromise was eliminated by implementing an automated **Key Lifecycle Management** pipeline designed to enforce rotation with zero service disruption:

### Phase A: Programmatic Key Rotation
The pipeline invokes HashiCorp Vault's Transit Engine API to rotate the master key. This action generates a brand-new cryptographic key version (`v2`) inside Vault's secure memory space. From this millisecond onward, all new incoming database writes are automatically encrypted using the `v2` key.

### Phase B: Non-Disruptive Data Rewrapping (The Rewrap Operation)
To secure historical data without service downtime, the engine pulls legacy ciphertexts (prefixed with `vault:v1:`) and submits them to Vault's specialized `/rewrap` endpoint. 
* Vault decrypts the ciphertext using `v1` and immediately re-encrypts it using `v2` **strictly within its internal memory space**.
* The raw plaintext is never exposed to the application or network layers during this operation.
* The database updates its records to the new format (prefixed with `vault:v2:`) seamlessly while users continue interacting with the platform.

### Phase C: Controlled Key Deprecation
Once the rewrapping pipeline confirms that 100% of the historical database records have been successfully migrated to `vault:v2:`, the `v1` key is safely disabled for encryption and preserved strictly in a read-only state for emergency recovery, completely shrinking the attack window.

---
**🔒 Cryptographic Compliance Notice:** Key rotations and rewrap cycles run as decoupled background workers. All encryption operations strictly follow AES-256-GCM standards.
