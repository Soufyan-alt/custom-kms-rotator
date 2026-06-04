# 🔑 Automated KMS Key Lifecycle & Zero-Downtime Rotation Engine
### Enterprise Cryptographic Agility & Dynamic Rewrapping Pipeline

[![Cryptographic Engine](https://img.shields.io/badge/Engine-HashiCorp%20Vault%20Transit-000000?style=for-the-badge&logo=hashicorp&logoColor=FF3E00)](https://www.vaultproject.io/)
[![Compliance Framework](https://img.shields.io/badge/Compliance-PCI--DSS%20%2F%20SOC2-0052CC?style=for-the-badge)]()

A production-grade cryptographic management framework demonstrating automated **Key Lifecycle Management** and zero-downtime key rotation using HashiCorp Vault's Transit Secrets Engine. This engine enforces strict enterprise compliance standards by programmatically rotating encryption keys every 30 days and upgrading legacy database ciphertexts using non-disruptive cryptographic rewrapping.

---

## 🛠️ Cryptographic Engineering Stack

The core enterprise-grade technologies managing the data plane protection layer:

### 🔑 Centralized Cryptographic Engine
| Component | Technology | Cryptographic Responsibility |
| :--- | :--- | :--- |
| **KMS Core** | ![HashiCorp Vault](https://img.shields.io/badge/HashiCorp_Vault-000000?style=flat-square&logo=hashicorp&logoColor=FF3E00) | Manages centralized root keys, handles convergent encryption, and executes data-at-rest rewrapping. |

### ⚙️ Automation & Pipeline Interceptors
* ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) **Python 3 / Hvac Client:** Intercepts cron-based or event-driven lifecycle triggers, orchestrates batched dataset evaluations, and executes bulk api requests against the KMS cluster.

---

## 📊 The Cryptographic Re-Keying Architecture (Zero-Downtime Rewrap)

### 🔄 Scenario A: Continuous Data Ingestion & Key Proliferation
Data is systematically ingested by the application layer, enveloped inside the current active cryptographic version (`v1`), and directly pushed into the storage layer.

```mermaid
sequenceDiagram
    autonumber
    participant App as 🖥️ Application Core
    participant Vault as 🔑 Vault Transit Engine
    participant DB as 🗄️ Database Storage

    App->>App: Receive Plaintext Payload
    App->>Vault: Encrypt Request (Payload, Key: `customer-data`)
    Note over Vault: Uses Active Key Version v1<br/>Ciphertext prepended with 'vault:v1:'
    Vault-->>App: Return Ciphertext (`vault:v1:exg2...`)
    App->>DB: INSERT Record into Database
    Note over DB: Data is heavily protected at rest
