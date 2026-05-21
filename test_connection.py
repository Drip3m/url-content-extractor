"""
Quick test — register agent on Nevermined using the dashboard approach.
This script just tests the connection.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from payments_py import Payments, PaymentOptions

payments = Payments.get_instance(
    PaymentOptions(
        nvm_api_key=os.getenv("NVM_API_KEY"),
        environment="live",
    )
)

# Test: list existing agents
agents = payments.agents.list()
print(f"Connected! Found {len(agents)} existing agent(s).")
for a in agents:
    print(f"  - {a.get('name', 'Unnamed')}: {a.get('id', a.get('did', 'no id'))}")
