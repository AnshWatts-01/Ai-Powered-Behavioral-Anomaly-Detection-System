import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()
Faker.seed(42)
np.random.seed(42)

NUM_ENTITIES = 150
START_DATE = datetime(2023, 1, 1)

def generate_synthetic_logs():
    print("Generating entity baseline profiles...")
    
    # 1. Generate Base Entities (Users, Service Accounts, Edge Devices)
    entities = []
    for i in range(NUM_ENTITIES):
        e_type = np.random.choice(['user', 'service_account', 'edge_device'], p=[0.7, 0.1, 0.2])
        entities.append({
            'entity_id': f"{e_type[:3]}_{fake.uuid4()[:8]}",
            'entity_type': e_type,
            'home_ip': fake.ipv4(),
            'typical_resource': fake.uri_path(),
            'device_fingerprint': fake.user_agent() if e_type == 'user' else f"FW_v{np.random.randint(1,5)}.0_MAC_{fake.mac_address()}"
        })

    logs = []
    current_time = START_DATE
    
    # 2. Generate Normal Behavior Baseline
    print("Generating normal baseline logs...")
    for _ in range(20000):
        current_time += timedelta(minutes=random.randint(1, 30))
        entity = random.choice(entities)
        
        # Introduce slight noise to normal baseline
        ip = entity['home_ip'] if random.random() > 0.1 else fake.ipv4()
        
        logs.append({
            'entity_id': entity['entity_id'],
            'entity_type': entity['entity_type'],
            'timestamp': current_time,
            'source_ip': ip,
            'resource_accessed': entity['typical_resource'] if random.random() > 0.2 else fake.uri_path(),
            'auth_method': np.random.choice(['password', 'token', 'certificate', 'biometric']),
            'session_duration': abs(np.random.normal(120, 30)),
            'command_sequence': "auth -> read -> exit",
            'device_fingerprint': entity['device_fingerprint'],
            'label': 'normal'
        })

    # 3. Inject Anomalies (The 7 Behaviors)
    print("Injecting complex anomaly patterns...")
    anomaly_time = START_DATE + timedelta(days=5)
    
    for _ in range(500): # Inject 500 total anomalies across types
        a_type = random.choice([
            'brute_force', 'impossible_travel', 'credential_stuffing', 
            'lateral_movement', 'device_spoofing', 'low_and_slow_exfiltration', 'insider_drift'
        ])
        
        entity = random.choice(entities)
        
        if a_type == 'brute_force':
            # Rapid failure from one source
            for i in range(15):
                logs.append({
                    'entity_id': entity['entity_id'], 'entity_type': entity['entity_type'],
                    'timestamp': anomaly_time + timedelta(seconds=i*2),
                    'source_ip': fake.ipv4(), 'resource_accessed': '/login',
                    'auth_method': 'password', 'session_duration': 0,
                    'command_sequence': "auth_failed", 'device_fingerprint': entity['device_fingerprint'],
                    'label': 'brute_force'
                })
                
        elif a_type == 'impossible_travel':
            # Same entity, distant locations (represented by new IP), zero time gap
            logs.append({**logs[-1], 'entity_id': entity['entity_id'], 'timestamp': anomaly_time, 'source_ip': '203.0.113.50', 'label': 'impossible_travel'})
            logs.append({**logs[-1], 'entity_id': entity['entity_id'], 'timestamp': anomaly_time + timedelta(seconds=5), 'source_ip': '198.51.100.12', 'label': 'impossible_travel'})
            
        elif a_type == 'credential_stuffing':
            # Many entities, same IP
            bad_ip = fake.ipv4()
            for _ in range(20):
                victim = random.choice(entities)
                logs.append({
                    'entity_id': victim['entity_id'], 'entity_type': victim['entity_type'],
                    'timestamp': anomaly_time + timedelta(seconds=random.randint(1,60)),
                    'source_ip': bad_ip, 'resource_accessed': '/login',
                    'auth_method': 'password', 'session_duration': 0,
                    'command_sequence': "auth_failed", 'device_fingerprint': fake.user_agent(),
                    'label': 'credential_stuffing'
                })
                
        elif a_type == 'device_spoofing':
            # Valid IP/User, highly mismatched fingerprint
            logs.append({
                'entity_id': entity['entity_id'], 'entity_type': entity['entity_type'],
                'timestamp': anomaly_time, 'source_ip': entity['home_ip'],
                'resource_accessed': entity['typical_resource'], 'auth_method': 'token',
                'session_duration': 100, 'command_sequence': "auth -> execute",
                'device_fingerprint': 'Kali_Linux_v2023_MAC_00:00:00:00:00',
                'label': 'device_spoofing'
            })
            
        else: # Generic mapping for lateral movement, insider drift, low/slow
            logs.append({
                'entity_id': entity['entity_id'], 'entity_type': entity['entity_type'],
                'timestamp': anomaly_time, 'source_ip': fake.ipv4(),
                'resource_accessed': f"/restricted_zone_{random.randint(1,99)}", 
                'auth_method': 'password', 'session_duration': 9999,
                'command_sequence': "auth -> dump_database -> zip -> exfiltrate",
                'device_fingerprint': entity['device_fingerprint'],
                'label': a_type
            })
            
        anomaly_time += timedelta(hours=1)

    df = pd.DataFrame(logs)
    df = df.sort_values('timestamp').reset_index(drop=True)
    df.to_csv('synthetic_access_logs.csv', index=False)
    print(f"✅ Generated dataset with {len(df)} records saved to 'synthetic_access_logs.csv'.")
    print(df['label'].value_counts())

if __name__ == "__main__":
    generate_synthetic_logs()