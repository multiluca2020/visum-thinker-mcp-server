"""
Verify the last two operations created
"""
import sys
sys.path.append(r'C:\Users\lrosa\AppData\Local\Programs\Python\Python311\Lib\site-packages')

import win32com.client

# Connect to running Visum instance
visum = win32com.client.Dispatch("Visum.Visum.250")

# Check operations 578 and 579
print("\n🔍 Verifica delle ultime operazioni create:\n")

try:
    op578 = visum.Procedures.Operations.ItemByKey(578)
    type578 = op578.AttValue("OPERATIONTYPE")
    print(f"Position 578: OPERATIONTYPE = {type578}")
    
    if type578 == 9:
        print("  ✅ CORRETTO: Initialize Assignment (Delete)")
    else:
        print(f"  ❌ ERRORE: Dovrebbe essere 9, invece è {type578}")
except Exception as e:
    print(f"Position 578: Errore - {e}")

try:
    op579 = visum.Procedures.Operations.ItemByKey(579)
    type579 = op579.AttValue("OPERATIONTYPE")
    print(f"\nPosition 579: OPERATIONTYPE = {type579}")
    
    if type579 == 101:
        print("  ✅ CORRETTO: PrT Assignment")
    else:
        print(f"  ❌ ERRORE: Dovrebbe essere 101, invece è {type579}")
except Exception as e:
    print(f"Position 579: Errore - {e}")

print("\n" + "="*50)
