import os
import base64
import requests

# إعدادات الاتصال بـ HashiCorp Vault
VAULT_URL = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "root")
KEY_NAME = "customer-data-key"

headers = {
    "X-Vault-Token": VAULT_TOKEN,
    "Content-Type": "application/json"
}

def init_transit_engine():
    """تفعيل محرك Transit وإنشاء مفتاح التشفير الرئيسي بأمان"""
    print("⚙️ Initializing Vault Transit Secrets Engine...")
    
    # تفعيل المحرك (وتجاهل الخطأ إذا كان مفعلاً مسبقاً)
    mount_url = f"{VAULT_URL}/v1/sys/mounts/transit"
    mount_res = requests.post(mount_url, headers=headers, json={"type": "transit"})
    if mount_res.status_code == 400 and "path is already mounted" in mount_res.text:
        print("ℹ️ Transit Secrets Engine is already enabled.")
    
    # إنشاء مفتاح التشفير
    url = f"{VAULT_URL}/v1/transit/keys/{KEY_NAME}"
    response = requests.post(url, headers=headers, json={"type": "aes256-gcm96"})
    if response.status_code in [200, 204]:
        print(f"✅ Key '{KEY_NAME}' initialized successfully.")

def encrypt_data(plain_text):
    """تشفير البيانات الحساسة عبر Vault"""
    url = f"{VAULT_URL}/v1/transit/encrypt/{KEY_NAME}"
    base64_text = base64.b64encode(plain_text.encode('utf-8')).decode('utf-8')
    
    response = requests.post(url, headers=headers, json={"plaintext": base64_text})
    response.raise_for_status()  # التأكد من عدم وجود أخطاء في الطلب
    
    cipher_text = response.json()['data']['ciphertext']
    return cipher_text

def rotate_encryption_key():
    """🤖 أتمتة تدوير المفتاح: إنشاء إصدار جديد تماماً من المفتاح تلقائياً"""
    print(f"\n🔄 Triggering Automated Key Rotation for '{KEY_NAME}' (Simulating 30-Day Policy)...")
    url = f"{VAULT_URL}/v1/transit/keys/{KEY_NAME}/rotate"
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    
    if response.status_code in [200, 204]:
        print("✅ Key rotated successfully! A new key version has been generated.")

def rewrap_data(old_cipher_text):
    """🛠️ عملية الـ Rewrap: إعادة تشفير البيانات القديمة بالمفتاح الجديد دون فكها في التطبيق"""
    print("⚡ Executing Rewrap operation on legacy database records...")
    url = f"{VAULT_URL}/v1/transit/rewrap/{KEY_NAME}"
    response = requests.post(url, headers=headers, json={"ciphertext": old_cipher_text})
    response.raise_for_status()
    
    new_cipher_text = response.json()['data']['ciphertext']
    return new_cipher_text

if __name__ == "__main__":
    try:
        # 1. تهيئة النظام
        init_transit_engine()
        
        # 2. محاكاة تخزين بيانات مشفرة بالمفتاح القديم (Version 1)
        secret_payload = "Super-Sensitive-Bank-Card-1234-5678"
        print(f"\n📥 Original Data to protect: {secret_payload}")
        
        v1_ciphertext = encrypt_data(secret_payload)
        print(f"🔒 Encrypted Data in DB (v1): {v1_ciphertext}")
        
        # 3. تدوير المفتاح تلقائياً
        rotate_encryption_key()
        
        # 4. ترقية التشفير للبيانات المخزنة دون انقطاع الخدمة
        v2_ciphertext = rewrap_data(v1_ciphertext)
        print(f"🚀 Upgraded Data in DB (v2): {v2_ciphertext}")
        
        print("\n💎 Key Lifecycle Management executed perfectly with Zero-Downtime!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to Vault. Is Vault server running on http://127.0.0.1:8200 ?")
    except Exception as e:
        print(f"\n❌ Unexpected Error occurred: {e}")
