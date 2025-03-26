import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from common.config_loader import load_config

import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

config = load_config()
log_file_path = config['log']['file_path']
openai_api_key = config['ai']['openai_api_key']

class EncDecUtil:
    def __init__(self, secret_key: str):
        """Initialize with a secret key (hashed for consistent AES key size)."""
        self.key = hashlib.sha256(secret_key.encode()).digest()  # 256-bit key

    def encrypt(self, plain_text: str) -> str:
        """Encrypts a string, ensures IV is stored for cross-machine decryption."""
        cipher = AES.new(self.key, AES.MODE_CBC)  # CBC mode for encryption
        iv = cipher.iv  # Initialization Vector (IV) for AES
        encrypted_bytes = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
        return base64.b64encode(iv + encrypted_bytes).decode()  # Encode as Base64

    def decrypt(self, encrypted_base64_text: str) -> str:
        """Decrypts a Base64 encoded encrypted string back to original, ensuring correct IV handling."""
        encrypted_data = base64.b64decode(encrypted_base64_text)
        iv = encrypted_data[:16]  # Extract IV (first 16 bytes)
        encrypted_bytes = encrypted_data[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(encrypted_bytes), AES.block_size).decode()

    #
    # def encrypt_file(self, file_path: str, output_path: str):
    #     """Reads a file, encrypts its content, and saves as a .enc file, ensuring IV is included."""
    #     with open(file_path, "r", encoding="utf-8") as file:
    #         content = file.read()
    #     encrypted_content = self.encrypt(content)
    #     with open(output_path, "w", encoding="utf-8") as enc_file:
    #         enc_file.write(encrypted_content)
    #
    # def decrypt_file(self, encrypted_file_path: str, output_path: str):
    #     """Reads an encrypted .enc file, decrypts its content, and saves as a .txt file, ensuring IV is correctly handled."""
    #     with open(encrypted_file_path, "r", encoding="utf-8") as enc_file:
    #         encrypted_content = enc_file.read()
    #     decrypted_content = self.decrypt(encrypted_content)
    #     with open(output_path, "w", encoding="utf-8") as file:
    #         file.write(decrypted_content)


# Example Usage
if __name__ == "__main__":

    # parser = argparse.ArgumentParser(description="AI-based Test Case Evaluation")
    # parser.add_argument("--secret", required=True, help="Secret key for SecureEncryptor")
    # args = parser.parse_args()

    secret = os.getenv("enc.secret")
    secure = EncDecUtil(secret)

    # Access variables
    # secret = os.getenv("enc.secret")
    # TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

    # # Encrypt and decrypt a string
    # original_text = "Hello, Secure World!"
    # encrypted_text = secure.encrypt(original_text)
    # print(f"Encrypted (Base64): {encrypted_text}")  # Output: Encrypted Base64 text

    decrypted_text = secure.decrypt(openai_api_key)
    print(f"Decrypted: {decrypted_text}")  # Output: Hello, Secure World!

    # Compare Original and Decrypted Text
    # if original_text == decrypted_text:
    #     print("✅ The decrypted text matches the original!")
    # else:
    #     print("❌ Mismatch detected! Decryption may have failed.")

    # # Encrypt and decrypt a file
    # input_file = "sample.txt"  # Create a sample file before running
    # encrypted_file = "sample.enc"
    # decrypted_file = "sample_decrypted.txt"
    #
    # secure.encrypt_file(input_file, encrypted_file)
    # print(f"File encrypted: {encrypted_file}")
    #
    # secure.decrypt_file(encrypted_file, decrypted_file)
    # print(f"File decrypted: {decrypted_file}")
    #
    # # Compare Original and Decrypted File Content
    # with open(input_file, "r", encoding="utf-8") as f1, open(decrypted_file, "r", encoding="utf-8") as f2:
    #     original_content = f1.read()
    #     decrypted_content = f2.read()
    #     if original_content == decrypted_content:
    #         print("✅ The decrypted file matches the original!")
    #     else:
    #         print("❌ Mismatch detected! Decryption may have failed.")
